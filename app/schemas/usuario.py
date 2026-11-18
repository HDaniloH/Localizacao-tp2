"""Schemas Pydantic de usuário e autenticação."""

from datetime import datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


def validar_forca_senha(senha: str) -> str:
    """Exige ao menos uma letra e um número na senha.

    Args:
        senha: Senha informada pelo usuário.

    Returns:
        A própria senha, se for válida.

    Raises:
        ValueError: Se faltar letra ou número.
    """
    if not any(c.isalpha() for c in senha):
        raise ValueError("A senha deve conter ao menos uma letra")
    if not any(c.isdigit() for c in senha):
        raise ValueError("A senha deve conter ao menos um número")
    return senha


# bcrypt só considera os primeiros 72 bytes, por isso o limite.
Senha = Annotated[
    str,
    Field(min_length=8, max_length=72),
    AfterValidator(validar_forca_senha),
]
Nome = Annotated[str, Field(min_length=2, max_length=120)]
# A coluna ``usuarios.email`` comporta até 150 caracteres.
Email = Annotated[EmailStr, Field(max_length=150)]


class UsuarioCriar(BaseModel):
    """Dados de cadastro público (nunca gera administrador)."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: Nome
    email: Email
    senha: Senha


class UsuarioCriarAdmin(UsuarioCriar):
    """Cadastro feito por um administrador, que pode criar outro admin."""

    is_admin: bool = False


class UsuarioAtualizar(BaseModel):
    """Campos que o próprio usuário pode alterar."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nome: Nome | None = None
    email: Email | None = None
    senha: Senha | None = None


class UsuarioAtualizarAdmin(UsuarioAtualizar):
    """Campos extras que só o administrador pode alterar."""

    is_admin: bool | None = None
    ativo: bool | None = None


class UsuarioPublico(BaseModel):
    """Representação de usuário devolvida pela API (sem senha)."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    email: EmailStr
    is_admin: bool
    ativo: bool
    criado_em: datetime


class Token(BaseModel):
    """Resposta do login."""

    access_token: str
    token_type: str = "bearer"
