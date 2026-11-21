"""Persistência e consultas reais no PostGIS (US01-12; US02-01..12)."""

from datetime import timedelta

import pytest
from geoalchemy2.shape import to_shape

from app.models import Ocorrencia as OcorrenciaModel
from app.models import PerimetroAutorizado
from app.models import StatusOcorrencia as S
from app.ocorrencias.filtros import LIMITE_PADRAO, FiltroOcorrencias
from app.ocorrencias.geo import Ponto
from app.ocorrencias.portas import SituacaoCategoria
from app.ocorrencias.repositorio_sql import (
    CatalogoCategoriasSQL,
    PerimetrosSQL,
    RepositorioSQL,
)
from app.ocorrencias.schemas import NovaOcorrencia

from .conftest import T0


@pytest.fixture
def repo(db):
    return RepositorioSQL(db)


@pytest.fixture
def criar(repo, massa):
    def _criar(cat=None, lat=-15.8, lon=-47.9, status=S.REGISTRADO, quando=T0):
        return repo.adicionar(
            NovaOcorrencia(
                usuario_id=massa.usuario_id,
                categoria_id=cat or massa.cat_buraco,
                titulo="t",
                descricao="d",
                ponto=Ponto(latitude=lat, longitude=lon),
                status=status,
                criado_em=quando,
            )
        )

    return _criar


def ids(pagina):
    return [o.id for o in pagina.itens]


def h(n):
    return T0 + timedelta(hours=n)


# --- Persistência (US01-01, US01-12) ---------------------------------------


def test_adicionar_e_obter_preserva_dados_e_eixos(repo, criar, db):
    oc = criar(lat=-15.7942, lon=-47.8825)
    assert oc.id is not None
    lido = repo.obter(oc.id)
    assert lido == oc
    assert (lido.ponto.latitude, lido.ponto.longitude) == (-15.7942, -47.8825)
    assert lido.criado_em == T0
    geom = to_shape(db.get(OcorrenciaModel, oc.id).localizacao)
    assert (geom.x, geom.y) == (-47.8825, -15.7942)  # X = longitude


def test_obter_inexistente(repo, massa):
    assert repo.obter(999) is None


# --- Consultas (US02) ------------------------------------------------------


def test_consulta_vazia(repo, massa):
    p = repo.listar(FiltroOcorrencias())
    assert (p.itens, p.proximo_offset) == ([], None)


def test_filtro_categoria(repo, criar, massa):
    a = criar(cat=massa.cat_buraco)
    criar(cat=massa.cat_luz)
    assert ids(repo.listar(FiltroOcorrencias(categorias={massa.cat_buraco}))) == [a.id]


def test_filtro_status_e_padrao_de_ativas(repo, criar):
    r = criar(status=S.REGISTRADO, quando=h(0))
    a = criar(status=S.EM_ANALISE, quando=h(1))
    s = criar(status=S.RESOLVIDO, quando=h(2))
    assert ids(repo.listar(FiltroOcorrencias())) == [a.id, r.id]
    assert ids(repo.listar(FiltroOcorrencias(status={S.RESOLVIDO}))) == [s.id]
    todos = FiltroOcorrencias(status=set(S))
    assert ids(repo.listar(todos)) == [s.id, a.id, r.id]


def test_filtro_intervalo_inicio_inclusivo_fim_exclusivo(repo, criar):
    criar(quando=h(0))
    no_inicio = criar(quando=h(1))
    dentro = criar(quando=h(2))
    criar(quando=h(3))
    f = FiltroOcorrencias(inicio=h(1), fim=h(3))
    assert ids(repo.listar(f)) == [dentro.id, no_inicio.id]


def test_filtro_retangulo_com_bordas_inclusivas(repo, criar):
    dentro = criar(lat=-15.5, lon=-47.5, quando=h(0))
    borda = criar(lat=-15.0, lon=-47.0, quando=h(1))
    criar(lat=-14.9, lon=-47.5)
    criar(lat=-15.5, lon=-46.9)
    f = FiltroOcorrencias(sul=-16, oeste=-48, norte=-15, leste=-47)
    assert ids(repo.listar(f)) == [borda.id, dentro.id]


