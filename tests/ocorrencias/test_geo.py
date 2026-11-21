"""Validação de coordenadas e retângulo do mapa (US01-04..07, US02-06)."""

import math

import pytest

from app.ocorrencias.geo import CoordenadaInvalida, Ponto, RetanguloMapa


@pytest.mark.parametrize("lat", [-90, -90.0, 0, 0.0, 90, 90.0, -15.7939])
def test_latitude_valida_incluindo_limites_e_zero(lat):
    assert Ponto(latitude=lat, longitude=0).latitude == float(lat)


@pytest.mark.parametrize("lon", [-180, 0, 180, -47.8828])
def test_longitude_valida_incluindo_limites_e_zero(lon):
    assert Ponto(latitude=0, longitude=lon).longitude == float(lon)


@pytest.mark.parametrize("lat", [-90.0001, 90.0001, -1000, 1000])
def test_latitude_fora_da_faixa(lat):
    with pytest.raises(CoordenadaInvalida, match="latitude"):
        Ponto(latitude=lat, longitude=0)


@pytest.mark.parametrize("lon", [-180.0001, 180.0001, 360])
def test_longitude_fora_da_faixa(lon):
    with pytest.raises(CoordenadaInvalida, match="longitude"):
        Ponto(latitude=0, longitude=lon)


@pytest.mark.parametrize("valor", [math.nan, math.inf, -math.inf])
def test_coordenada_nao_finita(valor):
    with pytest.raises(CoordenadaInvalida):
        Ponto(latitude=valor, longitude=0)
    with pytest.raises(CoordenadaInvalida):
        Ponto(latitude=0, longitude=valor)


@pytest.mark.parametrize("valor", [True, False, "10", None, [1]])
def test_coordenada_de_tipo_incompativel(valor):
    with pytest.raises(CoordenadaInvalida):
        Ponto(latitude=valor, longitude=0)


def test_ponto_ordem_xy_para_postgis():
    p = Ponto(latitude=-15.79, longitude=-47.88)
    assert (p.latitude, p.longitude) == (-15.79, -47.88)
    assert p.como_xy() == (-47.88, -15.79)


def test_retangulo_valido():
    r = RetanguloMapa(sul=-16, oeste=-48, norte=-15, leste=-47)
    assert (r.sul, r.oeste, r.norte, r.leste) == (-16.0, -48.0, -15.0, -47.0)


def test_retangulo_sul_maior_que_norte():
    with pytest.raises(CoordenadaInvalida, match="sul"):
        RetanguloMapa(sul=-15, oeste=-48, norte=-16, leste=-47)


def test_retangulo_cruzando_antimeridiano():
    with pytest.raises(CoordenadaInvalida, match="antimeridiano"):
        RetanguloMapa(sul=-10, oeste=170, norte=10, leste=-170)


@pytest.mark.parametrize(
    "bordas",
    [(-91, -48, -15, -47), (-16, -181, -15, -47), (-16, -48, 91, -47)],
)
def test_retangulo_com_borda_fora_da_faixa(bordas):
    sul, oeste, norte, leste = bordas
    with pytest.raises(CoordenadaInvalida):
        RetanguloMapa(sul=sul, oeste=oeste, norte=norte, leste=leste)
