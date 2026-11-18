"""Testes unitários de hash de senha e JWT."""

from datetime import timedelta

import jwt

from app.core.config import settings
from app.core.security import (
    criar_token_acesso,
    decodificar_token,
    gerar_hash_senha,
    verificar_senha,
)


def test_hash_nao_guarda_senha_em_texto_puro():
    senha_hash = gerar_hash_senha("Senha123")
    assert senha_hash != "Senha123"
    assert senha_hash.startswith("$2")


def test_hash_da_mesma_senha_muda_a_cada_chamada():
    assert gerar_hash_senha("Senha123") != gerar_hash_senha("Senha123")


def test_verificar_senha_correta():
    assert verificar_senha("Senha123", gerar_hash_senha("Senha123"))


def test_verificar_senha_incorreta():
    assert not verificar_senha("Outra123", gerar_hash_senha("Senha123"))


def test_verificar_senha_com_hash_corrompido_retorna_falso():
    assert not verificar_senha("Senha123", "isso-nao-e-um-hash")


def test_token_valido_devolve_sujeito():
    token = criar_token_acesso("42")
    assert decodificar_token(token) == "42"


def test_token_expirado_e_rejeitado():
    token = criar_token_acesso("42", expira_em=timedelta(seconds=-1))
    assert decodificar_token(token) is None


def test_token_com_assinatura_errada_e_rejeitado():
    chave_errada = "outra-chave-com-tamanho-suficiente-32b"
    token = jwt.encode({"sub": "42"}, chave_errada, algorithm="HS256")
    assert decodificar_token(token) is None


def test_token_sem_sujeito_e_rejeitado():
    token = jwt.encode({"x": 1}, settings.secret_key, algorithm=settings.algoritmo_jwt)
    assert decodificar_token(token) is None


def test_token_malformado_e_rejeitado():
    assert decodificar_token("abc.def.ghi") is None
