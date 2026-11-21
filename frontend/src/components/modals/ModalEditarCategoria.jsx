import { useState, useEffect } from 'react';
import { ModalBase } from './ModalBase';

export function ModalEditarCategoria({ isOpen, onClose, categoria, onEdit }) {
  const [nome, setNome] = useState('');
  const [descricao, setDescricao] = useState('');
  const [ativa, setAtiva] = useState(true);
  const [erro, setErro] = useState('');
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (categoria) {
      setNome(categoria.nome || '');
      setDescricao(categoria.descricao || '');
      setAtiva(Boolean(categoria.ativa));
      setErro('');
    }
  }, [categoria]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    if (nome.trim().length < 2) {
      setErro('O nome deve ter pelo menos 2 caracteres.');
      return;
    }

    setEnviando(true);
    try {
      await onEdit(categoria.id, {
        nome: nome.trim(),
        descricao: descricao.trim() || null,
        ativa,
      });
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao atualizar categoria.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Editar Categoria">
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <div>
          <label className="block mb-1 text-sm font-medium">Nome</label>
          <input
            type="text"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            maxLength={80}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Descrição (opcional)</label>
          <textarea
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            maxLength={255}
            rows={3}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Situação</label>
          <select
            value={ativa ? 'true' : 'false'}
            onChange={(e) => setAtiva(e.target.value === 'true')}
            className="w-full p-3 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="true">Ativa</option>
            <option value="false">Inativa</option>
          </select>
        </div>

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
            type="submit"
            disabled={enviando}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-60 transition font-medium"
          >
            {enviando ? 'Atualizando...' : 'Atualizar'}
          </button>
        </div>
      </form>
    </ModalBase>
  );
}