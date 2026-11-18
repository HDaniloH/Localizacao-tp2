# Sistema de Registro e Acompanhamento de Ocorrências Urbanas

Projeto da disciplina **Técnicas de Programação 2 (2/2026)** — CIC / **Universidade de Brasília (UnB)**.

## Como Executar
1. Ativar ambiente: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
2. Subir banco PostGIS: docker compose up -d
3. Rodar API: uvicorn app.main:app --reload (Swagger em http://localhost:8000/docs)
4. Rodar testes e linters: flake8 app tests && black --check app tests && bandit -r app -ll && pytest --cov=app --cov-fail-under=80
5. Gerar documentação Sphinx: sphinx-build -b html docs/source docs/build

Consulte a modelagem detalhada e o diagrama DER em [docs/arquitetura_db.md](docs/arquitetura_db.md).
