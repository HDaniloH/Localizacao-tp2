"""Schemas Pydantic de categoria (US05)."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

NomeCategoria = Annotated[str, Field(min_length=2, max_length=80)]
Descricao = Annotated[str, Field(max_length=255)]


class CategoriaCriar(BaseModel):
    """Dados para cadastrar uma categoria."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: NomeCategoria
    descricao: Descricao | None = None


class CategoriaAtualizar(BaseModel):
    """Dados para alterar uma categoria (todos opcionais)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: NomeCategoria | None = None
    descricao: Descricao | None = None


class CategoriaPublica(BaseModel):
    """Representação de categoria devolvida pela API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: str | None
    ativa: bool
