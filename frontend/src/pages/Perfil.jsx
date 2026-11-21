import { useState, useEffect } from 'react';
import { User, Save } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { usuariosService } from '../services/api';

function formatarData(isoString) {
  if (!isoString) return '-';
  return new Date(isoString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function Perfil() {
  const { usuario, setUsuario } = useAuth();

  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [erro, setErro] = useState('');
  const [sucesso, setSucesso] = useState('');
  const [salvando, setSalvando] = useState(false);

  useEffect(() => {
    if (usuario) {
      setNome(usuario.nome || '');
      setEmail(usuario.email || '');
    }
  }, [usuario]);

  const validar = () => {
    if (nome.trim().length < 2) {
      return 'O nome deve ter pelo menos 2 caracteres.';
    }
    if (senha) {
      if (senha.length < 8 || senha.length > 72) {
        return 'A nova senha deve ter entre 8 e 72 caracteres.';
      }
      if (!/[a-zA-Z]/.test(senha) || !/\d/.test(senha)) {
        return 'A nova senha deve conter ao menos uma letra e um número.';
      }
      if (senha !== confirmarSenha) {
        return 'As senhas não conferem.';
      }
    }
    return null;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');
    setSucesso('');

    const erroValidacao = validar();
    if (erroValidacao) {
      setErro(erroValidacao);
      return;
    }

    const payload = {
      nome: nome.trim(),
      email: email.trim(),
    };

    if (senha) {
      payload.senha = senha;
    }

    setSalvando(true);
    try {
      const atualizado = await usuariosService.atualizar(usuario.id, payload);
      setUsuario(atualizado);
      setSenha('');
      setConfirmarSenha('');
      setSucesso('Dados atualizados com sucesso.');
    } catch (err) {
      setErro(err.message || 'Erro ao atualizar perfil.');
    } finally {
      setSalvando(false);
    }
  };

  if (!usuario) return null;

  return (
    <div className="max-w-xl mx-auto bg-white dark:bg-gray-800 rounded-xl shadow p-6 sm:p-8">
      <div className="flex items-center gap-3 mb-6 pb-4 border-b dark:border-gray-700">
        <div className="p-3 rounded-full bg-blue-100 text-blue-600 dark:bg-blue-900/40 dark:text-blue-300">
          <User size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold">Meu Perfil</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {usuario.is_admin ? 'Administrador' : 'Cidadão'} • Membro desde{' '}
            {formatarData(usuario.criado_em)}
          </p>
        </div>
      </div>

      {erro && (
        <div className="mb-4 p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
          {erro}
        </div>
      )}

      {sucesso && (
        <div className="mb-4 p-3 rounded-lg bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300 text-sm">
          {sucesso}
        </div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block mb-1 text-sm font-medium">Nome completo</label>
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

        <div className="pt-2 border-t dark:border-gray-700">
          <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Alterar senha (opcional)
          </p>

          <div className="flex flex-col gap-4">
            <div>
              <label className="block mb-1 text-sm font-medium">Nova senha</label>
              <input
                type="password"
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                placeholder="Deixe em branco para manter a atual"
                maxLength={72}
                className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
              />
            </div>

            {senha && (
              <div>
                <label className="block mb-1 text-sm font-medium">Confirmar nova senha</label>
                <input
                  type="password"
                  value={confirmarSenha}
                  onChange={(e) => setConfirmarSenha(e.target.value)}
                  placeholder="Repita a nova senha"
                  maxLength={72}
                  className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
                  required
                />
              </div>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={salvando}
          className="mt-2 flex items-center justify-center gap-2 w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-60 transition font-semibold"
        >
          <Save size={18} />
          {salvando ? 'Salvando...' : 'Salvar Alterações'}
        </button>
      </form>
    </div>
  );
}