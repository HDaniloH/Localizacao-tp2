"""Rotas do CRUD de usuários."""

from fastapi import APIRouter, Response, status

from app.api.deps import AdminAtual, DbSession, UsuarioAtual
from app.core.exceptions import OperacaoNaoPermitida
from app.models import Usuario
from app.schemas.usuario import (
    UsuarioAtualizarAdmin,
    UsuarioCriarAdmin,
    UsuarioPublico,
)
from app.services import usuario_service

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("", response_model=list[UsuarioPublico])
def listar(
    db: DbSession, _admin: AdminAtual, ativo: bool | None = None
) -> list[Usuario]:
    """Lista usuários (somente admin). Filtro opcional ``?ativo=``."""
    return usuario_service.listar(db, ativo)


@router.post("", response_model=UsuarioPublico, status_code=status.HTTP_201_CREATED)
def criar(dados: UsuarioCriarAdmin, db: DbSession, _admin: AdminAtual) -> Usuario:
    """Admin cadastra usuário, podendo criar outro admin."""
    return usuario_service.criar(db, dados, is_admin=dados.is_admin)


@router.get("/{usuario_id}", response_model=UsuarioPublico)
def obter(usuario_id: int, db: DbSession, atual: UsuarioAtual) -> Usuario:
    """Consulta um usuário (o próprio, ou qualquer um se for admin)."""
    if not atual.is_admin and atual.id != usuario_id:
        raise OperacaoNaoPermitida("Sem permissão para ver este usuário")
    return usuario_service.obter(db, usuario_id)


@router.patch("/{usuario_id}", response_model=UsuarioPublico)
def atualizar(
    usuario_id: int,
    dados: UsuarioAtualizarAdmin,
    db: DbSession,
    atual: UsuarioAtual,
) -> Usuario:
    """Altera um usuário. ``is_admin`` e ``ativo`` só podem ser mudados por admin."""
    return usuario_service.atualizar(db, usuario_id, dados, atual)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def inativar(usuario_id: int, db: DbSession, admin: AdminAtual) -> Response:
    """Inativa um usuário (exclusão lógica; somente admin)."""
    usuario_service.inativar(db, usuario_id, admin)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
