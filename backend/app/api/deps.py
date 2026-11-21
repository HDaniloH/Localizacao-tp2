"""Dependências do FastAPI: sessão do banco e controle de acesso."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decodificar_token
from app.database import get_db
from app.models import Usuario

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

DbSession = Annotated[Session, Depends(get_db)]


def get_usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)], db: DbSession
) -> Usuario:
    """Resolve o usuário autenticado a partir do token Bearer.

    Raises:
        HTTPException: 401 se o token for inválido ou o usuário não existir
            ou estiver inativo.
    """
    nao_autorizado = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    sujeito = decodificar_token(token)
    if sujeito is None or not sujeito.isdigit():
        raise nao_autorizado
    usuario = db.get(Usuario, int(sujeito))
    if usuario is None or not usuario.ativo:
        raise nao_autorizado
    return usuario


UsuarioAtual = Annotated[Usuario, Depends(get_usuario_atual)]


def exigir_admin(usuario: UsuarioAtual) -> Usuario:
    """Só deixa passar administradores.

    Raises:
        HTTPException: 403 se o usuário autenticado não for admin.
    """
    if not usuario.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito",
        )
    return usuario


AdminAtual = Annotated[Usuario, Depends(exigir_admin)]
