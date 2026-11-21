import { useState, useEffect, useCallback } from 'react';
import { UserPlus, Edit2, Power, RotateCcw } from 'lucide-react';
import { usuariosService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { ModalAdicionarUsuario } from '../components/modals/ModalAdicionarUsuario';
import { ModalEditarUsuario } from '../components/modals/ModalEditarUsuario';
import { ModalStatusUsuario } from '../components/modals/ModalStatusUsuario';

function formatarData(isoString) {
  if (!isoString) return '-';
  return new Date(isoString).toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
  });
}

export function UsuariosAdmin() {
  const { usuario: usuarioLogado, setUsuario } = useAuth();

  const [usuarios, setUsuarios] = useState([]);
  const [filtroAtivo, setFiltroAtivo] = useState(null);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');

  const [isAddOpen, setIsAddOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const [isStatusOpen, setIsStatusOpen] = useState(false);
  const [usuarioSelecionado, setUsuarioSelecionado] = useState(null);

  const carregarUsuarios = useCallback(async () => {
    setCarregando(true);
    setErro('');
    try {
      const dados = await usuariosService.listar(filtroAtivo);
      setUsuarios(dados);
    } catch (err) {
      setErro(err.message || 'Erro ao carregar usuários.');
    } finally {
      setCarregando(false);
    }
  }, [filtroAtivo]);

  useEffect(() => {
    carregarUsuarios();
  }, [carregarUsuarios]);

  const handleAdd = async (dados) => {
    await usuariosService.criar(dados);
    await carregarUsuarios();
  };

  const handleEdit = async (id, dados) => {
    const atualizado = await usuariosService.atualizar(id, dados);
    if (usuarioLogado && atualizado.id === usuarioLogado.id) {
      setUsuario(atualizado);
    }
    await carregarUsuarios();
  };

  const handleToggleStatus = async (u) => {
    if (u.ativo) {
      await usuariosService.inativar(u.id);
    } else {
      await usuariosService.atualizar(u.id, { ativo: true });
    }
    await carregarUsuarios();
  };

  const openEdit = (u) => {
    setUsuarioSelecionado(u);
    setIsEditOpen(true);
  };

  const openStatus = (u) => {
    setUsuarioSelecionado(u);
    setIsStatusOpen(true);
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-6 relative">
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center gap-4 mb-6">
        <h2 className="text-2xl font-bold">Gestão de Usuários (Admin)</h2>

        <button
          onClick={() => setIsAddOpen(true)}
          className="flex items-center justify-center gap-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
        >
          <UserPlus size={20} /> <span>Novo Usuário</span>
        </button>
      </div>

      <div className="flex gap-2 mb-4">
        {[
          { label: 'Todos', valor: null },
          { label: 'Ativos', valor: true },
          { label: 'Inativos', valor: false },
        ].map((opcao) => (
          <button
            key={opcao.label}
            onClick={() => setFiltroAtivo(opcao.valor)}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition ${
              filtroAtivo === opcao.valor
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
          Carregando usuários...
        </p>
      ) : usuarios.length === 0 ? (
        <p className="py-8 text-center text-gray-500 dark:text-gray-400">
          Nenhum usuário encontrado.
        </p>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="border-b dark:border-gray-700">
                <th className="p-3">ID</th>
                <th className="p-3">Usuário</th>
                <th className="p-3">Perfil</th>
                <th className="p-3">Situação</th>
                <th className="p-3 hidden md:table-cell">Cadastro</th>
                <th className="p-3 text-right">Ações</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((u) => {
                const ehProprio = usuarioLogado?.id === u.id;
                return (
                  <tr
                    key={u.id}
                    className="border-b dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    <td className="p-3 text-gray-500 dark:text-gray-400">#{u.id}</td>
                    <td className="p-3">
                      <div className="font-medium">
                        {u.nome}
                        {ehProprio && (
                          <span className="ml-2 text-xs text-gray-500 dark:text-gray-400">(você)</span>
                        )}
                      </div>
                      <div className="text-xs text-gray-500 dark:text-gray-400">{u.email}</div>
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          u.is_admin
                            ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300'
                            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300'
                        }`}
                      >
                        {u.is_admin ? 'Admin' : 'Cidadão'}
                      </span>
                    </td>
                    <td className="p-3">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          u.ativo
                            ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                            : 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300'
                        }`}
                      >
                        {u.ativo ? 'Ativo' : 'Inativo'}
                      </span>
                    </td>
                    <td className="p-3 text-sm text-gray-500 dark:text-gray-400 hidden md:table-cell">
                      {formatarData(u.criado_em)}
                    </td>
                    <td className="p-3">
                      <div className="flex justify-end gap-2">
                        <button
                          onClick={() => openEdit(u)}
                          className="p-2 text-blue-500 hover:bg-blue-50 dark:hover:bg-gray-600 rounded transition"
                          title="Editar"
                        >
                          <Edit2 size={18} />
                        </button>
                        <button
                          onClick={() => openStatus(u)}
                          disabled={ehProprio}
                          className={`p-2 rounded transition disabled:opacity-30 disabled:cursor-not-allowed ${
                            u.ativo
                              ? 'text-red-500 hover:bg-red-50 dark:hover:bg-gray-600'
                              : 'text-green-500 hover:bg-green-50 dark:hover:bg-gray-600'
                          }`}
                          title={
                            ehProprio
                              ? 'Você não pode inativar a própria conta'
                              : u.ativo
                                ? 'Inativar'
                                : 'Reativar'
                          }
                        >
                          {u.ativo ? <Power size={18} /> : <RotateCcw size={18} />}
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      <ModalAdicionarUsuario
        isOpen={isAddOpen}
        onClose={() => setIsAddOpen(false)}
        onAdd={handleAdd}
      />

      <ModalEditarUsuario
        isOpen={isEditOpen}
        onClose={() => setIsEditOpen(false)}
        usuario={usuarioSelecionado}
        ehProprioUsuario={usuarioLogado?.id === usuarioSelecionado?.id}
        onEdit={handleEdit}
      />

      <ModalStatusUsuario
        isOpen={isStatusOpen}
        onClose={() => setIsStatusOpen(false)}
        usuario={usuarioSelecionado}
        onToggleStatus={handleToggleStatus}
      />
    </div>
  );
}