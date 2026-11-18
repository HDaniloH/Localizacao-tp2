"""Regras de negócio de usuários e autenticação."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito
from app.core.security import gerar_hash_senha, verificar_senha
from app.models import Usuario
from app.schemas.usuario import UsuarioCriar

# Hash usado quando o e-mail não existe, para que o tempo de resposta do
# login seja parecido nos dois casos (evita descobrir e-mails cadastrados).
_HASH_FICTICIO = gerar_hash_senha("senha-ficticia-0")


class CredenciaisInvalidas(Exception):
    """E-mail ou senha incorretos."""


class UsuarioInativo(Exception):
    """A conta existe, mas foi inativada."""


def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    """Busca um usuário pelo e-mail, sem diferenciar maiúsculas.

    Args:
        db: Sessão do banco.
        email: E-mail procurado.

    Returns:
        O usuário, ou ``None`` se não existir.
    """
    consulta = select(Usuario).where(
        func.lower(Usuario.email) == _normalizar_email(email)
    )
    return db.scalars(consulta).first()


def _garantir_email_livre(
    db: Session, email: str, ignorar_id: int | None = None
) -> None:
    existente = buscar_por_email(db, email)
    if existente is not None and existente.id != ignorar_id:
        raise Conflito("E-mail já cadastrado")


def criar(db: Session, dados: UsuarioCriar, is_admin: bool = False) -> Usuario:
    """Cadastra um novo usuário.

    Args:
        db: Sessão do banco.
        dados: Nome, e-mail e senha validados.
        is_admin: Se o novo usuário é administrador (só admins escolhem).

    Raises:
        Conflito: Se o e-mail já estiver em uso.
    """
    _garantir_email_livre(db, dados.email)
    usuario = Usuario(
        nome=dados.nome,
        email=_normalizar_email(dados.email),
        senha_hash=gerar_hash_senha(dados.senha),
        is_admin=is_admin,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    """Valida as credenciais de login.

    Raises:
        CredenciaisInvalidas: Se o e-mail não existir ou a senha não conferir.
        UsuarioInativo: Se a senha conferir, mas a conta estiver inativa.
    """
    usuario = buscar_por_email(db, email)
    if usuario is None:
        verificar_senha(senha, _HASH_FICTICIO)
        raise CredenciaisInvalidas()
    if not verificar_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidas()
    if not usuario.ativo:
        raise UsuarioInativo()
    return usuario
