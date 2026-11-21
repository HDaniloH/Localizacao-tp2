import { useState, useEffect } from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Sun, Moon, Menu, X, LogOut } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

export function Layout() {
  const [isDarkMode, setIsDarkMode] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const { usuario, autenticado, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  const handleLogout = () => {
    logout();
    setMenuOpen(false);
    navigate('/login');
  };

  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-white dark:bg-gray-800 shadow-md p-4">
        <div className="max-w-6xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-xl font-bold text-blue-600 dark:text-blue-400">
            UrbanReport
          </Link>

          <div className="flex items-center gap-4">
            <div className="hidden md:flex items-center gap-4">
              {!autenticado ? (
                <>
                  <Link to="/login" className="hover:text-blue-500">Login</Link>
                  <Link
                    to="/cadastro"
                    className="bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition text-sm font-medium"
                  >
                    Cadastrar
                  </Link>
                </>
              ) : (
                <>
                  {isAdmin && (
                    <>
                      <Link to="/admin/categorias" className="hover:text-blue-500">
                        Categorias (US05)
                      </Link>
                      <Link to="/admin/usuarios" className="hover:text-blue-500">
                        Usuários
                      </Link>
                    </>
                  )}
                  <Link
                    to="/perfil"
                    className={`text-sm text-gray-600 dark:text-gray-300 hover:text-blue-500 flex items-center ${
                      isAdmin ? 'border-l dark:border-gray-700 pl-4' : ''
                    }`}
                    title="Meu Perfil"
                  >
                    {usuario.nome}
                    {isAdmin && (
                      <span className="ml-1.5 text-xs bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 px-2 py-0.5 rounded-full">
                        Admin
                      </span>
                    )}
                  </Link>
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-1 text-sm text-red-600 dark:text-red-400 hover:underline"
                    title="Sair"
                  >
                    <LogOut size={16} />
                    Sair
                  </button>
                </>
              )}
            </div>

            <button
              onClick={() => setIsDarkMode(!isDarkMode)}
              className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
              aria-label="Alternar tema"
            >
              {isDarkMode ? <Sun size={20} /> : <Moon size={20} />}
            </button>

            <button
              className="md:hidden"
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Abrir menu"
            >
              {menuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {menuOpen && (
          <div className="md:hidden flex flex-col gap-2 mt-4 pb-2 border-t dark:border-gray-700 pt-2">
            {!autenticado ? (
              <>
                <Link to="/login" onClick={() => setMenuOpen(false)} className="block py-2">
                  Login
                </Link>
                <Link
                  to="/cadastro"
                  onClick={() => setMenuOpen(false)}
                  className="block py-2 text-blue-600 dark:text-blue-400 font-medium"
                >
                  Cadastrar
                </Link>
              </>
            ) : (
              <>
                <div className="py-2 text-sm text-gray-500 dark:text-gray-400">
                  Logado como <strong className="text-gray-800 dark:text-gray-200">{usuario.nome}</strong>
                </div>
                <Link
                  to="/perfil"
                  onClick={() => setMenuOpen(false)}
                  className="block py-2"
                >
                  Meu Perfil
                </Link>
                {isAdmin && (
                  <>
                    <Link
                      to="/admin/categorias"
                      onClick={() => setMenuOpen(false)}
                      className="block py-2"
                    >
                      Categorias (US05)
                    </Link>
                    <Link
                      to="/admin/usuarios"
                      onClick={() => setMenuOpen(false)}
                      className="block py-2"
                    >
                      Usuários
                    </Link>
                  </>
                )}
                <button
                  onClick={handleLogout}
                  className="flex items-center gap-2 py-2 text-red-600 dark:text-red-400 text-left"
                >
                  <LogOut size={16} />
                  Sair
                </button>
              </>
            )}
          </div>
        )}
      </nav>

      <main className="flex-1 w-full max-w-6xl mx-auto p-4 sm:p-6 lg:p-8">
        <Outlet />
      </main>
    </div>
  );
}