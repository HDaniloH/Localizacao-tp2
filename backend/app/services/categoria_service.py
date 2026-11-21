"""Regras de negócio de categorias de ocorrência (US05)."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import Conflito, RecursoNaoEncontrado
from app.models import Categoria
from app.schemas.categoria import CategoriaAtualizar, CategoriaCriar


def _garantir_nome_livre(db: Session, nome: str, ignorar_id: int | None = None) -> None:
    """Impede duas categorias com o mesmo nome (sem diferenciar maiúsculas).

    Categorias inativas também contam, para não haver duplicata ao reativar.

    Raises:
        Conflito: Se já existir outra categoria com esse nome.
    """
    consulta = select(Categoria).where(
        func.lower(Categoria.nome) == nome.strip().lower()
    )
    existente = db.scalars(consulta).first()
    if existente is not None and existente.id != ignorar_id:
        raise Conflito("Já existe uma categoria com esse nome")


def listar(db: Session, ativa: bool | None = None) -> list[Categoria]:
    """Lista categorias em ordem alfabética.

    Args:
        db: Sessão do banco.
        ativa: ``True``/``False`` para filtrar; ``None`` para todas.
    """
    consulta = select(Categoria).order_by(Categoria.nome)
    if ativa is not None:
        consulta = consulta.where(Categoria.ativa == ativa)
    return list(db.scalars(consulta))


def obter(db: Session, categoria_id: int, somente_ativa: bool = False) -> Categoria:
    """Obtém uma categoria pelo id.

    Args:
        db: Sessão do banco.
        categoria_id: Id procurado.
        somente_ativa: Se ``True``, trata categoria inativa como inexistente
            (usado nas rotas públicas).

    Raises:
        RecursoNaoEncontrado: Se não existir (ou estiver inativa, quando
            ``somente_ativa``).
    """
    categoria = db.get(Categoria, categoria_id)
    if categoria is None or (somente_ativa and not categoria.ativa):
        raise RecursoNaoEncontrado("Categoria não encontrada")
    return categoria


def criar(db: Session, dados: CategoriaCriar) -> Categoria:
    """Cadastra uma categoria ativa.

    Raises:
        Conflito: Se o nome já estiver em uso.
    """
    _garantir_nome_livre(db, dados.nome)
    categoria = Categoria(nome=dados.nome, descricao=dados.descricao)
    db.add(categoria)
    db.commit()
    db.refresh(categoria)
    return categoria


def atualizar(db: Session, categoria_id: int, dados: CategoriaAtualizar) -> Categoria:
    """Altera nome e/ou descrição de uma categoria.

    Raises:
        RecursoNaoEncontrado: Se a categoria não existir.
        Conflito: Se o novo nome pertencer a outra categoria.
    """
    categoria = obter(db, categoria_id)
    campos = dados.model_dump(exclude_unset=True)
    if campos.get("nome") is not None:
        _garantir_nome_livre(db, campos["nome"], ignorar_id=categoria.id)
        categoria.nome = campos["nome"]
    if "descricao" in campos:
        categoria.descricao = campos["descricao"]
    db.commit()
    db.refresh(categoria)
    return categoria


def definir_situacao(db: Session, categoria_id: int, ativa: bool) -> Categoria:
    """Ativa ou inativa uma categoria (operação idempotente).

    Raises:
        RecursoNaoEncontrado: Se a categoria não existir.
    """
    categoria = obter(db, categoria_id)
    categoria.ativa = ativa
    db.commit()
    db.refresh(categoria)
    return categoria
