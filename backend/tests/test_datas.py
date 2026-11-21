"""As datas devolvidas pela API devem vir em UTC, com o fuso explícito."""

from datetime import datetime, timedelta, timezone

from app.schemas.comum import garantir_utc


def test_data_sem_fuso_e_marcada_como_utc():
    data = garantir_utc(datetime(2026, 11, 17, 17, 45))
    assert data.tzinfo == timezone.utc
    assert data.hour == 17


def test_data_em_outro_fuso_e_convertida_para_utc():
    brasilia = timezone(timedelta(hours=-3))
    data = garantir_utc(datetime(2026, 11, 17, 14, 45, tzinfo=brasilia))
    assert data.hour == 17
    assert data.tzinfo == timezone.utc


def test_usuario_sai_com_sufixo_z(client):
    resp = client.post(
        "/auth/registrar",
        json={"nome": "Ana", "email": "ana@unb.br", "senha": "Senha123"},
    )
    assert resp.json()["criado_em"].endswith("Z")
