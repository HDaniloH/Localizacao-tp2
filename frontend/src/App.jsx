import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { Layout } from './components/Layout';
import { RotaProtegida } from './components/RotaProtegida';
import { Login } from './pages/Login';
import { Cadastro } from './pages/Cadastro';
import { CategoriasAdmin } from './pages/CategoriasAdmin';
import { UsuariosAdmin } from './pages/UsuariosAdmin';
import { Perfil } from './pages/Perfil';
import { MapaOcorrencias } from './pages/MapaOcorrencias';

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<MapaOcorrencias />} />
            <Route path="login" element={<Login />} />
            <Route path="cadastro" element={<Cadastro />} />

            <Route element={<RotaProtegida />}>
              <Route path="perfil" element={<Perfil />} />
            </Route>

            <Route element={<RotaProtegida apenasAdmin />}>
              <Route path="admin/categorias" element={<CategoriasAdmin />} />
              <Route path="admin/usuarios" element={<UsuariosAdmin />} />
            </Route>
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;