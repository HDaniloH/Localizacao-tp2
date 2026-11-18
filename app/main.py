"""Ponto de entrada da API RESTful do Sistema de Ocorrências Urbanas."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="API - Sistema de Registro e Acompanhamento de Ocorrências Urbanas",
    description="Backend georreferenciado desenvolvido para TP2 - UnB.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Infraestrutura"])
def health_check() -> dict[str, str]:
    """Verifica se a API está online e operacional."""
    return {"status": "ok", "service": "ocorrencias-urbanas-api"}
