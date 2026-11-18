"""Testes de integração das rotas base da aplicação FastAPI."""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Garante que o endpoint /health retorna status 200 e payload esperado."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "ocorrencias-urbanas-api",
    }
