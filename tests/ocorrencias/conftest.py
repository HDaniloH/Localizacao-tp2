"""Fixtures do módulo de ocorrências: banco PostGIS limpo e massa de dados."""

from dataclasses import dataclass
from datetime import datetime, timezone

import pytest
from geoalchemy2.elements import WKTElement

from app.database import Base, SessionLocal, engine
from app.models import Categoria, PerimetroAutorizado, Usuario

T0 = datetime(2026, 11, 16, 12, 0, tzinfo=timezone.utc)

# Retângulo que cobre o Distrito Federal (aprox.).
POLIGONO_DF = (
    "POLYGON((-48.30 -16.10, -47.30 -16.10, -47.30 -15.50, "
    "-48.30 -15.50, -48.30 -16.10))"
)


@dataclass
class Massa:
    """Identificadores criados para os testes."""

    usuario_id: int
    cat_buraco: int
    cat_luz: int
    cat_inativa: int


@pytest.fixture
def db():
    """Cria tabelas limpas no PostGIS e remove ao final."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def massa(db):
    """Usuário, categorias (duas ativas, uma inativa) e perímetro do DF."""
    usuario = Usuario(nome="Cidadã", email="cidada@unb.br", senha_hash="x")
    buraco = Categoria(nome="Buraco")
    luz = Categoria(nome="Iluminação")
    inativa = Categoria(nome="Antiga", ativa=False)
    perimetro = PerimetroAutorizado(
        nome_regiao="DF", area=WKTElement(POLIGONO_DF, srid=4326)
    )
    db.add_all([usuario, buraco, luz, inativa, perimetro])
    db.commit()
    return Massa(usuario.id, buraco.id, luz.id, inativa.id)
