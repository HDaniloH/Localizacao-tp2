"""Exceções de domínio, convertidas em respostas HTTP em ``app.main``."""


class ErroDominio(Exception):
    """Erro de regra de negócio.

    Attributes:
        status_code: Código HTTP correspondente.
        detalhe: Mensagem devolvida ao cliente.
    """

    status_code = 400

    def __init__(self, detalhe: str) -> None:
        super().__init__(detalhe)
        self.detalhe = detalhe


class RecursoNaoEncontrado(ErroDominio):
    """O recurso solicitado não existe."""

    status_code = 404


class Conflito(ErroDominio):
    """A operação viola uma restrição de unicidade."""

    status_code = 409


class OperacaoNaoPermitida(ErroDominio):
    """O usuário autenticado não pode executar a operação."""

    status_code = 403


class RequisicaoInvalida(ErroDominio):
    """A operação é inválida no estado atual do sistema."""

    status_code = 400
