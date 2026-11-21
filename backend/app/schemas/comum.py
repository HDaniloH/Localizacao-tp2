"""Tipos compartilhados entre os schemas."""

from datetime import datetime, timezone
from typing import Annotated

from pydantic import AfterValidator


def garantir_utc(valor: datetime) -> datetime:
    """Marca como UTC uma data sem fuso horário.

    O banco grava tudo em UTC, mas alguns bancos (como o SQLite) devolvem a
    data sem a informação de fuso. Sem ela, o JSON sairia sem o sufixo ``Z``
    e o frontend interpretaria o horário como local.

    Args:
        valor: Data lida do banco.

    Returns:
        A mesma data, com fuso UTC.
    """
    if valor.tzinfo is None:
        return valor.replace(tzinfo=timezone.utc)
    return valor.astimezone(timezone.utc)


DataHoraUTC = Annotated[datetime, AfterValidator(garantir_utc)]
