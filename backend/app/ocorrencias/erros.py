"""Erros de domínio do módulo de ocorrências.

Cada erro traz um ``codigo`` estável e o ``status_http`` correspondente, usados
pelas rotas para montar a resposta ``{"detail": {"codigo", "mensagem"}}``.
"""


class ErroOcorrencia(Exception):
    """Base dos erros de regra de negócio deste módulo."""

    codigo = "erro_ocorrencia"
    status_http = 400


class NaoAutenticado(ErroOcorrencia):
    """Cadastro tentado sem usuário autenticado."""

    codigo = "nao_autenticado"
    status_http = 401


class CategoriaInexistente(ErroOcorrencia):
    """A categoria informada não existe."""

    codigo = "categoria_inexistente"
    status_http = 422


class CategoriaInativa(ErroOcorrencia):
    """A categoria foi inativada pelo administrador."""

    codigo = "categoria_inativa"
    status_http = 422


class ForaDaAreaAutorizada(ErroOcorrencia):
    """O ponto está fora dos perímetros autorizados."""

    codigo = "fora_da_area_autorizada"
    status_http = 422


class OcorrenciaNaoEncontrada(ErroOcorrencia):
    """Nenhuma ocorrência com o identificador solicitado."""

    codigo = "ocorrencia_nao_encontrada"
    status_http = 404
