"""Testes do CRUD de usuários (/usuarios)."""

from tests.conftest import SENHA_PADRAO

# ---------- Listar ----------


def test_admin_lista_usuarios(client, headers_admin, cidadao):
    resp = client.get("/usuarios", headers=headers_admin)
    assert resp.status_code == 200
    emails = {u["email"] for u in resp.json()}
    assert {"admin@unb.br", "cidadao@aluno.unb.br"} <= emails


def test_admin_filtra_usuarios_por_ativo(client, headers_admin, criar_usuario):
    criar_usuario(email="inativo@unb.br", ativo=False)
    resp = client.get("/usuarios?ativo=false", headers=headers_admin)
    assert [u["email"] for u in resp.json()] == ["inativo@unb.br"]


def test_cidadao_nao_lista_usuarios(client, headers_cidadao):
    assert client.get("/usuarios", headers=headers_cidadao).status_code == 403


def test_listar_sem_token_retorna_401(client):
    assert client.get("/usuarios").status_code == 401


# ---------- Criar (admin) ----------


def test_admin_cria_outro_admin(client, headers_admin):
    dados = {
        "nome": "Nova Admin",
        "email": "nova@unb.br",
        "senha": "Admin1234",
        "is_admin": True,
    }
    resp = client.post("/usuarios", json=dados, headers=headers_admin)
    assert resp.status_code == 201
    assert resp.json()["is_admin"] is True


def test_admin_cria_usuario_com_email_repetido_retorna_409(
    client, headers_admin, cidadao
):
    dados = {"nome": "X Y", "email": cidadao.email, "senha": "Senha1234"}
    resp = client.post("/usuarios", json=dados, headers=headers_admin)
    assert resp.status_code == 409


def test_cidadao_nao_cria_usuario_pelo_painel(client, headers_cidadao):
    dados = {"nome": "X Y", "email": "x@unb.br", "senha": "Senha1234"}
    resp = client.post("/usuarios", json=dados, headers=headers_cidadao)
    assert resp.status_code == 403


# ---------- Consultar ----------


def test_usuario_consulta_a_si_mesmo(client, cidadao, headers_cidadao):
    resp = client.get(f"/usuarios/{cidadao.id}", headers=headers_cidadao)
    assert resp.status_code == 200


def test_cidadao_nao_consulta_outro_usuario(client, admin, headers_cidadao):
    resp = client.get(f"/usuarios/{admin.id}", headers=headers_cidadao)
    assert resp.status_code == 403


def test_admin_consulta_qualquer_usuario(client, cidadao, headers_admin):
    resp = client.get(f"/usuarios/{cidadao.id}", headers=headers_admin)
    assert resp.json()["email"] == cidadao.email


def test_consultar_usuario_inexistente_retorna_404(client, headers_admin):
    assert client.get("/usuarios/9999", headers=headers_admin).status_code == 404


# ---------- Alterar ----------


def test_usuario_altera_o_proprio_nome(client, cidadao, headers_cidadao):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"nome": "Nome Novo"},
        headers=headers_cidadao,
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Nome Novo"


def test_usuario_troca_senha_e_consegue_logar_com_a_nova(
    client, cidadao, headers_cidadao
):
    client.patch(
        f"/usuarios/{cidadao.id}",
        json={"senha": "NovaSenha9"},
        headers=headers_cidadao,
    )
    antiga = client.post(
        "/auth/login",
        data={"username": cidadao.email, "password": SENHA_PADRAO},
    )
    nova = client.post(
        "/auth/login",
        data={"username": cidadao.email, "password": "NovaSenha9"},
    )
    assert antiga.status_code == 401
    assert nova.status_code == 200


def test_cidadao_nao_pode_se_promover_a_admin(client, cidadao, headers_cidadao):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"is_admin": True},
        headers=headers_cidadao,
    )
    assert resp.status_code == 403


def test_cidadao_nao_pode_se_reativar_ou_alterar_ativo(
    client, cidadao, headers_cidadao
):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"ativo": True},
        headers=headers_cidadao,
    )
    assert resp.status_code == 403


def test_cidadao_nao_altera_outro_usuario(client, admin, headers_cidadao):
    resp = client.patch(
        f"/usuarios/{admin.id}",
        json={"nome": "Hackeado"},
        headers=headers_cidadao,
    )
    assert resp.status_code == 403


def test_admin_promove_usuario_a_admin(client, cidadao, headers_admin):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"is_admin": True},
        headers=headers_admin,
    )
    assert resp.json()["is_admin"] is True


def test_alterar_para_email_ja_usado_retorna_409(
    client, cidadao, admin, headers_cidadao
):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"email": admin.email},
        headers=headers_cidadao,
    )
    assert resp.status_code == 409


def test_alterar_para_o_proprio_email_e_permitido(client, cidadao, headers_cidadao):
    resp = client.patch(
        f"/usuarios/{cidadao.id}",
        json={"email": cidadao.email.upper()},
        headers=headers_cidadao,
    )
    assert resp.status_code == 200


def test_admin_nao_pode_remover_o_proprio_acesso_de_admin(client, admin, headers_admin):
    resp = client.patch(
        f"/usuarios/{admin.id}",
        json={"is_admin": False},
        headers=headers_admin,
    )
    assert resp.status_code == 400


def test_alterar_usuario_inexistente_retorna_404(client, headers_admin):
    resp = client.patch("/usuarios/9999", json={"nome": "Abc"}, headers=headers_admin)
    assert resp.status_code == 404


# ---------- Inativar ----------


def test_admin_inativa_usuario_e_ele_nao_loga_mais(client, cidadao, headers_admin):
    resp = client.delete(f"/usuarios/{cidadao.id}", headers=headers_admin)
    assert resp.status_code == 204
    login = client.post(
        "/auth/login",
        data={"username": cidadao.email, "password": SENHA_PADRAO},
    )
    assert login.status_code == 403


def test_inativar_nao_apaga_o_registro(client, cidadao, headers_admin):
    client.delete(f"/usuarios/{cidadao.id}", headers=headers_admin)
    resp = client.get(f"/usuarios/{cidadao.id}", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json()["ativo"] is False


def test_admin_nao_pode_inativar_a_si_mesmo(client, admin, headers_admin):
    resp = client.delete(f"/usuarios/{admin.id}", headers=headers_admin)
    assert resp.status_code == 400


def test_cidadao_nao_inativa_usuarios(client, admin, headers_cidadao):
    resp = client.delete(f"/usuarios/{admin.id}", headers=headers_cidadao)
    assert resp.status_code == 403


def test_inativar_usuario_inexistente_retorna_404(client, headers_admin):
    assert client.delete("/usuarios/9999", headers=headers_admin).status_code == 404
