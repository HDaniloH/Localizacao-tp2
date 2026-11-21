"""Validação do cadastro e projeções de saída (US01-02, 03, 10; US02-01)."""

import math
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.models import StatusOcorrencia
from app.ocorrencias.geo import Ponto
from app.ocorrencias.schemas import (
    DESCRICAO_MAX,
    TITULO_MAX,
    DetalheOcorrencia,
    Ocorrencia,
    OcorrenciaEntrada,
    ResumoMapa,
)

VALIDO = {
    "titulo": "Buraco na calçada",
    "categoria_id": 1,
    "descricao": "Em frente ao bloco A, risco para pedestres",
    "latitude": -15.7939,
    "longitude": -47.8828,
}
OBRIGATORIOS = ["titulo", "categoria_id", "descricao", "latitude", "longitude"]


def campos_com_erro(exc):
    return {str(e["loc"][0]) for e in exc.errors()}


def test_entrada_valida():
    e = OcorrenciaEntrada.model_validate(VALIDO)
    assert e.categoria_id == 1
    assert e.latitude == -15.7939


def test_coordenadas_inteiras_e_zero_aceitas():
    e = OcorrenciaEntrada.model_validate({**VALIDO, "latitude": 0, "longitude": 0})
    assert (e.latitude, e.longitude) == (0.0, 0.0)


@pytest.mark.parametrize("campo", OBRIGATORIOS)
def test_campo_obrigatorio_ausente(campo):
    dados = {k: v for k, v in VALIDO.items() if k != campo}
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate(dados)
    assert campos_com_erro(exc.value) == {campo}


@pytest.mark.parametrize("campo", OBRIGATORIOS)
def test_campo_obrigatorio_nulo(campo):
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate({**VALIDO, campo: None})
    assert campos_com_erro(exc.value) == {campo}


@pytest.mark.parametrize("campo", ["titulo", "descricao"])
@pytest.mark.parametrize("texto", ["", "   ", "\n\t "])
def test_texto_vazio_ou_so_espacos(campo, texto):
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate({**VALIDO, campo: texto})
    assert campos_com_erro(exc.value) == {campo}


def test_textos_tem_espacos_externos_removidos():
    e = OcorrenciaEntrada.model_validate(
        {**VALIDO, "titulo": "  Poste  ", "descricao": "  apagado  "}
    )
    assert (e.titulo, e.descricao) == ("Poste", "apagado")


@pytest.mark.parametrize(
    ("campo", "maximo"), [("titulo", TITULO_MAX), ("descricao", DESCRICAO_MAX)]
)
def test_tamanho_maximo(campo, maximo):
    OcorrenciaEntrada.model_validate({**VALIDO, campo: "x" * maximo})
    with pytest.raises(ValidationError):
        OcorrenciaEntrada.model_validate({**VALIDO, campo: "x" * (maximo + 1)})


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("latitude", 90.1),
        ("latitude", -90.1),
        ("longitude", 180.1),
        ("longitude", -180.1),
        ("latitude", math.nan),
        ("longitude", math.inf),
    ],
)
def test_coordenada_invalida(campo, valor):
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate({**VALIDO, campo: valor})
    assert campos_com_erro(exc.value) == {campo}


@pytest.mark.parametrize(
    ("campo", "valor"),
    [
        ("latitude", "-15.79"),
        ("latitude", True),
        ("categoria_id", "1"),
        ("categoria_id", 1.5),
        ("categoria_id", 0),
        ("categoria_id", -3),
        ("descricao", 123),
    ],
)
def test_tipos_incompativeis(campo, valor):
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate({**VALIDO, campo: valor})
    assert campos_com_erro(exc.value) == {campo}


@pytest.mark.parametrize(
    "campo",
    ["usuario_id", "status", "criado_em", "id", "foto_url", "desconhecido"],
)
def test_metadados_do_servidor_nao_aceitos(campo):
    """US01-10: o cliente não define autor, status, data, id nem foto."""
    with pytest.raises(ValidationError) as exc:
        OcorrenciaEntrada.model_validate({**VALIDO, campo: "x"})
    assert campos_com_erro(exc.value) == {campo}


def ocorrencia(**kw):
    base = dict(
        id=5,
        usuario_id=42,
        categoria_id=1,
        titulo="Buraco",
        descricao="Grande",
        ponto=Ponto(latitude=-15.5, longitude=-47.5),
        status=StatusOcorrencia.REGISTRADO,
        criado_em=datetime(2026, 11, 16, tzinfo=timezone.utc),
        foto_url=None,
    )
    return Ocorrencia(**{**base, **kw})


def test_resumo_mapa_tem_dados_do_marcador_sem_autor():
    dados = ResumoMapa.de(ocorrencia()).model_dump(mode="json")
    assert dados == {
        "id": 5,
        "latitude": -15.5,
        "longitude": -47.5,
        "categoria_id": 1,
        "titulo": "Buraco",
        "status": "REGISTRADO",
        "criado_em": "2026-11-16T00:00:00Z",
        "foto_url": None,
    }


def test_detalhe_tem_descricao_completa_sem_autor():
    longa = "a" * 500
    dados = DetalheOcorrencia.de(ocorrencia(descricao=longa)).model_dump()
    assert dados["descricao"] == longa
    assert "usuario_id" not in dados
