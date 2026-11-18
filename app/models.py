"""Modelos ORM e geoespaciais do sistema de ocorrências urbanas."""

from datetime import datetime, timezone
import enum
from geoalchemy2 import Geometry
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from app.database import Base


class StatusOcorrencia(str, enum.Enum):
    """Estados possíveis no ciclo de vida de uma ocorrência."""

    REGISTRADO = "REGISTRADO"
    EM_ANALISE = "EM_ANALISE"
    RESOLVIDO = "RESOLVIDO"


class Usuario(Base):
    """Representa um cidadão ou administrador cadastrado no sistema."""

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False)
    email = Column(String(150), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    criado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    ocorrencias = relationship("Ocorrencia", back_populates="autor")


class Categoria(Base):
    """Categorias de ocorrências gerenciadas pelo administrador (US05)."""

    __tablename__ = "categorias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(80), unique=True, nullable=False)
    descricao = Column(String(255), nullable=True)
    ativa = Column(Boolean, default=True, nullable=False)

    ocorrencias = relationship("Ocorrencia", back_populates="categoria")


class PerimetroAutorizado(Base):
    """Polígonos geográficos autorizados para registro de chamados (US05)."""

    __tablename__ = "perimetros_autorizados"

    id = Column(Integer, primary_key=True, index=True)
    nome_regiao = Column(String(100), unique=True, nullable=False)
    area = Column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)


class Ocorrencia(Base):
    """Registro georreferenciado de incidente urbano (US01/US02)."""

    __tablename__ = "ocorrencias"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String(120), nullable=False)
    descricao = Column(Text, nullable=False)
    status = Column(
        Enum(StatusOcorrencia),
        default=StatusOcorrencia.REGISTRADO,
        nullable=False,
    )
    localizacao = Column(Geometry(geometry_type="POINT", srid=4326), nullable=False)
    foto_url = Column(String(255), nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)
    criado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    atualizado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    autor = relationship("Usuario", back_populates="ocorrencias")
    categoria = relationship("Categoria", back_populates="ocorrencias")
    logs = relationship("LogEvento", back_populates="ocorrencia")


class InscricaoNotificacao(Base):
    """Subscrição de alertas por ocorrência específica ou raio (US03)."""

    __tablename__ = "inscricoes_notificacao"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    ocorrencia_id = Column(Integer, ForeignKey("ocorrencias.id"), nullable=True)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=True)
    centro_alerta = Column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    raio_metros = Column(Float, nullable=True)


class LogEvento(Base):
    """Histórico de transições de status das ocorrências (US03)."""

    __tablename__ = "logs_eventos"

    id = Column(Integer, primary_key=True, index=True)
    ocorrencia_id = Column(Integer, ForeignKey("ocorrencias.id"), nullable=False)
    status_anterior = Column(Enum(StatusOcorrencia), nullable=True)
    status_novo = Column(Enum(StatusOcorrencia), nullable=False)
    registrado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    ocorrencia = relationship("Ocorrencia", back_populates="logs")


class LogPesquisa(Base):
    """Auditoria de buscas e filtros para relatórios gerenciais (US06)."""

    __tablename__ = "logs_pesquisa"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True)
    termo_buscado = Column(String(150), nullable=True)
    regiao_filtrada = Column(String(100), nullable=True)
    pesquisado_em = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
