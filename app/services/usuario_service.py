"""Regras de negócio de usuários e autenticação."""

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    Conflito,
    OperacaoNaoPermitida,
    RecursoNaoEncontrado,
    RequisicaoInvalida,
)
from app.core.security import gerar_hash_senha, verificar_senha
from app.models import Usuario
from app.schemas.usuario import (
    UsuarioAtualizarAdmin,
    UsuarioCriar,
)

# Hash usado quando o e-mail não existe, para que o tempo de resposta do
# login seja parecido nos dois casos (evita descobrir e-mails cadastrados).
_HASH_FICTICIO = gerar_hash_senha("senha-ficticia-0")


class CredenciaisInvalidas(Exception):
    """E-mail ou senha incorretos."""


class UsuarioInativo(Exception):
    """A conta existe, mas foi inativada."""


def _normalizar_email(email: str) -> str:
    return email.strip().lower()


def buscar_por_email(db: Session, email: str) -> Usuario | None:
    """Busca um usuário pelo e-mail, sem diferenciar maiúsculas.

    Args:
        db: Sessão do banco.
        email: E-mail procurado.

    Returns:
        O usuário, ou ``None`` se não existir.
    """
    consulta = select(Usuario).where(
        func.lower(Usuario.email) == _normalizar_email(email)
    )
    return db.scalars(consulta).first()


def obter(db: Session, usuario_id: int) -> Usuario:
    """Obtém um usuário pelo id.

    Raises:
        RecursoNaoEncontrado: Se o id não existir.
    """
    usuario = db.get(Usuario, usuario_id)
    if usuario is None:
        raise RecursoNaoEncontrado("Usuário não encontrado")
    return usuario


def listar(db: Session, ativo: bool | None = None) -> list[Usuario]:
    """Lista usuários, opcionalmente filtrando pela situação.

    Args:
        db: Sessão do banco.
        ativo: ``True``/``False`` para filtrar; ``None`` para todos.
    """
    consulta = select(Usuario).order_by(Usuario.nome, Usuario.id)
    if ativo is not None:
        consulta = consulta.where(Usuario.ativo == ativo)
    return list(db.scalars(consulta))


def _garantir_email_livre(
    db: Session, email: str, ignorar_id: int | None = None
) -> None:
    existente = buscar_por_email(db, email)
    if existente is not None and existente.id != ignorar_id:
        raise Conflito("E-mail já cadastrado")


def criar(db: Session, dados: UsuarioCriar, is_admin: bool = False) -> Usuario:
    """Cadastra um novo usuário.

    Args:
        db: Sessão do banco.
        dados: Nome, e-mail e senha validados.
        is_admin: Se o novo usuário é administrador (só admins escolhem).

    Raises:
        Conflito: Se o e-mail já estiver em uso.
    """
    _garantir_email_livre(db, dados.email)
    usuario = Usuario(
        nome=dados.nome,
        email=_normalizar_email(dados.email),
        senha_hash=gerar_hash_senha(dados.senha),
        is_admin=is_admin,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def autenticar(db: Session, email: str, senha: str) -> Usuario:
    """Valida as credenciais de login.

    Raises:
        CredenciaisInvalidas: Se o e-mail não existir ou a senha não conferir.
        UsuarioInativo: Se a senha conferir, mas a conta estiver inativa.
    """
    usuario = buscar_por_email(db, email)
    if usuario is None:
        verificar_senha(senha, _HASH_FICTICIO)
        raise CredenciaisInvalidas()
    if not verificar_senha(senha, usuario.senha_hash):
        raise CredenciaisInvalidas()
    if not usuario.ativo:
        raise UsuarioInativo()
    return usuario


def atualizar(
    db: Session,
    usuario_id: int,
    dados: UsuarioAtualizarAdmin,
    solicitante: Usuario,
) -> Usuario:
    """Altera um usuário respeitando as permissões do solicitante.

    Regras:
        * Usuário comum só altera a si mesmo, e só nome/e-mail/senha.
        * Admin altera qualquer usuário, inclusive ``is_admin`` e ``ativo``.
        * Admin não pode tirar o próprio acesso de admin nem se inativar
          (evita o sistema ficar sem administrador por engano).

    Raises:
        OperacaoNaoPermitida: Se o solicitante não tiver permissão.
        RecursoNaoEncontrado: Se o usuário não existir.
        Conflito: Se o novo e-mail já estiver em uso.
        RequisicaoInvalida: Se o admin tentar rebaixar/inativar a si mesmo.
    """
    eh_admin = bool(solicitante.is_admin)
    if not eh_admin and solicitante.id != usuario_id:
        raise OperacaoNaoPermitida("Sem permissão para alterar este usuário")
    campos = dados.model_dump(exclude_unset=True)
    if not eh_admin and ({"is_admin", "ativo"} & campos.keys()):
        raise OperacaoNaoPermitida("Apenas administradores alteram is_admin e situação")

    usuario = obter(db, usuario_id)
    if eh_admin and usuario.id == solicitante.id:
        rebaixando = campos.get("is_admin") is False
        inativando = campos.get("ativo") is False
        if rebaixando or inativando:
            raise RequisicaoInvalida(
                "Você não pode remover o próprio acesso de administrador"
            )

    if "email" in campos:
        _garantir_email_livre(db, campos["email"], ignorar_id=usuario.id)
        usuario.email = _normalizar_email(campos["email"])
    if "senha" in campos:
        usuario.senha_hash = gerar_hash_senha(campos["senha"])
    for campo in ("nome", "is_admin", "ativo"):
        if campos.get(campo) is not None:
            setattr(usuario, campo, campos[campo])

    db.commit()
    db.refresh(usuario)
    return usuario


def inativar(db: Session, usuario_id: int, solicitante: Usuario) -> None:
    """Inativa (exclusão lógica) um usuário.

    Raises:
        RequisicaoInvalida: Se o admin tentar inativar a si mesmo.
        RecursoNaoEncontrado: Se o usuário não existir.
    """
    if usuario_id == solicitante.id:
        raise RequisicaoInvalida("Você não pode inativar a própria conta")
    usuario = obter(db, usuario_id)
    usuario.ativo = False
    db.commit()
