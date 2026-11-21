"""Fixtures compartilhadas pelos testes da API.

Os testes usam o mesmo PostgreSQL/PostGIS do grupo (``DATABASE_URL``; local:
``docker compose up -d``). Cada teste recria as tabelas, então nenhum teste
depende do estado deixado por outro.
"""

import os
from collections.abc import Callable, Generator

# Precisa vir antes dos imports de ``app`` (as configurações são lidas no
# import). bcrypt com custo 4 deixa a suíte rápida.
os.environ.setdefault("BCRYPT_ROUNDS", "4")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from sqlalchemy.orm import Session  # noqa: E402

from app.core.security import criar_token_acesso, gerar_hash_senha  # noqa: E402
from app.database import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Categoria, Usuario  # noqa: E402

SENHA_PADRAO = "Senha123"


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Sessão ligada a tabelas recém-criadas no PostGIS."""
    Base.metadata.create_all(bind=engine)
    sessao = SessionLocal()
    try:
        yield sessao
    finally:
        sessao.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Cliente HTTP da API usando a sessão do teste."""
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def criar_usuario(db_session: Session) -> Callable[..., Usuario]:
    """Fábrica de usuários gravados direto no banco."""
    contador = {"n": 0}

    def _criar(
        email: str | None = None,
        is_admin: bool = False,
        ativo: bool = True,
        senha: str = SENHA_PADRAO,
        nome: str = "Fulano de Tal",
    ) -> Usuario:
        contador["n"] += 1
        usuario = Usuario(
            nome=nome,
            email=email or f"usuario{contador['n']}@aluno.unb.br",
            senha_hash=gerar_hash_senha(senha),
            is_admin=is_admin,
            ativo=ativo,
        )
        db_session.add(usuario)
        db_session.commit()
        db_session.refresh(usuario)
        return usuario

    return _criar


@pytest.fixture
def criar_categoria(db_session: Session) -> Callable[..., Categoria]:
    """Fábrica de categorias gravadas direto no banco."""

    def _criar(
        nome: str, descricao: str | None = None, ativa: bool = True
    ) -> Categoria:
        categoria = Categoria(nome=nome, descricao=descricao, ativa=ativa)
        db_session.add(categoria)
        db_session.commit()
        db_session.refresh(categoria)
        return categoria

    return _criar


def headers_de(usuario: Usuario) -> dict[str, str]:
    """Cabeçalho Authorization com um token válido para o usuário."""
    return {"Authorization": f"Bearer {criar_token_acesso(str(usuario.id))}"}


@pytest.fixture
def cidadao(criar_usuario: Callable[..., Usuario]) -> Usuario:
    """Usuário comum ativo."""
    return criar_usuario(email="cidadao@aluno.unb.br")


@pytest.fixture
def admin(criar_usuario: Callable[..., Usuario]) -> Usuario:
    """Administrador ativo."""
    return criar_usuario(email="admin@unb.br", is_admin=True)


@pytest.fixture
def headers_cidadao(cidadao: Usuario) -> dict[str, str]:
    """Cabeçalho autenticado como cidadão."""
    return headers_de(cidadao)


@pytest.fixture
def headers_admin(admin: Usuario) -> dict[str, str]:
    """Cabeçalho autenticado como administrador."""
    return headers_de(admin)
