"""Rotas de autenticação: cadastro público, login e usuário logado."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import DbSession, UsuarioAtual
from app.core.security import criar_token_acesso
from app.models import Usuario
from app.schemas.usuario import Token, UsuarioCriar, UsuarioPublico
from app.services import usuario_service

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/registrar",
    response_model=UsuarioPublico,
    status_code=status.HTTP_201_CREATED,
)
def registrar(dados: UsuarioCriar, db: DbSession) -> Usuario:
    """Cadastro público. Nunca cria administrador."""
    return usuario_service.criar(db, dados)


@router.post("/login", response_model=Token)
def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession
) -> Token:
    """Troca e-mail (campo ``username``) e senha por um token JWT.

    Usa o formato OAuth2 para que o botão "Authorize" do Swagger funcione.
    """
    try:
        usuario = usuario_service.autenticar(db, form.username, form.password)
    except usuario_service.CredenciaisInvalidas:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except usuario_service.UsuarioInativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta inativa",
        ) from None
    return Token(access_token=criar_token_acesso(str(usuario.id)))


@router.get("/me", response_model=UsuarioPublico)
def me(usuario: UsuarioAtual) -> Usuario:
    """Dados do usuário dono do token."""
    return usuario
