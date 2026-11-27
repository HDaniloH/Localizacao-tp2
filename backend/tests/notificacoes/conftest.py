import pytest

from app.models import Ocorrencia, StatusOcorrencia


@pytest.fixture
def usuario_teste(cidadao):
    return cidadao


@pytest.fixture
def ocorrencia_teste(db_session, cidadao, criar_categoria):
    categoria = criar_categoria(nome="Iluminação")
    ocorrencia = Ocorrencia(
        titulo="Poste apagado",
        descricao="Poste sem luz na quadra",
        status=StatusOcorrencia.REGISTRADO,
        localizacao="SRID=4326;POINT(-47.8822 -15.7942)",
        usuario_id=cidadao.id,
        categoria_id=categoria.id,
    )
    db_session.add(ocorrencia)
    db_session.commit()
    db_session.refresh(ocorrencia)
    return ocorrencia