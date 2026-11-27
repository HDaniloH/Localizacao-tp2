from app.models import StatusOcorrencia
from app.notificacoes.schemas import LogEventoResponse
from app.notificacoes.servico import ServicoNotificacoes


def test_criar_inscricao_notificacao(db_session, usuario_teste, ocorrencia_teste):
    servico = ServicoNotificacoes(db_session)

    inscricao = servico.inscrever_usuario(
        usuario_id=usuario_teste.id, ocorrencia_id=ocorrencia_teste.id
    )

    assert inscricao.id is not None
    assert inscricao.usuario_id == usuario_teste.id
    assert inscricao.ocorrencia_id == ocorrencia_teste.id


def test_registrar_log_mudanca_status(db_session, ocorrencia_teste):
    servico = ServicoNotificacoes(db_session)

    log = servico.registrar_mudanca_status(
        ocorrencia_id=ocorrencia_teste.id,
        status_anterior=StatusOcorrencia.REGISTRADO,
        status_novo=StatusOcorrencia.EM_ANALISE,
    )

    assert log.id is not None
    assert log.status_novo == StatusOcorrencia.EM_ANALISE
    resposta = LogEventoResponse.model_validate(log)
    assert "EM_ANALISE" in resposta.mensagem