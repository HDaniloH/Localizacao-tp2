"""Configurações da autenticação, lidas de variáveis de ambiente.

A conexão com o banco fica em ``app.database`` (``DATABASE_URL``).
"""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    """Parâmetros de configuração da autenticação.

    Attributes:
        secret_key: Chave usada para assinar os tokens JWT.
        algoritmo_jwt: Algoritmo de assinatura do JWT.
        expiracao_token_minutos: Validade do token de acesso, em minutos.
        bcrypt_rounds: Custo do bcrypt (12 em produção; menor nos testes).
    """

    secret_key: str
    algoritmo_jwt: str
    expiracao_token_minutos: int
    bcrypt_rounds: int


def carregar_settings() -> Settings:
    """Monta as configurações a partir do ambiente.

    Returns:
        Instância imutável de :class:`Settings`.
    """
    return Settings(
        secret_key=os.getenv(
            "SECRET_KEY", "dev-inseguro-troque-em-producao-0123456789abcdef"
        ),
        algoritmo_jwt=os.getenv("JWT_ALGORITMO", "HS256"),
        expiracao_token_minutos=int(os.getenv("JWT_EXPIRACAO_MIN", "60")),
        bcrypt_rounds=int(os.getenv("BCRYPT_ROUNDS", "12")),
    )


settings = carregar_settings()
