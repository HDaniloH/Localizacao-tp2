"""Cria o primeiro administrador do sistema.

Uso::

    python -m app.criar_admin "Nome do Admin" admin@unb.br SenhaForte123
"""

import sys

from sqlalchemy.orm import Session

from app.database import Base, SessionLocal, engine
from app.models import Usuario
from app.schemas.usuario import UsuarioCriar
from app.services import usuario_service


def criar_admin_inicial(db: Session, nome: str, email: str, senha: str) -> Usuario:
    """Cadastra um administrador validando os dados como no cadastro normal.

    Raises:
        pydantic.ValidationError: Se nome, e-mail ou senha forem inválidos.
        app.core.exceptions.Conflito: Se o e-mail já existir.
    """
    dados = UsuarioCriar(nome=nome, email=email, senha=senha)
    return usuario_service.criar(db, dados, is_admin=True)


def main(argv: list[str]) -> int:
    """Executa o comando de linha de comando."""
    if len(argv) != 3:
        print(__doc__)
        return 1
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        admin = criar_admin_inicial(db, *argv)
    print(f"Administrador criado: id={admin.id} email={admin.email}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main(sys.argv[1:]))
