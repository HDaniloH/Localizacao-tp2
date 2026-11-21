import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

export function RotaProtegida({ apenasAdmin = false }) {
  const { autenticado, isAdmin, carregando } = useAuth();

  if (carregando) {
    return (
      <div className="flex items-center justify-center min-h-[50vh]">
        <p className="text-gray-500 dark:text-gray-400">Verificando sessão...</p>
      </div>
    );
  }

  if (!autenticado) {
    return <Navigate to="/login" replace />;
  }

  if (apenasAdmin && !isAdmin) {
    return <Navigate to="/" replace />;
  }

  return <Outlet />;
}