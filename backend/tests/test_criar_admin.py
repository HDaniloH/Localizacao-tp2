"""Testes do comando que cria o primeiro administrador."""

import pytest
from pydantic import ValidationError

from app import criar_admin
from app.core.exceptions import Conflito


def test_cria_usuario_administrador(db_session):
    admin = criar_admin.criar_admin_inicial(
        db_session, "Admin Raiz", "raiz@unb.br", "Admin1234"
    )
    assert admin.is_admin is True
    assert admin.ativo is True


def test_valida_senha_fraca(db_session):
    with pytest.raises(ValidationError):
        criar_admin.criar_admin_inicial(db_session, "Admin", "a@unb.br", "123")


def test_nao_duplica_email(db_session):
    criar_admin.criar_admin_inicial(db_session, "Admin", "a@unb.br", "Admin1234")
    with pytest.raises(Conflito):
        criar_admin.criar_admin_inicial(db_session, "Outro", "A@unb.br", "Admin1234")


def test_main_sem_argumentos_mostra_ajuda(capsys):
    assert criar_admin.main([]) == 1
    assert "Uso" in capsys.readouterr().out


def test_main_cria_admin(monkeypatch, db_session, capsys):
    monkeypatch.setattr(criar_admin, "SessionLocal", lambda: db_session)
    codigo = criar_admin.main(["Admin Raiz", "raiz@unb.br", "Admin1234"])
    assert codigo == 0
    assert "raiz@unb.br" in capsys.readouterr().out
