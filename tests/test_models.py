"""Testes de unidade e persistência geoespacial para os modelos ORM."""

import pytest
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from sqlalchemy.exc import IntegrityError
from app.database import Base, SessionLocal, engine, get_db
from app.models import (
    Categoria,
    InscricaoNotificacao,
    LogEvento,
    LogPesquisa,
    Ocorrencia,
    PerimetroAutorizado,
    StatusOcorrencia,
    Usuario,
)


@pytest.fixture(scope="function")
def db_session():
    """Cria tabelas limpas no PostGIS antes de cada teste e limpa ao final."""
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_get_db_generator():
    """Valida o gerador de sessão transacional do banco."""
    gen = get_db()
    session = next(gen)
    assert session is not None
    with pytest.raises(StopIteration):
        next(gen)


def test_criar_ocorrencia_com_geolocalizacao(db_session):
    """Valida persistência de coordenadas GPS (Point SRID 4326) na US01."""
    user = Usuario(
        nome="Cidadao Teste",
        email="cidadao@unb.br",
        senha_hash="hash_seguro_123",
    )
    categoria = Categoria(
        nome="Buraco na Via",
        descricao="Problemas de asfaltamento e calçadas",
    )
    db_session.add_all([user, categoria])
    db_session.commit()

    ponto_gps = WKTElement("POINT(-47.8825 -15.7942)", srid=4326)
    ocorrencia = Ocorrencia(
        titulo="Cratera na pista",
        descricao="Buraco fundo próximo à faixa de pedestres",
        localizacao=ponto_gps,
        usuario_id=user.id,
        categoria_id=categoria.id,
    )
    db_session.add(ocorrencia)
    db_session.commit()
    db_session.refresh(ocorrencia)

    assert ocorrencia.id is not None
    assert ocorrencia.status == StatusOcorrencia.REGISTRADO
    geometria_salva = to_shape(ocorrencia.localizacao)
    assert pytest.approx(geometria_salva.x, 0.0001) == -47.8825
    assert pytest.approx(geometria_salva.y, 0.0001) == -15.7942


def test_email_usuario_deve_ser_unico(db_session):
    """Garante restrição de unicidade para e-mails cadastrados."""
    u1 = Usuario(nome="User 1", email="dup@unb.br", senha_hash="123")
    u2 = Usuario(nome="User 2", email="dup@unb.br", senha_hash="456")
    db_session.add(u1)
    db_session.commit()

    db_session.add(u2)
    with pytest.raises(IntegrityError):
        db_session.commit()


def test_perimetro_inscricoes_e_logs(db_session):
    """Valida persistência de polígonos (US05), alertas (US03) e logs (US06)."""
    user = Usuario(
        nome="Admin",
        email="admin@unb.br",
        senha_hash="admin_hash",
        is_admin=True,
    )
    cat = Categoria(nome="Iluminação", descricao="Postes apagados")
    poligono = WKTElement(
        (
            "POLYGON((-47.90 -15.80, -47.85 -15.80, "
            "-47.85 -15.75, -47.90 -15.75, -47.90 -15.80))"
        ),
        srid=4326,
    )
    perimetro = PerimetroAutorizado(nome_regiao="Plano Piloto", area=poligono)
    db_session.add_all([user, cat, perimetro])
    db_session.commit()

    ocorrencia = Ocorrencia(
        titulo="Poste apagado",
        descricao="Trecho escuro na quadra",
        localizacao=WKTElement("POINT(-47.88 -15.78)", srid=4326),
        usuario_id=user.id,
        categoria_id=cat.id,
    )
    db_session.add(ocorrencia)
    db_session.commit()

    inscricao = InscricaoNotificacao(
        usuario_id=user.id,
        ocorrencia_id=ocorrencia.id,
        categoria_id=cat.id,
        centro_alerta=WKTElement("POINT(-47.88 -15.78)", srid=4326),
        raio_metros=500.0,
    )
    log_evento = LogEvento(
        ocorrencia_id=ocorrencia.id,
        status_anterior=StatusOcorrencia.REGISTRADO,
        status_novo=StatusOcorrencia.EM_ANALISE,
    )
    log_pesquisa = LogPesquisa(
        usuario_id=user.id,
        termo_buscado="poste",
        regiao_filtrada="Plano Piloto",
    )
    db_session.add_all([inscricao, log_evento, log_pesquisa])
    db_session.commit()

    assert perimetro.id is not None
    assert inscricao.raio_metros == 500.0
    assert log_evento.status_novo == StatusOcorrencia.EM_ANALISE
    assert log_pesquisa.termo_buscado == "poste"
