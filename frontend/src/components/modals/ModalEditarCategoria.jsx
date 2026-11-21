import { useState, useEffect } from 'react';
import { ModalBase } from './ModalBase';

export function ModalEditarCategoria({ isOpen, onClose, categoria, onEdit }) {
  const [nome, setNome] = useState('');
  const [status, setStatus] = useState('Ativo');

  // Atualiza os inputs quando a categoria selecionada mudar
  useEffect(() => {
    if (categoria) {
      setNome(categoria.nome);
      setStatus(categoria.status);
    }
  }, [categoria]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!nome.trim()) return;
    
    onEdit(categoria.id, nome, status);
    onClose();
  };

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Editar Categoria">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block mb-1 text-sm font-medium">Nome</label>
          <input 
            type="text" 
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Status</label>
          <select 
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="Ativo">Ativo</option>
            <option value="Inativo">Inativo</option>
          </select>
        </div>
        
        <div className="flex justify-end gap-2 mt-2">
          <button 
            type="button" 
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button 
            type="submit"
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
          >
            Atualizar
          </button>
        </div>
      </form>
    </ModalBase>
  );
}