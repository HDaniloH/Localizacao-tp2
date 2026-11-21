"""Rotas HTTP de ocorrências, de ponta a ponta com PostGIS."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.database import get_db
from app.ocorrencias.rotas import router, usuario_atual_id

CORPO = {
    "titulo": "Buraco na via",
    "categoria_id": None,  # preenchido com a massa
    "descricao": "Próximo à faixa",
    "latitude": -15.7942,
    "longitude": -47.8825,
}


@pytest.fixture
def app_teste(db):
    # App próprio: não depende de app/main.py incluir o router.
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_db] = lambda: db
    return app


@pytest.fixture
def cliente(app_teste, massa):
    app_teste.dependency_overrides[usuario_atual_id] = lambda: massa.usuario_id
    return TestClient(app_teste)


@pytest.fixture
def corpo(massa):
    return {**CORPO, "categoria_id": massa.cat_buraco}


def test_registrar_201(cliente, corpo):
    r = cliente.post("/ocorrencias", json=corpo)
    assert r.status_code == 201
    dados = r.json()
    assert dados["status"] == "REGISTRADO"
    assert (dados["latitude"], dados["longitude"]) == (-15.7942, -47.8825)
    assert dados["titulo"] == "Buraco na via"
    assert "usuario_id" not in dados


def test_sem_autenticacao_401(app_teste, corpo):
    r = TestClient(app_teste).post("/ocorrencias", json=corpo)
    assert r.status_code == 401
    assert r.json()["detail"] == "Not authenticated"


def test_campo_invalido_422(cliente, corpo):
    r = cliente.post("/ocorrencias", json={**corpo, "latitude": 91})
    assert r.status_code == 422


def test_metadado_do_servidor_422(cliente, corpo):
    r = cliente.post("/ocorrencias", json={**corpo, "status": "RESOLVIDO"})
    assert r.status_code == 422


@pytest.mark.parametrize(
    ("ajuste", "codigo"),
    [
        ({"categoria_id": 999}, "categoria_inexistente"),
        ({"latitude": -23.55, "longitude": -46.63}, "fora_da_area_autorizada"),
    ],
)
def test_regra_de_negocio_422(cliente, corpo, ajuste, codigo):
    r = cliente.post("/ocorrencias", json={**corpo, **ajuste})
    assert r.status_code == 422
    assert r.json()["detail"]["codigo"] == codigo


def test_categoria_inativa_422(cliente, corpo, massa):
    r = cliente.post("/ocorrencias", json={**corpo, "categoria_id": massa.cat_inativa})
    assert r.json()["detail"]["codigo"] == "categoria_inativa"


def test_listar_e_detalhar(cliente, corpo, massa):
    criada = cliente.post("/ocorrencias", json=corpo).json()
    cliente.post("/ocorrencias", json={**corpo, "categoria_id": massa.cat_luz})

    r = cliente.get(
        "/ocorrencias",
        params={
            "categorias": [massa.cat_buraco],
            "status": ["REGISTRADO", "EM_ANALISE"],
            "sul": -16,
            "oeste": -48,
            "norte": -15,
            "leste": -47,
            "limite": 10,
        },
    )
    assert r.status_code == 200
    pagina = r.json()
    assert [o["id"] for o in pagina["itens"]] == [criada["id"]]
    assert pagina["proximo_offset"] is None
    assert "descricao" not in pagina["itens"][0]

    det = cliente.get(f"/ocorrencias/{criada['id']}")
    assert det.status_code == 200
    assert det.json()["descricao"] == "Próximo à faixa"


def test_listar_sem_login_e_permitido(app_teste, massa):
    assert TestClient(app_teste).get("/ocorrencias").status_code == 200


@pytest.mark.parametrize(
    "params",
    [
        {"sul": -16},
        {"inicio": "2026-11-16T00:00:00"},
        {"limite": 0},
        {"status": "XYZ"},
    ],
)
def test_filtro_invalido_422(cliente, params):
    assert cliente.get("/ocorrencias", params=params).status_code == 422


def test_detalhe_inexistente_404(cliente):
    r = cliente.get("/ocorrencias/999")
    assert r.status_code == 404
    assert r.json()["detail"]["codigo"] == "ocorrencia_nao_encontrada"


def test_usuario_atual_id_retorna_id_do_usuario():
    from types import SimpleNamespace

    assert usuario_atual_id(SimpleNamespace(id=42)) == 42