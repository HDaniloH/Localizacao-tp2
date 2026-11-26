"""Doubles das fronteiras para os testes de unidade do serviço."""

from datetime import timedelta

from app.ocorrencias.portas import Pagina, SituacaoCategoria
from app.ocorrencias.schemas import Ocorrencia


class CatalogoFake:
    """Substitui o catálogo de categorias (US05)."""

    def __init__(self, ativas=(1, 2), inativas=(9,)):
        self.ativas = set(ativas)
        self.inativas = set(inativas)

    def situacao(self, categoria_id):
        if categoria_id in self.ativas:
            return SituacaoCategoria.ATIVA
        if categoria_id in self.inativas:
            return SituacaoCategoria.INATIVA
        return SituacaoCategoria.INEXISTENTE


class AreaFake:
    """Substitui a política de perímetros autorizados (US05)."""

    def __init__(self, autoriza=True):
        self.autoriza = autoriza
        self.consultados = []

    def ponto_autorizado(self, ponto):
        self.consultados.append(ponto)
        return self.autoriza


class RepositorioFake:
    """Guarda em memória; a consulta real é testada no PostGIS."""

    def __init__(self):
        self.dados = {}
        self.filtros = []

    def adicionar(self, nova):
        oc = Ocorrencia(id=len(self.dados) + 1, foto_url=None, **vars_de(nova))
        self.dados[oc.id] = oc
        return oc

    def obter(self, id_):
        return self.dados.get(id_)

    def listar(self, filtro):
        self.filtros.append(filtro)
        return Pagina(itens=list(self.dados.values()), proximo_offset=None)


def vars_de(nova):
    return {
        campo: getattr(nova, campo)
        for campo in (
            "usuario_id",
            "categoria_id",
            "titulo",
            "descricao",
            "ponto",
            "status",
            "criado_em",
        )
    }


class RelogioFake:
    """Relógio controlável."""

    def __init__(self, inicio):
        self.agora = inicio

    def __call__(self):
        return self.agora

    def avancar(self, **kwargs):
        self.agora += timedelta(**kwargs)
