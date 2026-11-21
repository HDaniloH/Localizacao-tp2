"""Ponto de entrada da API RESTful do Sistema de Ocorrências Urbanas."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import models  # noqa: F401  (registra as tabelas no metadata)
from app.api.routes import auth, categorias, usuarios
from app.core.exceptions import ErroDominio
from app.database import Base, engine

from app.ocorrencias.rotas import router as ocorrencias_router


@asynccontextmanager
async def ciclo_de_vida(_app: FastAPI) -> AsyncIterator[None]:
    """Cria as tabelas que faltarem ao subir a aplicação.

    Provisório: quando o grupo adotar migrações (ex.: Alembic), remover.
    """
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="API - Sistema de Registro e Acompanhamento de Ocorrências Urbanas",
    description="Backend georreferenciado desenvolvido para TP2 - UnB.",
    version="0.1.0",
    lifespan=ciclo_de_vida,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ErroDominio)
async def tratar_erro_dominio(_req: Request, exc: ErroDominio) -> JSONResponse:
    """Converte exceções de domínio em respostas HTTP."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detalhe})


@app.get("/health", tags=["Infraestrutura"])
def health_check() -> dict[str, str]:
    """Verifica se a API está online e operacional."""
    return {"status": "ok", "service": "ocorrencias-urbanas-api"}


app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(categorias.router_admin)
app.include_router(categorias.router_publico)
app.include_router(ocorrencias_router)