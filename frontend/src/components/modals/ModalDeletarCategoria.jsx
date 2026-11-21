import { ModalBase } from './ModalBase';

export function ModalDeletarCategoria({ isOpen, onClose, categoria, onDelete }) {
  if (!categoria) return null;

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Confirmar Exclusão">
      <div className="flex flex-col gap-4">
        <p className="text-gray-700 dark:text-gray-300">
          Tem certeza que deseja excluir a categoria <span className="font-bold text-gray-900 dark:text-white">"{categoria.nome}"</span>? 
          Esta ação não poderá ser desfeita.
        </p>
        
        <div className="flex justify-end gap-2 mt-2">
          <button 
            onClick={onClose}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button 
            onClick={() => {
              onDelete(categoria.id);
              onClose();
            }}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition font-medium"
          >
            Excluir
          </button>
        </div>
      </div>
    </ModalBase>
  );
}