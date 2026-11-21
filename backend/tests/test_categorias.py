"""Testes da US05 — Painel Administrativo e Gestão de Categorias.

Critérios de aceitação cobertos:

* CA1 — Acesso autenticado via perfil com privilégios de administrador
  (``is_admin``).
* CA2 — Restrição a operações não autorizadas.
* Funcional — Cadastrar, alterar e inativar categorias de ocorrências.
"""

import pytest

URL_ADMIN = "/admin/categorias"
URL_PUBLICA = "/categorias"


# ---------- CA1/CA2: controle de acesso ----------


@pytest.mark.parametrize(
    ("metodo", "url", "corpo"),
    [
        ("get", URL_ADMIN, None),
        ("post", URL_ADMIN, {"nome": "Buraco"}),
        ("get", f"{URL_ADMIN}/1", None),
        ("patch", f"{URL_ADMIN}/1", {"nome": "Outro"}),
        ("patch", f"{URL_ADMIN}/1/inativar", None),
        ("patch", f"{URL_ADMIN}/1/reativar", None),
    ],
)
def test_us05_rotas_admin_exigem_autenticacao(client, metodo, url, corpo):
    resp = client.request(metodo, url, json=corpo)
    assert resp.status_code == 401


@pytest.mark.parametrize(
    ("metodo", "url", "corpo"),
    [
        ("get", URL_ADMIN, None),
        ("post", URL_ADMIN, {"nome": "Buraco"}),
        ("get", f"{URL_ADMIN}/1", None),
        ("patch", f"{URL_ADMIN}/1", {"nome": "Outro"}),
        ("patch", f"{URL_ADMIN}/1/inativar", None),
        ("patch", f"{URL_ADMIN}/1/reativar", None),
    ],
)
def test_us05_cidadao_nao_acessa_rotas_admin(
    client, headers_cidadao, criar_categoria, metodo, url, corpo
):
    criar_categoria("Iluminação")
    resp = client.request(metodo, url, json=corpo, headers=headers_cidadao)
    assert resp.status_code == 403


# ---------- Cadastrar ----------


def test_us05_admin_cadastra_categoria(client, headers_admin):
    resp = client.post(
        URL_ADMIN,
        json={"nome": "Buraco na via", "descricao": "Asfalto danificado"},
        headers=headers_admin,
    )
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["nome"] == "Buraco na via"
    assert corpo["descricao"] == "Asfalto danificado"
    assert corpo["ativa"] is True
    assert isinstance(corpo["id"], int)


def test_us05_cadastro_remove_espacos_das_pontas(client, headers_admin):
    resp = client.post(URL_ADMIN, json={"nome": "  Lixo  "}, headers=headers_admin)
    assert resp.json()["nome"] == "Lixo"


def test_us05_descricao_e_opcional(client, headers_admin):
    resp = client.post(URL_ADMIN, json={"nome": "Lixo"}, headers=headers_admin)
    assert resp.status_code == 201
    assert resp.json()["descricao"] is None


@pytest.mark.parametrize("nome", ["Buraco na via", "BURACO NA VIA", " buraco na via "])
def test_us05_nao_permite_nome_duplicado(client, headers_admin, criar_categoria, nome):
    criar_categoria("Buraco na via")
    resp = client.post(URL_ADMIN, json={"nome": nome}, headers=headers_admin)
    assert resp.status_code == 409


def test_us05_nome_duplicado_de_categoria_inativa_tambem_conflita(
    client, headers_admin, criar_categoria
):
    criar_categoria("Buraco na via", ativa=False)
    resp = client.post(URL_ADMIN, json={"nome": "Buraco na via"}, headers=headers_admin)
    assert resp.status_code == 409


@pytest.mark.parametrize(
    "corpo",
    [
        {},
        {"nome": ""},
        {"nome": "A"},
        {"nome": "x" * 81},
        {"nome": "Ok", "descricao": "d" * 256},
    ],
)
def test_us05_cadastro_valida_campos(client, headers_admin, corpo):
    resp = client.post(URL_ADMIN, json=corpo, headers=headers_admin)
    assert resp.status_code == 422


# ---------- Listar / consultar ----------


def test_us05_admin_lista_ativas_e_inativas(client, headers_admin, criar_categoria):
    criar_categoria("Ativa")
    criar_categoria("Inativa", ativa=False)
    resp = client.get(URL_ADMIN, headers=headers_admin)
    assert {c["nome"] for c in resp.json()} == {"Ativa", "Inativa"}


def test_us05_admin_filtra_por_situacao(client, headers_admin, criar_categoria):
    criar_categoria("Ativa")
    criar_categoria("Inativa", ativa=False)
    resp = client.get(f"{URL_ADMIN}?ativa=false", headers=headers_admin)
    assert [c["nome"] for c in resp.json()] == ["Inativa"]


def test_us05_listagem_vem_em_ordem_alfabetica(client, headers_admin, criar_categoria):
    for nome in ["Poda de árvore", "Buraco", "Iluminação"]:
        criar_categoria(nome)
    resp = client.get(URL_ADMIN, headers=headers_admin)
    assert [c["nome"] for c in resp.json()] == [
        "Buraco",
        "Iluminação",
        "Poda de árvore",
    ]


