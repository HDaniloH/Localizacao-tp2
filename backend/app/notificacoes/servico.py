from sqlalchemy.orm import Session

from app.models import InscricaoNotificacao, LogEvento, Ocorrencia, StatusOcorrencia


class ServicoNotificacoes:
    def __init__(self, db: Session):
        self.db = db

    def inscrever_usuario(
        self, usuario_id: int, ocorrencia_id: int
    ) -> InscricaoNotificacao:
        ocorrencia = (
            self.db.query(Ocorrencia)
            .filter(Ocorrencia.id == ocorrencia_id)
            .first()
        )
        if not ocorrencia:
            raise ValueError("Ocorrência não encontrada")

        existente = (
            self.db.query(InscricaoNotificacao)
            .filter(
                InscricaoNotificacao.usuario_id == usuario_id,
                InscricaoNotificacao.ocorrencia_id == ocorrencia_id,
            )
            .first()
        )

        if existente:
            return existente

        inscricao = InscricaoNotificacao(
            usuario_id=usuario_id, ocorrencia_id=ocorrencia_id
        )
        self.db.add(inscricao)
        self.db.commit()
        self.db.refresh(inscricao)
        return inscricao

    def registrar_mudanca_status(
        self,
        ocorrencia_id: int,
        status_anterior: StatusOcorrencia | str | None,
        status_novo: StatusOcorrencia | str,
    ) -> LogEvento:
        log = LogEvento(
            ocorrencia_id=ocorrencia_id,
            status_anterior=status_anterior,
            status_novo=status_novo,
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def listar_logs_ocorrencia(self, ocorrencia_id: int) -> list[LogEvento]:
        return (
            self.db.query(LogEvento)
            .filter(LogEvento.ocorrencia_id == ocorrencia_id)
            .order_by(LogEvento.registrado_em.desc())
            .all()
        )