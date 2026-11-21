"""Rotas de categorias (US05 — Painel Administrativo).

* ``/admin/categorias``: gestão completa, restrita a administradores.
* ``/categorias``: consulta pública das categorias ativas, usada pelo
  formulário de registro de ocorrência (US01) e pelos filtros do mapa (US02).
"""

from fastapi import APIRouter

from app.api.deps import AdminAtual, DbSession
from app.models import Categoria
from app.schemas.categoria import (
    CategoriaAtualizar,
    CategoriaCriar,
    CategoriaPublica,
)
from app.services import categoria_service

router_admin = APIRouter(prefix="/admin/categorias", tags=["Admin — Categorias (US05)"])
router_publico = APIRouter(prefix="/categorias", tags=["Categorias"])


# ---------- Admin ----------


@router_admin.get("", response_model=list[CategoriaPublica])
def listar_admin(
    db: DbSession, _admin: AdminAtual, ativa: bool | None = None
) -> list[Categoria]:
    """Lista todas as categorias. Filtro opcional ``?ativa=``."""
    return categoria_service.listar(db, ativa)


@router_admin.post("", response_model=CategoriaPublica, status_code=201)
def criar(dados: CategoriaCriar, db: DbSession, _admin: AdminAtual) -> Categoria:
    """Cadastra uma nova categoria (já nasce ativa)."""
    return categoria_service.criar(db, dados)


@router_admin.get("/{categoria_id}", response_model=CategoriaPublica)
def obter_admin(categoria_id: int, db: DbSession, _admin: AdminAtual) -> Categoria:
    """Consulta uma categoria, ativa ou inativa."""
    return categoria_service.obter(db, categoria_id)


@router_admin.patch("/{categoria_id}", response_model=CategoriaPublica)
def atualizar(
    categoria_id: int,
    dados: CategoriaAtualizar,
    db: DbSession,
    _admin: AdminAtual,
) -> Categoria:
    """Altera nome e/ou descrição."""
    return categoria_service.atualizar(db, categoria_id, dados)


@router_admin.patch("/{categoria_id}/inativar", response_model=CategoriaPublica)
def inativar(categoria_id: int, db: DbSession, _admin: AdminAtual) -> Categoria:
    """Inativa a categoria: some das listas públicas, mas não é apagada."""
    return categoria_service.definir_situacao(db, categoria_id, ativa=False)


@router_admin.patch("/{categoria_id}/reativar", response_model=CategoriaPublica)
def reativar(categoria_id: int, db: DbSession, _admin: AdminAtual) -> Categoria:
    """Reativa uma categoria inativa."""
    return categoria_service.definir_situacao(db, categoria_id, ativa=True)


# ---------- Público ----------


@router_publico.get("", response_model=list[CategoriaPublica])
def listar_ativas(db: DbSession) -> list[Categoria]:
    """Lista as categorias ativas."""
    return categoria_service.listar(db, ativa=True)


@router_publico.get("/{categoria_id}", response_model=CategoriaPublica)
def obter_ativa(categoria_id: int, db: DbSession) -> Categoria:
    """Consulta uma categoria ativa."""
    return categoria_service.obter(db, categoria_id, somente_ativa=True)
