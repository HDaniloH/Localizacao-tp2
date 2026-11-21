"""Testes de cadastro público, login e usuário autenticado (/auth)."""

import jwt

from app.core.config import settings
from app.core.security import criar_token_acesso
from tests.conftest import SENHA_PADRAO, headers_de

DADOS_CADASTRO = {
    "nome": "Maria Silva",
    "email": "maria@aluno.unb.br",
    "senha": "Segura123",
}


def fazer_login(client, email, senha):
    return client.post("/auth/login", data={"username": email, "password": senha})


# ---------- Cadastro ----------


def test_cadastro_cria_usuario_comum_ativo(client):
    resp = client.post("/auth/registrar", json=DADOS_CADASTRO)
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["email"] == "maria@aluno.unb.br"
    assert corpo["is_admin"] is False
    assert corpo["ativo"] is True
    assert "senha" not in corpo and "senha_hash" not in corpo


def test_cadastro_ignora_tentativa_de_virar_admin(client):
    dados = {**DADOS_CADASTRO, "is_admin": True}
    resp = client.post("/auth/registrar", json=dados)
    assert resp.status_code == 201
    assert resp.json()["is_admin"] is False


def test_cadastro_normaliza_email_para_minusculas(client):
    dados = {**DADOS_CADASTRO, "email": "Maria@Aluno.UNB.br"}
    resp = client.post("/auth/registrar", json=dados)
    assert resp.json()["email"] == "maria@aluno.unb.br"


def test_cadastro_com_email_repetido_retorna_409(client):
    client.post("/auth/registrar", json=DADOS_CADASTRO)
    dados = {**DADOS_CADASTRO, "email": "MARIA@aluno.unb.br"}
    resp = client.post("/auth/registrar", json=dados)
    assert resp.status_code == 409


def test_cadastro_com_email_invalido_retorna_422(client):
    dados = {**DADOS_CADASTRO, "email": "nao-e-email"}
    assert client.post("/auth/registrar", json=dados).status_code == 422


def test_cadastro_com_senha_curta_retorna_422(client):
    dados = {**DADOS_CADASTRO, "senha": "Ab1"}
    assert client.post("/auth/registrar", json=dados).status_code == 422


def test_cadastro_com_senha_sem_numero_retorna_422(client):
    dados = {**DADOS_CADASTRO, "senha": "SomenteLetras"}
    assert client.post("/auth/registrar", json=dados).status_code == 422


def test_cadastro_com_senha_sem_letra_retorna_422(client):
    dados = {**DADOS_CADASTRO, "senha": "12345678"}
    assert client.post("/auth/registrar", json=dados).status_code == 422


def test_cadastro_sem_nome_retorna_422(client):
    dados = {k: v for k, v in DADOS_CADASTRO.items() if k != "nome"}
    assert client.post("/auth/registrar", json=dados).status_code == 422


# ---------- Login ----------


def test_login_com_credenciais_corretas_devolve_token(client, cidadao):
    resp = fazer_login(client, cidadao.email, SENHA_PADRAO)
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["token_type"] == "bearer"
    payload = jwt.decode(
        corpo["access_token"],
        settings.secret_key,
        algorithms=[settings.algoritmo_jwt],
    )
    assert payload["sub"] == str(cidadao.id)


def test_login_aceita_email_com_maiusculas(client, cidadao):
    resp = fazer_login(client, cidadao.email.upper(), SENHA_PADRAO)
    assert resp.status_code == 200


def test_login_com_senha_errada_retorna_401(client, cidadao):
    resp = fazer_login(client, cidadao.email, "SenhaErrada1")
    assert resp.status_code == 401


def test_login_com_email_inexistente_retorna_401_com_mesma_mensagem(client, cidadao):
    errada = fazer_login(client, cidadao.email, "SenhaErrada1")
    inexistente = fazer_login(client, "ninguem@unb.br", "SenhaErrada1")
    assert inexistente.status_code == 401
    # Não revela se o e-mail existe ou não.
    assert inexistente.json() == errada.json()


def test_login_de_usuario_inativo_retorna_403(client, criar_usuario):
    usuario = criar_usuario(ativo=False)
    resp = fazer_login(client, usuario.email, SENHA_PADRAO)
    assert resp.status_code == 403


# ---------- /auth/me ----------


def test_me_devolve_usuario_do_token(client, cidadao, headers_cidadao):
    resp = client.get("/auth/me", headers=headers_cidadao)
    assert resp.status_code == 200
    assert resp.json()["id"] == cidadao.id


def test_me_sem_token_retorna_401(client):
    assert client.get("/auth/me").status_code == 401


def test_me_com_token_invalido_retorna_401(client):
    resp = client.get("/auth/me", headers={"Authorization": "Bearer lixo"})
    assert resp.status_code == 401


def test_me_com_sujeito_nao_numerico_retorna_401(client):
    token = criar_token_acesso("abc")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_me_com_usuario_inexistente_retorna_401(client):
    token = criar_token_acesso("9999")
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401


def test_token_de_usuario_inativado_deixa_de_valer(client, criar_usuario, db_session):
    usuario = criar_usuario()
    headers = headers_de(usuario)
    usuario.ativo = False
    db_session.commit()
    assert client.get("/auth/me", headers=headers).status_code == 401


def test_fluxo_completo_cadastro_login_me(client):
    client.post("/auth/registrar", json=DADOS_CADASTRO)
    token = fazer_login(
        client, DADOS_CADASTRO["email"], DADOS_CADASTRO["senha"]
    ).json()["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.json()["nome"] == "Maria Silva"
