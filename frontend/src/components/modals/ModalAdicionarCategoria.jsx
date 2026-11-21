import { useState } from 'react';
import { ModalBase } from './ModalBase';

export function ModalAdicionarCategoria({ isOpen, onClose, onAdd }) {
  const [novaCategoria, setNovaCategoria] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!novaCategoria.trim()) return;
    
    onAdd(novaCategoria);
    setNovaCategoria(''); // Limpa o input
    onClose(); // Fecha o modal
  };

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Nova Categoria">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="block mb-1 text-sm font-medium">Nome da Categoria</label>
          <input 
            type="text" 
            value={novaCategoria}
            onChange={(e) => setNovaCategoria(e.target.value)}
            placeholder="Ex: Buraco na via..."
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            autoFocus
          />
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
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium"
          >
            Salvar
          </button>
        </div>
      </form>
    </ModalBase>
  );
}