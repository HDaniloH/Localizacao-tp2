import { useState, useEffect } from 'react';
import { ModalBase } from './ModalBase';

export function ModalEditarUsuario({
  isOpen,
  onClose,
  usuario,
  ehProprioUsuario,
  onEdit,
}) {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [ativo, setAtivo] = useState(true);
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (usuario) {
      setNome(usuario.nome || '');
      setEmail(usuario.email || '');
      setSenha('');
      setIsAdmin(Boolean(usuario.is_admin));
      setAtivo(Boolean(usuario.ativo));
      setErro('');
    }
  }, [usuario]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (nome.trim().length < 2) {
      setErro('O nome deve ter pelo menos 2 caracteres.');
      return;
    }

    if (senha) {
      if (senha.length < 8 || senha.length > 72) {
        setErro('A nova senha deve ter entre 8 e 72 caracteres.');
        return;
      }
      if (!/[a-zA-Z]/.test(senha) || !/\d/.test(senha)) {
        setErro('A nova senha deve conter ao menos uma letra e um número.');
        return;
      }
    }

    const payload = {
      nome: nome.trim(),
      email: email.trim(),
      is_admin: isAdmin,
      ativo,
    };

    if (senha) {
      payload.senha = senha;
    }

    setEnviando(true);
    try {
      await onEdit(usuario.id, payload);
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao atualizar usuário.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Editar Usuário">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <div>
          <label className="block mb-1 text-sm font-medium">Nome</label>
          <input
            type="text"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            maxLength={120}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">E-mail</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            maxLength={150}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Nova Senha (opcional)</label>
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder="Deixe em branco para manter a atual"
            maxLength={72}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Situação</label>
          <select
            value={ativo ? 'true' : 'false'}
            onChange={(e) => setAtivo(e.target.value === 'true')}
            disabled={ehProprioUsuario}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none disabled:opacity-60"
          >
            <option value="true">Ativo</option>
            <option value="false">Inativo</option>
          </select>
        </div>

        <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
          <input
            type="checkbox"
            checked={isAdmin}
            onChange={(e) => setIsAdmin(e.target.checked)}
            disabled={ehProprioUsuario}
            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500 disabled:opacity-60"
          />
          <span>Permissão de Administrador</span>
        </label>

        {ehProprioUsuario && (
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Por segurança, não é possível alterar o próprio status ou permissão de administrador.
          </p>
        )}

        <div className="flex justify-end gap-2 mt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={enviando}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={enviando}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 transition font-medium"
          >
            {enviando ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>
      </form>
    </ModalBase>
  );
}