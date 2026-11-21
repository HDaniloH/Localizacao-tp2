"""Validação de coordenadas e do retângulo visível do mapa.

As coordenadas são sempre identificadas por nome (``latitude``/``longitude``)
para evitar inversão de eixos. No PostGIS (SRID 4326) a ordem é X = longitude
e Y = latitude; use :meth:`Ponto.como_xy`.
"""

import math
from dataclasses import dataclass

LAT_MIN, LAT_MAX = -90.0, 90.0
LON_MIN, LON_MAX = -180.0, 180.0


class CoordenadaInvalida(ValueError):
    """Coordenada não numérica, não finita ou fora da faixa."""


def _validar(nome: str, valor: object, minimo: float, maximo: float) -> float:
    """Valida um valor de coordenada e o devolve como ``float``.

    Args:
        nome: Nome usado na mensagem de erro.
        valor: Valor recebido.
        minimo: Limite inferior inclusivo.
        maximo: Limite superior inclusivo.

    Returns:
        O valor convertido para ``float``.

    Raises:
        CoordenadaInvalida: Se não for número real finito dentro da faixa.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise CoordenadaInvalida(f"{nome} deve ser numérica")
    numero = float(valor)
    if not math.isfinite(numero):
        raise CoordenadaInvalida(f"{nome} deve ser finita")
    if not minimo <= numero <= maximo:
        raise CoordenadaInvalida(f"{nome} deve estar entre {minimo} e {maximo}")
    return numero


@dataclass(frozen=True)
class Ponto:
    """Ponto geográfico em graus decimais (WGS 84).

    Attributes:
        latitude: Entre -90 e 90, inclusive.
        longitude: Entre -180 e 180, inclusive.
    """

    latitude: float
    longitude: float

    def __post_init__(self) -> None:
        """Valida e normaliza as coordenadas para ``float``."""
        lat = _validar("latitude", self.latitude, LAT_MIN, LAT_MAX)
        lon = _validar("longitude", self.longitude, LON_MIN, LON_MAX)
        object.__setattr__(self, "latitude", lat)
        object.__setattr__(self, "longitude", lon)

    def como_xy(self) -> tuple[float, float]:
        """Devolve ``(longitude, latitude)``, a ordem X/Y do PostGIS."""
        return (self.longitude, self.latitude)


@dataclass(frozen=True)
class RetanguloMapa:
    """Área visível do mapa; as bordas são inclusivas.

    Retângulos que cruzam o antimeridiano (``oeste > leste``) são rejeitados
    explicitamente, pois estão fora do alcance geográfico do sistema.
    """

    sul: float
    oeste: float
    norte: float
    leste: float

    def __post_init__(self) -> None:
        """Valida as bordas e a orientação do retângulo."""
        for nome, minimo, maximo in (
            ("sul", LAT_MIN, LAT_MAX),
            ("norte", LAT_MIN, LAT_MAX),
            ("oeste", LON_MIN, LON_MAX),
            ("leste", LON_MIN, LON_MAX),
        ):
            valor = _validar(nome, getattr(self, nome), minimo, maximo)
            object.__setattr__(self, nome, valor)
        if self.sul > self.norte:
            raise CoordenadaInvalida("sul deve ser menor ou igual a norte")
        if self.oeste > self.leste:
            raise CoordenadaInvalida(
                "oeste maior que leste (cruzamento do antimeridiano não suportado)"
            )
