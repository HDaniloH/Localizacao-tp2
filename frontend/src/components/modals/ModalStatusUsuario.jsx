import { useState } from 'react';
import { ModalBase } from './ModalBase';

export function ModalStatusUsuario({ isOpen, onClose, usuario, onToggleStatus }) {
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  if (!usuario) return null;

  const estaAtivo = usuario.ativo;

  const handleConfirm = async () => {
    setErro('');
    setEnviando(true);
    try {
      await onToggleStatus(usuario);
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao alterar situação do usuário.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase
      isOpen={isOpen}
      onClose={onClose}
      title={estaAtivo ? 'Inativar Usuário' : 'Reativar Usuário'}
    >
      <div className="flex flex-col gap-4">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <p className="text-gray-700 dark:text-gray-300">
          {estaAtivo ? (
            <>
              Deseja inativar a conta de{' '}
              <span className="font-bold text-gray-900 dark:text-white">{usuario.nome}</span>?
              O usuário perderá acesso ao login, mas suas ocorrências registradas serão preservadas.
            </>
          ) : (
            <>
              Deseja reativar a conta de{' '}
              <span className="font-bold text-gray-900 dark:text-white">{usuario.nome}</span>?
              O usuário voltará a conseguir acessar o sistema normalmente.
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
              estaAtivo
                ? 'bg-red-600 hover:bg-red-700'
                : 'bg-green-600 hover:bg-green-700'
            }`}
          >
            {enviando
              ? 'Processando...'
              : estaAtivo
                ? 'Inativar'
                : 'Reativar'}
          </button>
        </div>
      </div>
    </ModalBase>
  );
}