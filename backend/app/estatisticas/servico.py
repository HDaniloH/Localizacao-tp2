"""Montagem das estatísticas do painel (US04)."""

from dataclasses import dataclass
from typing import Optional, Protocol

from app.core.exceptions import RecursoNaoEncontrado
from app.estatisticas.schemas import (
    FORA_DAS_REGIOES,
    EstatisticaRegiao,
    FiltroEstatisticas,
    PorStatus,
    Resumo,
)


class RegiaoNaoEncontrada(RecursoNaoEncontrado):
    """O filtro pede uma região que não está cadastrada (HTTP 404)."""


@dataclass(frozen=True)
class ContagemRegiao:
    """Contagem por status numa região (``regiao_id`` nulo = fora de todas)."""

    regiao_id: Optional[int]
    nome: str
    por_status: PorStatus


class FonteEstatisticas(Protocol):
    """Consultas de que o painel depende.

    A implementação real é ``RepositorioEstatisticasSQL``; os testes do
    serviço usam uma fonte falsa.
    """

    def regiao_existe(self, regiao_id: int) -> bool:
        """Indica se a região está cadastrada."""

    def contar_por_status(self, filtro: FiltroEstatisticas) -> PorStatus:
        """Quantidade de ocorrências em cada status."""

    def contar_por_regiao(self, filtro: FiltroEstatisticas) -> list[ContagemRegiao]:
        """Contagem por status em cada região, mais a das de fora."""


def _ordem_das_regioes(item: EstatisticaRegiao) -> tuple[bool, int, str]:
    """Maior total primeiro, empate em ordem alfabética, "fora" no fim."""
    return (item.regiao_id is None, -item.total, item.regiao)


class ServicoEstatisticas:
    """Calcula as estatísticas a partir de uma fonte de dados.

    Args:
        fonte: Consultas de contagem.
    """

    def __init__(self, fonte: FonteEstatisticas) -> None:
        self._fonte = fonte

    def _checar_regiao(self, filtro: FiltroEstatisticas) -> None:
        if filtro.regiao_id is not None and not self._fonte.regiao_existe(
            filtro.regiao_id
        ):
            raise RegiaoNaoEncontrada(f"região {filtro.regiao_id} não encontrada")

    def resumo(self, filtro: FiltroEstatisticas) -> Resumo:
        """Totais do filtro: resolvidas × pendentes e taxa de resolução.

        Raises:
            RegiaoNaoEncontrada: ``regiao_id`` não cadastrada.
        """
        self._checar_regiao(filtro)
        return Resumo.de(self._fonte.contar_por_status(filtro))

    def regioes(self, filtro: FiltroEstatisticas) -> list[EstatisticaRegiao]:
        """Resolvidas × pendentes em cada região (distribuição espacial).

        Raises:
            RegiaoNaoEncontrada: ``regiao_id`` não cadastrada.
        """
        self._checar_regiao(filtro)
        itens = [
            EstatisticaRegiao(
                regiao_id=c.regiao_id,
                regiao=c.nome if c.regiao_id is not None else FORA_DAS_REGIOES,
                **EstatisticaRegiao.campos(c.por_status),
            )
            for c in self._fonte.contar_por_regiao(filtro)
        ]
        return sorted(itens, key=_ordem_das_regioes)
