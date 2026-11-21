import { useState } from 'react';
import { Plus, Trash2, Edit2 } from 'lucide-react';
import { ModalAdicionarCategoria } from '../components/modals/ModalAdicionarCategoria';
import { ModalEditarCategoria } from '../components/modals/ModalEditarCategoria';
import { ModalDeletarCategoria } from '../components/modals/ModalDeletarCategoria';

export function CategoriasAdmin() {
  const [categorias, setCategorias] = useState([
    { id: 1, nome: 'Buraco na via', status: 'Ativo' },
    { id: 2, nome: 'Falta de iluminação', status: 'Ativo' },
    { id: 3, nome: 'Semáforo quebrado', status: 'Inativo' },
  ]);

  // Estados de controle dos modais
  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);

  // Guarda qual categoria foi selecionada para editar ou deletar
  const [categoriaSelecionada, setCategoriaSelecionada] = useState(null);

  // --- Funções de Ação ---
  const handleAdd = (nome) => {
    const nova = { id: Date.now(), nome, status: 'Ativo' };
    setCategorias([...categorias, nova]);
  };

  const handleEdit = (id, novoNome, novoStatus) => {
    setCategorias(categorias.map(cat => 
      cat.id === id ? { ...cat, nome: novoNome, status: novoStatus } : cat
    ));
  };

  const handleDelete = (id) => {
    setCategorias(categorias.filter(cat => cat.id !== id));
  };

  // --- Funções para abrir os modais com o item certo ---
  const openEdit = (cat) => {
    setCategoriaSelecionada(cat);
    setIsEditOpen(true);
  };

  const openDelete = (cat) => {
    setCategoriaSelecionada(cat);
    setIsDeleteOpen(true);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 relative">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">Gestão de Categorias (Admin)</h2>
        
        {/* O input de cadastro virou apenas um botão que abre o modal */}
        <button 
          onClick={() => setIsAddOpen(true)}
          className="flex items-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
        >
          <Plus size={20} /> <span className="hidden sm:inline">Nova Categoria</span>
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="border-b dark:border-gray-700">
              <th className="p-3">ID</th>
              <th className="p-3">Nome da Categoria</th>
              <th className="p-3">Status</th>
              <th className="p-3 text-right">Ações</th>
            </tr>
          </thead>
          <tbody>
            {categorias.map((cat) => (
              <tr key={cat.id} className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                <td className="p-3 text-gray-500 dark:text-gray-400">#{cat.id}</td>
                <td className="p-3 font-medium">{cat.nome}</td>
                <td className="p-3">
                  <span className={`px-2 py-1 rounded-full text-xs font-semibold ${
                    cat.status === 'Ativo' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {cat.status}
                  </span>
                </td>
                <td className="p-3 flex justify-end gap-2">
                  <button 
                    onClick={() => openEdit(cat)}
                    className="p-2 text-blue-500 hover:bg-blue-50 dark:hover:bg-gray-700 rounded transition"
                  >
                    <Edit2 size={18} />
                  </button>
                  <button 
                    onClick={() => openDelete(cat)}
                    className="p-2 text-red-500 hover:bg-red-50 dark:hover:bg-gray-700 rounded transition"
                  >
                    <Trash2 size={18} />
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Renderização dos Modais (ficam invisíveis até isOpen ser true) */}
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
        isOpen={isDeleteOpen} 
        onClose={() => setIsDeleteOpen(false)} 
        categoria={categoriaSelecionada}
        onDelete={handleDelete}
      />
    </div>
  );
}