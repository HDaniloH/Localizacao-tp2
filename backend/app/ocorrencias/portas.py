"""Interfaces de que o serviço depende.

As implementações reais estão em ``repositorio_sql``; os testes de unidade
usam doubles. Assim o serviço não conhece SQLAlchemy nem FastAPI.
"""

import enum
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional, Protocol

from app.ocorrencias.geo import Ponto
from app.ocorrencias.schemas import NovaOcorrencia, Ocorrencia


class SituacaoCategoria(enum.Enum):
    """Resultado da consulta ao catálogo de categorias (US05)."""

    ATIVA = "ativa"
    INATIVA = "inativa"
    INEXISTENTE = "inexistente"


class CatalogoCategorias(Protocol):
    """Informa se uma categoria pode receber novos registros."""

    def situacao(self, categoria_id: int) -> SituacaoCategoria:
        """Informa se a categoria existe e está ativa."""


class PoliticaArea(Protocol):
    """Informa se um ponto está numa área atendida (US05)."""

    def ponto_autorizado(self, ponto: Ponto) -> bool:
        """Indica se é permitido registrar ocorrência no ponto."""


@dataclass(frozen=True)
class Pagina:
    """Página de resultados em ordem determinística.

    Attributes:
        itens: Ocorrências da página.
        proximo_offset: Offset da próxima página, ou ``None`` se acabou.
    """

    itens: list[Ocorrencia]
    proximo_offset: Optional[int]


class RepositorioOcorrencias(Protocol):
    """Persistência das ocorrências.

    ``listar`` ordena por ``criado_em`` decrescente e, em empate, por ``id``
    decrescente.
    """

    def adicionar(self, nova: NovaOcorrencia) -> Ocorrencia:
        """Persiste e devolve a ocorrência com identificador."""

    def obter(self, id_: int) -> Optional[Ocorrencia]:
        """Busca por identificador."""

    def listar(self, filtro) -> Pagina:
        """Lista conforme um ``FiltroOcorrencias``."""


Relogio = Callable[[], datetime]
