import { useState } from 'react';
import { ModalBase } from './ModalBase';

export function ModalDeletarCategoria({ isOpen, onClose, categoria, onToggleStatus }) {
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  if (!categoria) return null;

  const estaAtiva = categoria.ativa;

  const handleConfirm = async () => {
    setErro('');
    setEnviando(true);
    try {
      await onToggleStatus(categoria);
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao alterar situação da categoria.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase
      isOpen={isOpen}
      onClose={onClose}
      title={estaAtiva ? 'Inativar Categoria' : 'Reativar Categoria'}
    >
      <div className="flex flex-col gap-4">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <p className="text-gray-700 dark:text-gray-300">
          {estaAtiva ? (
            <>
              Deseja inativar a categoria{' '}
              <span className="font-bold text-gray-900 dark:text-white">"{categoria.nome}"</span>?
              Ela deixará de aparecer nas listas públicas, mas poderá ser reativada depois.
            </>
          ) : (
            <>
              Deseja reativar a categoria{' '}
              <span className="font-bold text-gray-900 dark:text-white">"{categoria.nome}"</span>?
              Ela voltará a ficar disponível para novas ocorrências.
            </>
          )}
        </p>

        <div className="flex justify-end gap-2 mt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={enviando}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            type="button"
            onClick={handleConfirm}
            disabled={enviando}
            className={`px-4 py-2 text-white rounded-lg disabled:opacity-60 transition font-medium ${
              estaAtiva
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {enviando
              ? 'Processando...'
              : estaAtiva
                ? 'Inativar'
                : 'Reativar'}
          </button>
        </div>
      </div>
    </ModalBase>
  );
}