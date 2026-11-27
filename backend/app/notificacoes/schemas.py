from datetime import datetime
from pydantic import BaseModel, ConfigDict, computed_field

from app.models import StatusOcorrencia


class InscricaoNotificacaoCreate(BaseModel):
    ocorrencia_id: int


class InscricaoNotificacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    usuario_id: int
    ocorrencia_id: int


class LogEventoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ocorrencia_id: int
    status_anterior: StatusOcorrencia | None
    status_novo: StatusOcorrencia
    registrado_em: datetime

    @computed_field
    @property
    def mensagem(self) -> str:
        anterior = self.status_anterior.value if self.status_anterior else "Nenhum"
        return (
            f"Ocorrência #{self.ocorrencia_id} alterou status de "
            f"'{anterior}' para '{self.status_novo.value}'"
        )