import { useState } from 'react';
import { ModalBase } from './ModalBase';

export function ModalAdicionarCategoria({ isOpen, onClose, onAdd }) {
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  const handleClose = () => {
    setErro('');
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (nome.trim().length < 2) {
      setErro('O nome deve ter pelo menos 2 caracteres.');
      return;
    }

    setEnviando(true);
    try {
      await onAdd({ nome: nome.trim(), descricao: descricao.trim() || null });
      setNome('');
      setDescricao('');
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao criar categoria.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase isOpen={isOpen} onClose={handleClose} title="Nova Categoria">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <div>
          <label className="block mb-1 text-sm font-medium">Nome da Categoria</label>
          <input
            type="text"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            placeholder="Ex: Buraco na via..."
            maxLength={80}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            autoFocus
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Descrição (opcional)</label>
          <textarea
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Breve descrição do tipo de ocorrência..."
            maxLength={255}
            rows={3}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          />
        </div>

        <div className="flex justify-end gap-2 mt-2">
          <button
            type="button"
            onClick={handleClose}
            disabled={enviando}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={enviando}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-60 transition font-medium"
          >
            {enviando ? 'Salvando...' : 'Salvar'}
          </button>
        </div>
      </form>
    </ModalBase>
  );
}