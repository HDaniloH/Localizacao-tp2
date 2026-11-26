"""Cadastro, consulta e geolocalização de ocorrências (US01 e US02).

Camadas:

* ``geo``, ``schemas``, ``filtros``, ``erros``: regras puras, sem banco.
* ``servico``: casos de uso; depende apenas das interfaces de ``portas``.
* ``repositorio_sql``: adaptadores SQLAlchemy/PostGIS sobre ``app.models``.
* ``rotas``: ``APIRouter`` FastAPI montado sobre o serviço.
"""
