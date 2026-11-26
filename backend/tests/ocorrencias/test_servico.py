"""Regras do serviço com doubles (US01-01, 08, 09, 10, 11; US02-10)."""

from datetime import datetime, timezone

import pytest

from app.models import StatusOcorrencia
from app.ocorrencias.erros import (
    CategoriaInativa,
    CategoriaInexistente,
    ForaDaAreaAutorizada,
    NaoAutenticado,
    OcorrenciaNaoEncontrada,
)
from app.ocorrencias.filtros import FiltroOcorrencias
from app.ocorrencias.schemas import OcorrenciaEntrada
from app.ocorrencias.servico import ServicoOcorrencias

from .fakes import AreaFake, CatalogoFake, RelogioFake, RepositorioFake

T0 = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)


def entrada(**kw):
    base = {
        "titulo": "Poste apagado",
        "categoria_id": 1,
        "descricao": "Rua escura",
        "latitude": -15.7939,
        "longitude": -47.8828,
    }
    return OcorrenciaEntrada.model_validate({**base, **kw})


@pytest.fixture
def repo():
    return RepositorioFake()


@pytest.fixture
def area():
    return AreaFake()


@pytest.fixture
def servico(repo, area):
    return ServicoOcorrencias(repo, CatalogoFake(), area, RelogioFake(T0))


def test_registro_valido_com_metadados_do_servidor(servico, repo):
    oc = servico.registrar(usuario_id=42, entrada=entrada())
    assert oc.usuario_id == 42
    assert oc.status is StatusOcorrencia.REGISTRADO
    assert oc.criado_em == T0
    assert oc.titulo == "Poste apagado"
    assert (oc.ponto.latitude, oc.ponto.longitude) == (-15.7939, -47.8828)
    assert repo.obter(oc.id) == oc


def test_sem_autenticacao(servico, repo):
    with pytest.raises(NaoAutenticado):
        servico.registrar(usuario_id=None, entrada=entrada())
    assert repo.dados == {}


def test_categoria_inexistente(servico, repo):
    with pytest.raises(CategoriaInexistente):
        servico.registrar(usuario_id=1, entrada=entrada(categoria_id=777))
    assert repo.dados == {}


def test_categoria_inativa(servico, repo):
    with pytest.raises(CategoriaInativa):
        servico.registrar(usuario_id=1, entrada=entrada(categoria_id=9))
    assert repo.dados == {}


def test_fora_da_area_autorizada(repo):
    area = AreaFake(autoriza=False)
    servico = ServicoOcorrencias(repo, CatalogoFake(), area, RelogioFake(T0))
    with pytest.raises(ForaDaAreaAutorizada):
        servico.registrar(usuario_id=1, entrada=entrada())
    assert repo.dados == {}
    assert area.consultados[0].longitude == -47.8828


def test_relogio_sem_fuso_e_erro_de_configuracao(repo, area):
    servico = ServicoOcorrencias(
        repo, CatalogoFake(), area, lambda: datetime(2026, 1, 1)
    )
    with pytest.raises(ValueError, match="fuso"):
        servico.registrar(usuario_id=1, entrada=entrada())
    assert repo.dados == {}


def test_relogio_padrao_em_utc(repo, area):
    servico = ServicoOcorrencias(repo, CatalogoFake(), area)
    oc = servico.registrar(usuario_id=1, entrada=entrada())
    assert oc.criado_em.utcoffset().total_seconds() == 0


def test_detalhar(servico):
    oc = servico.registrar(usuario_id=1, entrada=entrada())
    assert servico.detalhar(oc.id) == oc
    with pytest.raises(OcorrenciaNaoEncontrada):
        servico.detalhar(999)


def test_consultar_repassa_filtro(servico, repo):
    filtro = FiltroOcorrencias(categorias={1})
    servico.consultar(filtro)
    assert repo.filtros == [filtro]
