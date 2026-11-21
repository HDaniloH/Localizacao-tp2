# Sistema de Registro e Acompanhamento de Ocorrências Urbanas

Projeto da disciplina **Técnicas de Programação 2 (2/2026)** — CIC / **Universidade de Brasília (UnB)**.

## Como Executar

### Backend
1. Entrar na pasta e ativar ambiente: `cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt`
2. Subir banco PostGIS (na raiz do projeto): `docker compose up -d`
3. Rodar API (em `backend/`): `uvicorn app.main:app --reload` (Swagger em http://localhost:8000/docs)
4. Rodar testes e linters (em `backend/`): `flake8 app tests && black --check app tests && bandit -r app -ll && pytest --cov=app --cov-fail-under=80`
5. Gerar documentação Sphinx (na raiz): `sphinx-build -b html docs/source docs/build`

### Frontend
1. Entrar na pasta e instalar dependências: `cd frontend && npm install`
2. Rodar servidor de desenvolvimento: `npm run dev`

Consulte a modelagem detalhada e o diagrama DER em [docs/arquitetura_db.md](docs/arquitetura_db.md).