def test_us05_admin_consulta_categoria_inativa(client, headers_admin, criar_categoria):
    cat = criar_categoria("Inativa", ativa=False)
    resp = client.get(f"{URL_ADMIN}/{cat.id}", headers=headers_admin)
    assert resp.status_code == 200


def test_us05_consultar_inexistente_retorna_404(client, headers_admin):
    assert client.get(f"{URL_ADMIN}/9999", headers=headers_admin).status_code == 404


# ---------- Rotas públicas (usadas pelo formulário da US01) ----------


def test_lista_publica_mostra_so_ativas(client, criar_categoria):
    criar_categoria("Ativa")
    criar_categoria("Inativa", ativa=False)
    resp = client.get(URL_PUBLICA)
    assert resp.status_code == 200
    assert [c["nome"] for c in resp.json()] == ["Ativa"]


def test_consulta_publica_de_categoria_ativa(client, criar_categoria):
    cat = criar_categoria("Ativa")
    assert client.get(f"{URL_PUBLICA}/{cat.id}").status_code == 200


def test_consulta_publica_de_categoria_inativa_retorna_404(client, criar_categoria):
    cat = criar_categoria("Inativa", ativa=False)
    assert client.get(f"{URL_PUBLICA}/{cat.id}").status_code == 404


# ---------- Alterar ----------


def test_us05_admin_altera_nome_e_descricao(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco", descricao="Antiga")
    resp = client.patch(
        f"{URL_ADMIN}/{cat.id}",
        json={"nome": "Buraco na via", "descricao": "Nova"},
        headers=headers_admin,
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "Buraco na via"
    assert resp.json()["descricao"] == "Nova"


def test_us05_alteracao_parcial_mantem_demais_campos(
    client, headers_admin, criar_categoria
):
    cat = criar_categoria("Buraco", descricao="Mantida")
    resp = client.patch(
        f"{URL_ADMIN}/{cat.id}", json={"nome": "Cratera"}, headers=headers_admin
    )
    assert resp.json()["descricao"] == "Mantida"


def test_us05_alterar_para_nome_de_outra_categoria_retorna_409(
    client, headers_admin, criar_categoria
):
    criar_categoria("Buraco")
    cat = criar_categoria("Lixo")
    resp = client.patch(
        f"{URL_ADMIN}/{cat.id}", json={"nome": "buraco"}, headers=headers_admin
    )
    assert resp.status_code == 409


def test_us05_alterar_mantendo_o_proprio_nome_e_permitido(
    client, headers_admin, criar_categoria
):
    cat = criar_categoria("Buraco")
    resp = client.patch(
        f"{URL_ADMIN}/{cat.id}",
        json={"nome": "BURACO", "descricao": "x"},
        headers=headers_admin,
    )
    assert resp.status_code == 200
    assert resp.json()["nome"] == "BURACO"


def test_us05_alterar_inexistente_retorna_404(client, headers_admin):
    resp = client.patch(
        f"{URL_ADMIN}/9999", json={"nome": "Abc"}, headers=headers_admin
    )
    assert resp.status_code == 404


def test_us05_alterar_com_nome_invalido_retorna_422(
    client, headers_admin, criar_categoria
):
    cat = criar_categoria("Buraco")
    resp = client.patch(
        f"{URL_ADMIN}/{cat.id}", json={"nome": ""}, headers=headers_admin
    )
    assert resp.status_code == 422


# ---------- Inativar / reativar ----------


def test_us05_admin_inativa_categoria(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco")
    resp = client.patch(f"{URL_ADMIN}/{cat.id}/inativar", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json()["ativa"] is False


def test_us05_categoria_inativada_some_da_lista_publica(
    client, headers_admin, criar_categoria
):
    cat = criar_categoria("Buraco")
    client.patch(f"{URL_ADMIN}/{cat.id}/inativar", headers=headers_admin)
    assert client.get(URL_PUBLICA).json() == []


def test_us05_inativar_nao_apaga_a_categoria(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco")
    client.patch(f"{URL_ADMIN}/{cat.id}/inativar", headers=headers_admin)
    resp = client.get(f"{URL_ADMIN}/{cat.id}", headers=headers_admin)
    assert resp.status_code == 200


def test_us05_inativar_duas_vezes_e_idempotente(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco", ativa=False)
    resp = client.patch(f"{URL_ADMIN}/{cat.id}/inativar", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json()["ativa"] is False


def test_us05_admin_reativa_categoria(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco", ativa=False)
    resp = client.patch(f"{URL_ADMIN}/{cat.id}/reativar", headers=headers_admin)
    assert resp.status_code == 200
    assert resp.json()["ativa"] is True
    assert [c["nome"] for c in client.get(URL_PUBLICA).json()] == ["Buraco"]


@pytest.mark.parametrize("acao", ["inativar", "reativar"])
def test_us05_mudar_situacao_de_inexistente_retorna_404(client, headers_admin, acao):
    resp = client.patch(f"{URL_ADMIN}/9999/{acao}", headers=headers_admin)
    assert resp.status_code == 404


def test_us05_nao_existe_exclusao_fisica(client, headers_admin, criar_categoria):
    cat = criar_categoria("Buraco")
    resp = client.delete(f"{URL_ADMIN}/{cat.id}", headers=headers_admin)
    assert resp.status_code == 405
