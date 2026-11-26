import { createContext, useContext, useEffect, useState } from 'react';
import { authService } from '../services/api';

const AuthContext = createContext(null);

/**
 * Provedor de contexto global de autenticação JWT da aplicação.
 * Gerencia o armazenamento do token, dados do usuário logado e ações de login/logout.
 *
 * @param {Object} props - Propriedades do provedor.
 * @param {React.ReactNode} props.children - Componentes filhos envolvidos pelo contexto.
 * @returns {JSX.Element} Provedor AuthContext.
 */
export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null);
  const [carregando, setCarregando] = useState(true);

  useEffect(() => {
    async function restaurarSessao() {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setCarregando(false);
        return;
      }

      try {
        const dados = await authService.me();
        setUsuario(dados);
      } catch {
        localStorage.removeItem('access_token');
        setUsuario(null);
      } finally {
        setCarregando(false);
      }
    }

    restaurarSessao();
  }, []);

  async function login(email, senha) {
    const { access_token } = await authService.login(email, senha);
    localStorage.setItem('access_token', access_token);
    const dados = await authService.me();
    setUsuario(dados);
    return dados;
  }

  async function registrar({ nome, email, senha }) {
    await authService.registrar({ nome, email, senha });
    return login(email, senha);
  }

  function logout() {
    localStorage.removeItem('access_token');
    setUsuario(null);
  }

  return (
    <AuthContext.Provider
      value={{
        usuario,
        setUsuario,
        carregando,
        autenticado: Boolean(usuario),
        isAdmin: Boolean(usuario?.is_admin),
        login,
        registrar,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return ctx;
}