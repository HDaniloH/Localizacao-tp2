# Guia da API — Autenticação

Backend em FastAPI sobre o PostgreSQL/PostGIS do projeto (`app/database.py`,
`app/models.py`). A documentação interativa (Swagger) fica em `/docs`.

## Como rodar

```bash
docker compose up -d                 # sobe o PostgreSQL + PostGIS
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m app.criar_admin "Admin" admin@unb.br Admin1234   # primeiro admin
uvicorn app.main:app --reload                             # http://localhost:8000/docs
```

As tabelas que faltarem são criadas ao subir a API (`create_all`, provisório
até o grupo adotar migrações). No Swagger, clique em **Authorize** e entre com
o e-mail (campo *username*) e a senha.

| Variável | Padrão | Para quê |
|---|---|---|
| `DATABASE_URL` | `postgresql://tp2_user:tp2_password@localhost:5432/ocorrencias_db` | Conexão com o banco |
| `SECRET_KEY` | chave de desenvolvimento | Assina os tokens. **Obrigatória em produção** |
| `JWT_EXPIRACAO_MIN` | `60` | Validade do token, em minutos |
| `BCRYPT_ROUNDS` | `12` | Custo do hash de senha |

## Testes e qualidade

Os mesmos passos do CI. Os testes usam o PostGIS do `docker compose`, e cada
teste recria as tabelas.

```bash
black --check app tests
flake8 app tests
bandit -r app
pytest --cov=app --cov-report=term-missing --cov-fail-under=80
```

## Endpoints

### Autenticação (`/auth`)
| Método | Rota | Quem | O que faz |
|---|---|---|---|
| POST | `/auth/registrar` | público | Cadastra usuário comum (ignora `is_admin` enviado) |
| POST | `/auth/login` | público | Formulário `username`/`password` → JWT Bearer |
| GET | `/auth/me` | logado | Dados do usuário do token |

### Usuários (`/usuarios`)
| Método | Rota | Quem | O que faz |
|---|---|---|---|
| GET | `/usuarios?ativo=` | admin | Lista usuários |
| POST | `/usuarios` | admin | Cria usuário (pode criar outro admin com `is_admin`) |
| GET | `/usuarios/{id}` | o próprio ou admin | Consulta |
| PATCH | `/usuarios/{id}` | o próprio ou admin | Altera; `is_admin`/`ativo` só admin |
| DELETE | `/usuarios/{id}` | admin | **Inativa** (exclusão lógica) |

## Decisões de projeto

- **Administrador:** é o campo `is_admin` do modelo `Usuario`. O cadastro
  público nunca cria admin; o primeiro vem do comando `criar_admin`.
- **Exclusão lógica:** nada é apagado. Usuários têm a coluna `ativo`
  (acrescentada ao modelo), para que ocorrências antigas continuem apontando
  para registros válidos.
- **Senha:** bcrypt; de 8 a 72 caracteres, com letra e número.
- **Login:** a mesma mensagem para e-mail inexistente e senha errada, com tempo
  de resposta parecido, para não revelar quais e-mails estão cadastrados.
- **Admin não pode remover o próprio acesso** (`is_admin` ou `ativo`), para o
  sistema não ficar sem administrador.
- **Datas em UTC**, com `Z` no final.
- **Camadas:** `api/routes` (HTTP) → `services` (regras) → `models` (ORM). Os
  serviços levantam exceções de `app/core/exceptions.py`, que o `main.py`
  converte em HTTP.

## Para quem cria rotas novas

```python
from app.api.deps import AdminAtual, DbSession, UsuarioAtual

@router.post("/ocorrencias")         # qualquer usuário logado
def registrar(dados: OcorrenciaCriar, db: DbSession, usuario: UsuarioAtual): ...

@router.delete("/admin/algo/{id}")   # só admin
def apagar(id: int, db: DbSession, _admin: AdminAtual): ...
```

Fixtures em `tests/conftest.py`: `client`, `db_session`, `cidadao`, `admin`,
`headers_cidadao`, `headers_admin`, `criar_usuario(...)` e a função
`headers_de(usuario)`.

## Pendências

- **mypy:** o `app/models.py` usa o estilo `Column(...)`, e o mypy acusa
  incompatibilidade de tipos nos serviços. Migrar os modelos para o estilo
  `Mapped[...]` do SQLAlchemy 2.0 resolve.

## Histórico de commits (TDD)

Cada funcionalidade tem um commit de teste falhando (`[RED]`) seguido do
commit que o faz passar (`[GREEN]`):

1. `chore`: dependências da autenticação e correção do `requirements.txt`
2. Teste 1 — hash bcrypt e JWT
3. Teste 2 — cadastro, login e `/auth/me`
4. Teste 3 — CRUD de usuários
5. Teste 4 — comando `criar_admin`
6. Teste 5 — datas em UTC
7. `docs`: este guia
