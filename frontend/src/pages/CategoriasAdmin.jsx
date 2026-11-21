import { useState, useEffect, useCallback } from 'react';
import { Plus, Edit2, Power, RotateCcw } from 'lucide-react';
import { categoriasService } from '../services/api';
import { ModalAdicionarCategoria } from '../components/modals/ModalAdicionarCategoria';
import { ModalEditarCategoria } from '../components/modals/ModalEditarCategoria';
import { ModalDeletarCategoria } from '../components/modals/ModalDeletarCategoria';

export function CategoriasAdmin() {
  const [categorias, setCategorias] = useState([]);
  const [filtroAtiva, setFiltroAtiva] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isToggleOpen, setIsToggleOpen] = useState(false);
  const [categoriaSelecionada, setCategoriaSelecionada] = useState(null);

  const carregarCategorias = useCallback(async () => {
    setCarregando(true);
    setErro('');
    try {
      const dados = await categoriasService.listarAdmin(filtroAtiva);
      setCategorias(dados);
    } catch (err) {
      setErro(err.message || 'Erro ao carregar categorias.');
    } finally {
      setCarregando(false);
    }
  }, [filtroAtiva]);

  useEffect(() => {
    carregarCategorias();
  }, [carregarCategorias]);

  const handleAdd = async ({ nome, descricao }) => {
    await categoriasService.criar({ nome, descricao });
    await carregarCategorias();
  };

  const handleEdit = async (id, { nome, descricao, ativa }) => {
    const atualizada = await categoriasService.atualizar(id, { nome, descricao });
    if (atualizada.ativa !== ativa) {
      if (ativa) {
        await categoriasService.reativar(id);
      } else {
        await categoriasService.inativar(id);
      }
    }
    await carregarCategorias();
  };

  const handleToggleStatus = async (cat) => {
    if (cat.ativa) {
      await categoriasService.inativar(cat.id);
    } else {
      await categoriasService.reativar(cat.id);
    }
    await carregarCategorias();
  };

  const openEdit = (cat) => {
    setCategoriaSelecionada(cat);
    setIsEditOpen(true);
  };

  const openToggle = (cat) => {
    setCategoriaSelecionada(cat);
    setIsToggleOpen(true);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 relative">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <h2 className="text-2xl font-bold">Gestão de Categorias (Admin)</h2>

        <button
          onClick={() => setIsAddOpen(true)}
          className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
        >
          <Plus size={20} /> <span>Nova Categoria</span>
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        {[
          { label: 'Todas', valor: null },
          { label: 'Ativas', valor: true },
          { label: 'Inativas', valor: false },
        ].map((opcao) => (
          <button
            key={opcao.label}
            onClick={() => setFiltroAtiva(opcao.valor)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              filtroAtiva === opcao.valor
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600'
            }`}
          >
            {opcao.label}
          </button>
        ))}
      </div>

      {erro && (
        <div className="mb-4 p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
          {erro}
        </div>
      )}

      {carregando ? (
        <p className="py-8 text-center text-gray-500 dark:text-gray-400">
          Carregando categorias...
        </p>
      ) : categorias.length === 0 ? (
        <p className="py-8 text-center text-gray-500 dark:text-gray-400">
          Nenhuma categoria encontrada.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b dark:border-gray-700">
                <th className="p-3">ID</th>
                <th className="p-3">Categoria</th>
                <th className="p-3">Situação</th>
                <th className="p-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {categorias.map((cat) => (
                <tr
                  key={cat.id}
                  className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  <td className="p-3 text-gray-500 dark:text-gray-400">#{cat.id}</td>
                  <td className="p-3">
                    <div className="font-medium">{cat.nome}</div>
                    {cat.descricao && (
                      <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                        {cat.descricao}
                      </div>
                    )}
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-1 rounded-full text-xs font-semibold ${
                        cat.ativa
                          ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                          : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                      }`}
                    >
                      {cat.ativa ? 'Ativa' : 'Inativa'}
                    </span>
                  </td>
                  <td className="p-3">
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => openEdit(cat)}
                        className="p-2 text-blue-500 hover:bg-blue-50 dark:hover:bg-gray-600 rounded transition"
                        title="Editar"
                      >
                        <Edit2 size={18} />
                      </button>
                      <button
                        onClick={() => openToggle(cat)}
                        className={`p-2 rounded transition ${
                          cat.ativa
                            ? 'text-red-500 hover:bg-red-50 dark:hover:bg-gray-600'
                            : 'text-green-500 hover:bg-green-50 dark:hover:bg-gray-600'
                        }`}
                        title={cat.ativa ? 'Inativar' : 'Reativar'}
                      >
                        {cat.ativa ? <Power size={18} /> : <RotateCcw size={18} />}
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <ModalAdicionarCategoria
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onAdd={handleAdd}
      />

      <ModalEditarCategoria
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        categoria={categoriaSelecionada}
        onEdit={handleEdit}
      />

      <ModalDeletarCategoria
        isOpen={isToggleOpen}
        onClose={() => setIsToggleOpen(false)}
        categoria={categoriaSelecionada}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  );
}