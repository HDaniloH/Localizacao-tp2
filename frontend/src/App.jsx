import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Login } from './pages/Login';
import { CategoriasAdmin } from './pages/CategoriasAdmin';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<h1 className="text-xl">Bem-vindo ao UrbanReport (Em construção)</h1>} />
          <Route path="login" element={<Login />} />
          <Route path="admin/categorias" element={<CategoriasAdmin />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;