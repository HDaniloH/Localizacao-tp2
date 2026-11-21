import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function Cadastro() {
  const [nome, setNome] = useState('');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [confirmarSenha, setConfirmarSenha] = useState('');
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const { registrar } = useAuth();
  const navigate = useNavigate();

  const validarFormulario = () => {
    if (nome.trim().length < 2) {
      return 'O nome deve ter pelo menos 2 caracteres.';
    }
    if (senha.length < 8 || senha.length > 72) {
      return 'A senha deve ter entre 8 e 72 caracteres.';
    }
    if (!/[a-zA-Z]/.test(senha) || !/\d/.test(senha)) {
      return 'A senha deve conter ao menos uma letra e um número.';
    }
    if (senha !== confirmarSenha) {
      return 'As senhas não conferem.';
    }
    return null;
  };

  const handleCadastro = async (e) => {
    e.preventDefault();
    setErro('');

    const erroValidacao = validarFormulario();
    if (erroValidacao) {
      setErro(erroValidacao);
      return;
    }

    setEnviando(true);
    try {
      await registrar({ nome: nome.trim(), email: email.trim(), senha });
      navigate('/');
    } catch (err) {
      setErro(err.message || 'Não foi possível concluir o cadastro.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[70vh]">
      <div className="bg-white dark:bg-gray-800 p-8 rounded-xl shadow-lg w-full max-w-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Criar Conta</h2>

        {erro && (
          <div className="mb-4 p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <form onSubmit={handleCadastro} className="flex flex-col gap-4">
          <div>
            <label className="block mb-1 text-sm font-medium">Nome completo</label>
            <input
              type="text"
              className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Seu nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block mb-1 text-sm font-medium">E-mail</label>
            <input
              type="email"
              className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="seu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block mb-1 text-sm font-medium">Senha</label>
            <input
              type="password"
              className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Mín. 8 caracteres (letras e números)"
              value={senha}
              onChange={(e) => setSenha(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block mb-1 text-sm font-medium">Confirmar senha</label>
            <input
              type="password"
              className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
              placeholder="Repita a senha"
              value={confirmarSenha}
              onChange={(e) => setConfirmarSenha(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            disabled={enviando}
            className="mt-4 w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 disabled:opacity-60 transition font-semibold"
          >
            {enviando ? 'Cadastrando...' : 'Cadastrar'}
          </button>
        </form>

        <p className="mt-6 text-center text-sm text-gray-600 dark:text-gray-400">
          Já possui conta?{' '}
          <Link to="/login" className="text-blue-600 dark:text-blue-400 font-medium hover:underline">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}