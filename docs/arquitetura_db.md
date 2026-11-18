# Arquitetura e Modelagem do Banco de Dados

## 1. Visão Geral da Arquitetura
- **Back-end:** API RESTful em Python 3.11+ (FastAPI), SQLAlchemy e GeoAlchemy2.
- **Banco de Dados:** PostgreSQL 16 + PostGIS 3.4 (SRID 4326).
- **Front-end:** React com Leaflet.js / OpenStreetMap.

## 2. Diagrama Entidade-Relacionamento (DER)

```mermaid
erDiagram
    USUARIOS ||--o{ OCORRENCIAS : registra
    CATEGORIAS ||--o{ OCORRENCIAS : classifica
    OCORRENCIAS ||--o{ LOGS_EVENTOS : gera
    USUARIOS ||--o{ INSCRICOES_NOTIFICACAO : assina
    OCORRENCIAS ||--o{ INSCRICOES_NOTIFICACAO : monitora
    CATEGORIAS ||--o{ INSCRICOES_NOTIFICACAO : filtra
    USUARIOS ||--o{ LOGS_PESQUISA : realiza

    USUARIOS {
        int id PK
        string nome
        string email UK
        string senha_hash
        boolean is_admin
        datetime criado_em
    }
    CATEGORIAS {
        int id PK
        string nome UK
        string descricao
        boolean ativa
    }
    PERIMETROS_AUTORIZADOS {
        int id PK
        string nome_regiao UK
        geometry area "POLYGON SRID 4326"
    }
    OCORRENCIAS {
        int id PK
        string titulo
        text descricao
        enum status "REGISTRADO | EM_ANALISE | RESOLVIDO"
        geometry localizacao "POINT SRID 4326"
        string foto_url
        int usuario_id FK
        int categoria_id FK
        datetime criado_em
        datetime atualizado_em
    }
    INSCRICOES_NOTIFICACAO {
        int id PK
        int usuario_id FK
        int ocorrencia_id FK
        int categoria_id FK
        geometry centro_alerta "POINT SRID 4326"
        float raio_metros
    }
    LOGS_EVENTOS {
        int id PK
        int ocorrencia_id FK
        enum status_anterior
        enum status_novo
        datetime registrado_em
    }
    LOGS_PESQUISA {
        int id PK
        int usuario_id FK
        string termo_buscado
        string regiao_filtrada
        datetime pesquisado_em
    }
```

## 3. Rastreabilidade (US01 a US06)
- **US01 / US02:** Tabela ocorrencias armazena coordenadas GPS (POINT) e status.
- **US03:** Tabelas inscricoes_notificacao e logs_eventos gerenciam assinaturas e auditoria de status.
- **US04 / US06:** Consultas sobre ocorrencias e logs_pesquisa geram estatísticas e relatórios gerenciais.
- **US05:** Tabelas categorias e perimetros_autorizados (POLYGON) controlam tipos e áreas válidas.