def test_filtros_combinados_sao_intersecao(repo, criar, massa):
    alvo = criar(cat=massa.cat_buraco, lat=-15.5, lon=-47.5, status=S.EM_ANALISE)
    criar(cat=massa.cat_luz, lat=-15.5, lon=-47.5, status=S.EM_ANALISE)
    criar(cat=massa.cat_buraco, lat=-10.0, lon=-47.5, status=S.EM_ANALISE)
    criar(cat=massa.cat_buraco, lat=-15.5, lon=-47.5, status=S.REGISTRADO)
    criar(cat=massa.cat_buraco, lat=-15.5, lon=-47.5, status=S.EM_ANALISE, quando=h(-5))
    f = FiltroOcorrencias(
        categorias={massa.cat_buraco},
        status={S.EM_ANALISE},
        inicio=T0,
        sul=-16,
        oeste=-48,
        norte=-15,
        leste=-47,
    )
    assert ids(repo.listar(f)) == [alvo.id]


def test_ordem_recente_primeiro_com_desempate_por_id(repo, criar):
    a = criar(quando=h(0))
    b = criar(quando=h(0))
    c = criar(quando=h(1))
    d = criar(quando=h(0))
    assert ids(repo.listar(FiltroOcorrencias())) == [c.id, d.id, b.id, a.id]


def test_paginacao_sem_duplicar_nem_perder(repo, criar):
    criados = [criar(quando=h(i % 3)) for i in range(10)]
    vistos, offset = [], 0
    while offset is not None:
        p = repo.listar(FiltroOcorrencias(limite=3, offset=offset))
        assert len(p.itens) <= 3
        vistos += ids(p)
        offset = p.proximo_offset
    assert sorted(vistos) == sorted(o.id for o in criados)
    assert len(vistos) == len(set(vistos))


def test_limite_padrao_trunca_e_indica_continuacao(repo, criar):
    for _ in range(LIMITE_PADRAO + 2):
        criar()
    p = repo.listar(FiltroOcorrencias())
    assert len(p.itens) == LIMITE_PADRAO
    assert p.proximo_offset == LIMITE_PADRAO


# --- Adaptadores do módulo administrativo (US05) ---------------------------


def test_catalogo_categorias(db, massa):
    cat = CatalogoCategoriasSQL(db)
    assert cat.situacao(massa.cat_buraco) is SituacaoCategoria.ATIVA
    assert cat.situacao(massa.cat_inativa) is SituacaoCategoria.INATIVA
    assert cat.situacao(999) is SituacaoCategoria.INEXISTENTE


@pytest.mark.parametrize(
    ("lat", "lon", "esperado"),
    [
        (-15.79, -47.88, True),  # dentro
        (-16.10, -47.80, True),  # borda sul
        (-15.50, -48.30, True),  # vértice
        (-16.20, -47.80, False),  # fora
        (-23.55, -46.63, False),  # São Paulo
    ],
)
def test_perimetros_autorizados(db, massa, lat, lon, esperado):
    politica = PerimetrosSQL(db)
    assert politica.ponto_autorizado(Ponto(latitude=lat, longitude=lon)) is esperado


def test_sem_perimetro_cadastrado(db):
    db.query(PerimetroAutorizado).delete()
    db.commit()
    p = Ponto(latitude=-15.79, longitude=-47.88)
    assert PerimetrosSQL(db).ponto_autorizado(p) is False
    assert PerimetrosSQL(db, permitir_sem_perimetros=True).ponto_autorizado(p)


def test_permitir_sem_perimetros_nao_ignora_perimetros_existentes(db, massa):
    sp = Ponto(latitude=-23.55, longitude=-46.63)
    assert not PerimetrosSQL(db, permitir_sem_perimetros=True).ponto_autorizado(sp)
