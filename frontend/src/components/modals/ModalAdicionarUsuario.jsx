import { useState } from 'react';
import { ModalBase } from './ModalBase';

export function ModalAdicionarUsuario({ isOpen, onClose, onAdd }) {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [isAdmin, setIsAdmin] = useState(false);
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const handleClose = () => {
    setErro('');
    onClose();
  };

  const validar = () => {
    if (nome.trim().length < 2) {
      return 'O nome deve ter pelo menos 2 caracteres.';
    }
    if (senha.length < 8 || senha.length > 72) {
      return 'A senha deve ter entre 8 e 72 caracteres.';
    }
    if (!/[a-zA-Z]/.test(senha) || !/\d/.test(senha)) {
      return 'A senha deve conter ao menos uma letra e um número.';
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    const erroValidacao = validar();
    if (erroValidacao) {
      setErro(erroValidacao);
      return;
    }

    setEnviando(true);
    try {
      await onAdd({
        nome: nome.trim(),
        email: email.trim(),
        senha,
        is_admin: isAdmin,
      });
      setNome('');
      setEmail('');
      setSenha('');
      setIsAdmin(false);
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao criar usuário.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase isOpen={isOpen} onClose={handleClose} title="Novo Usuário">
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
            placeholder="Nome completo"
            maxLength={120}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            autoFocus
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">E-mail</label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="usuario@email.com"
            maxLength={150}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Senha</label>
          <input
            type="password"
            value={senha}
            onChange={(e) => setSenha(e.target.value)}
            placeholder="Mín. 8 caracteres (letras e números)"
            maxLength={72}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <label className="flex items-center gap-2 text-sm cursor-pointer select-none">
          <input
            type="checkbox"
            checked={isAdmin}
            onChange={(e) => setIsAdmin(e.target.checked)}
            className="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />
          <span>Conceder permissão de Administrador</span>
        </label>

        <div className="flex justify-end gap-2 mt-2">
          <button
            type="button"
            onClick={handleClose}
            disabled={enviando}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={enviando}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-60 transition font-medium"
          >
            {enviando ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </ModalBase>
  );
}