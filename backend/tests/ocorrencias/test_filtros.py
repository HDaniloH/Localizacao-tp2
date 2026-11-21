"""Validação dos filtros de consulta (US02-08, 11)."""

from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.models import StatusOcorrencia
from app.ocorrencias.filtros import (
    LIMITE_MAX,
    LIMITE_PADRAO,
    STATUS_ATIVOS,
    FiltroOcorrencias,
)

T0 = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def test_padroes():
    f = FiltroOcorrencias()
    assert f.limite == LIMITE_PADRAO
    assert f.offset == 0
    assert f.retangulo is None
    assert f.status_efetivos == STATUS_ATIVOS


def test_ativas_sao_registrado_e_em_analise():
    assert STATUS_ATIVOS == {StatusOcorrencia.REGISTRADO, StatusOcorrencia.EM_ANALISE}


def test_status_explicito_substitui_padrao():
    f = FiltroOcorrencias(status={StatusOcorrencia.RESOLVIDO})
    assert f.status_efetivos == {StatusOcorrencia.RESOLVIDO}


@pytest.mark.parametrize(
    "dados",
    [
        {"inicio": T0, "fim": T0},
        {"inicio": T0 + timedelta(days=1), "fim": T0},
        {"inicio": "2026-11-16T12:00:00"},
        {"fim": "2026-11-16T12:00:00"},
        {"sul": -16, "oeste": -48, "norte": -15},
        {"sul": -15, "oeste": -48, "norte": -16, "leste": -47},
        {"sul": -16, "oeste": 170, "norte": -15, "leste": -170},
        {"sul": -95, "oeste": -48, "norte": -15, "leste": -47},
        {"limite": 0},
        {"limite": LIMITE_MAX + 1},
        {"offset": -1},
        {"status": {"inexistente"}},
        {"categorias": set()},
        {"status": set()},
        {"desconhecido": 1},
    ],
)
def test_filtro_invalido_rejeitado(dados):
    with pytest.raises(ValidationError):
        FiltroOcorrencias.model_validate(dados)


def test_aceita_valores_textuais_de_query():
    f = FiltroOcorrencias.model_validate(
        {
            "categorias": ["1", "2"],
            "status": ["EM_ANALISE"],
            "inicio": "2026-11-16T00:00:00-03:00",
            "fim": "2026-11-17T00:00:00Z",
            "sul": "-16",
            "oeste": "-48",
            "norte": "-15",
            "leste": "-47",
            "limite": "10",
            "offset": "20",
        }
    )
    assert f.categorias == {1, 2}
    assert f.status == {StatusOcorrencia.EM_ANALISE}
    assert f.retangulo.sul == -16.0
    assert (f.limite, f.offset) == (10, 20)
