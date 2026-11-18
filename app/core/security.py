"""Funções de segurança: hash de senha e tokens JWT."""

from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

from app.core.config import settings


def gerar_hash_senha(senha: str) -> str:
    """Gera o hash bcrypt de uma senha em texto puro.

    Args:
        senha: Senha em texto puro (até 72 bytes, limite do bcrypt).

    Returns:
        Hash bcrypt codificado em UTF-8.
    """
    salt = bcrypt.gensalt(rounds=settings.bcrypt_rounds)
    return bcrypt.hashpw(senha.encode("utf-8"), salt).decode("utf-8")


def verificar_senha(senha: str, senha_hash: str) -> bool:
    """Confere se a senha corresponde ao hash armazenado.

    Args:
        senha: Senha em texto puro informada no login.
        senha_hash: Hash bcrypt salvo no banco.

    Returns:
        ``True`` se a senha confere; ``False`` caso contrário ou se o hash
        for inválido.
    """
    try:
        return bcrypt.checkpw(senha.encode("utf-8"), senha_hash.encode("utf-8"))
    except ValueError:
        return False


def criar_token_acesso(sujeito: str, expira_em: timedelta | None = None) -> str:
    """Cria um JWT de acesso assinado.

    Args:
        sujeito: Identificador do usuário (vai na claim ``sub``).
        expira_em: Validade customizada; usa a configuração se ``None``.

    Returns:
        Token JWT codificado.
    """
    if expira_em is None:
        expira_em = timedelta(minutes=settings.expiracao_token_minutos)
    agora = datetime.now(timezone.utc)
    payload = {"sub": sujeito, "iat": agora, "exp": agora + expira_em}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algoritmo_jwt)


def decodificar_token(token: str) -> str | None:
    """Valida um JWT e devolve o seu sujeito.

    Args:
        token: Token JWT recebido no cabeçalho ``Authorization``.

    Returns:
        O valor da claim ``sub``, ou ``None`` se o token for inválido,
        expirado ou não tiver sujeito.
    """
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algoritmo_jwt]
        )
    except jwt.PyJWTError:
        return None
    sujeito = payload.get("sub")
    return sujeito if isinstance(sujeito, str) else None
