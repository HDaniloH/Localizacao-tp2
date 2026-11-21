"""Modelos de entrada, domínio e saída das ocorrências."""

from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import StatusOcorrencia
from app.ocorrencias.geo import LAT_MAX, LAT_MIN, LON_MAX, LON_MIN, Ponto

TITULO_MAX = 120  # mesmo tamanho da coluna ocorrencias.titulo
DESCRICAO_MAX = 2000  # proposta; a coluna é Text

Latitude = Annotated[float, Field(ge=LAT_MIN, le=LAT_MAX, allow_inf_nan=False)]
Longitude = Annotated[float, Field(ge=LON_MIN, le=LON_MAX, allow_inf_nan=False)]


class OcorrenciaEntrada(BaseModel):
    """Corpo da requisição de cadastro (US01).

    Modo estrito: não converte texto nem booleano em número. Campos extras são
    proibidos, então o cliente não define autor, status, data, id nem foto.
    """

    model_config = ConfigDict(extra="forbid", strict=True, str_strip_whitespace=True)

    titulo: Annotated[str, Field(min_length=1, max_length=TITULO_MAX)]
    categoria_id: Annotated[int, Field(gt=0)]
    descricao: Annotated[str, Field(min_length=1, max_length=DESCRICAO_MAX)]
    latitude: Latitude
    longitude: Longitude


@dataclass(frozen=True)
class NovaOcorrencia:
    """Dados validados prontos para persistir, ainda sem identificador."""

    usuario_id: int
    categoria_id: int
    titulo: str
    descricao: str
    ponto: Ponto
    status: StatusOcorrencia
    criado_em: datetime


@dataclass(frozen=True)
class Ocorrencia:
    """Ocorrência persistida, independente do ORM."""

    id: int
    usuario_id: int
    categoria_id: int
    titulo: str
    descricao: str
    ponto: Ponto
    status: StatusOcorrencia
    criado_em: datetime
    foto_url: Optional[str]


class ResumoMapa(BaseModel):
    """Dados de um marcador do mapa (US02). Não expõe o autor."""

    id: int
    latitude: float
    longitude: float
    categoria_id: int
    titulo: str
    status: StatusOcorrencia
    criado_em: datetime
    foto_url: Optional[str]

    @classmethod
    def de(cls, oc: Ocorrencia) -> "ResumoMapa":
        """Cria o resumo a partir da ocorrência."""
        return cls(
            id=oc.id,
            latitude=oc.ponto.latitude,
            longitude=oc.ponto.longitude,
            categoria_id=oc.categoria_id,
            titulo=oc.titulo,
            status=oc.status,
            criado_em=oc.criado_em,
            foto_url=oc.foto_url,
        )


class DetalheOcorrencia(ResumoMapa):
    """Detalhe exibido ao selecionar um marcador. Não expõe o autor."""

    descricao: str

    @classmethod
    def de(cls, oc: Ocorrencia) -> "DetalheOcorrencia":
        """Cria o detalhe, com a descrição completa."""
        resumo = ResumoMapa.de(oc).model_dump()
        return cls(**resumo, descricao=oc.descricao)
