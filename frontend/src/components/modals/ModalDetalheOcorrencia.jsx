import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { MapPin, Calendar, Tag, Bell, BellRing, History } from 'lucide-react';
import { ModalBase } from './ModalBase';
import { ocorrenciasService, notificacoesService } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { STATUS_CONFIG, formatarDataHora } from '../../utils/ocorrencias';

/**
 * Modal de visualização dos detalhes completos de uma ocorrência (US02),
 * subscrição em alertas e histórico de eventos de status (US03).
 *
 * @param {Object} props - Propriedades do componente.
 * @param {boolean} props.isOpen - Controla a visibilidade do modal.
 * @param {Function} props.onClose - Callback executado ao fechar o modal.
 * @param {number|null} props.ocorrenciaId - Identificador da ocorrência consultada.
 * @param {Object.<number, string>} props.mapaCategorias - Mapa de ID para nome da categoria.
 * @returns {JSX.Element|null} Modal com metadados, subscrição e linha do tempo de eventos.
 */
export function ModalDetalheOcorrencia({ isOpen, onClose, ocorrenciaId, mapaCategorias }) {
  const { autenticado } = useAuth();

  const [detalhe, setDetalhe] = useState(null);
  const [logs, setLogs] = useState([]);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');

  const [inscrevendo, setInscrevendo] = useState(false);
  const [inscrito, setInscrito] = useState(false);
  const [feedbackNotificacao, setFeedbackNotificacao] = useState('');

  useEffect(() => {
    if (!isOpen || !ocorrenciaId) return;

    let ativo = true;
    setCarregando(true);
    setErro('');
    setDetalhe(null);
    setLogs([]);
    setInscrito(false);
    setFeedbackNotificacao('');

    Promise.all([
      ocorrenciasService.detalhar(ocorrenciaId),
      notificacoesService.listarLogs(ocorrenciaId).catch(() => []),
    ])
      .then(([dadosOcorrencia, listaLogs]) => {
        if (!ativo) return;
        setDetalhe(dadosOcorrencia);
        setLogs(Array.isArray(listaLogs) ? listaLogs : []);
      })
      .catch((err) => {
        if (ativo) setErro(err.message || 'Erro ao carregar detalhes da ocorrência.');
      })
      .finally(() => {
        if (ativo) setCarregando(false);
      });

    return () => {
      ativo = false;
    };
  }, [isOpen, ocorrenciaId]);

  const handleInscrever = async () => {
    if (!ocorrenciaId) return;

    setInscrevendo(true);
    setFeedbackNotificacao('');
    try {
      await notificacoesService.inscrever(ocorrenciaId);
      setInscrito(true);
      setFeedbackNotificacao('Você receberá alertas quando o status desta ocorrência mudar.');
    } catch (err) {
      setFeedbackNotificacao(err.message || 'Não foi possível ativar as notificações.');
    } finally {
      setInscrevendo(false);
    }
  };

  const statusInfo = detalhe ? STATUS_CONFIG[detalhe.status] : null;
  const nomeCategoria = detalhe
    ? mapaCategorias[detalhe.categoria_id] || `Categoria #${detalhe.categoria_id}`
    : '';

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Detalhes da Ocorrência">
      {carregando && (
        <p className="py-6 text-center text-gray-500 dark:text-gray-400">
          Carregando detalhes...
        </p>
      )}

      {erro && (
        <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
          {erro}
        </div>
      )}

      {detalhe && (
        <div className="flex flex-col gap-4">
          <div className="flex items-start justify-between gap-2">
            <h4 className="text-lg font-bold leading-snug">{detalhe.titulo}</h4>
            {statusInfo && (
              <span
                className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold ${statusInfo.badgeClass}`}
              >
                {statusInfo.label}
              </span>
            )}
          </div>

          <div className="flex flex-wrap gap-x-4 gap-y-1.5 text-xs text-gray-600 dark:text-gray-400">
            <span className="flex items-center gap-1">
              <Tag size={14} /> {nomeCategoria}
            </span>
            <span className="flex items-center gap-1">
              <Calendar size={14} /> {formatarDataHora(detalhe.criado_em)}
            </span>
            <span className="flex items-center gap-1">
              <MapPin size={14} /> {detalhe.latitude.toFixed(5)}, {detalhe.longitude.toFixed(5)}
            </span>
          </div>

          {detalhe.foto_url && (
            <img
              src={detalhe.foto_url}
              alt={detalhe.titulo}
              className="w-full max-h-56 object-cover rounded-lg border dark:border-gray-700"
            />
          )}

          <div className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700/60 text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">
            {detalhe.descricao}
          </div>

          {/* Subscrição de Notificações (US03) */}
          <div className="border-t dark:border-gray-700 pt-3 flex flex-col gap-2">
            {autenticado ? (
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs text-gray-600 dark:text-gray-400">
                  Acompanhar atualizações desta ocorrência:
                </span>
                <button
                  type="button"
                  onClick={handleInscrever}
                  disabled={inscrevendo || inscrito}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition ${
                    inscrito
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300 cursor-default'
                      : 'bg-blue-600 text-white hover:bg-blue-700 disabled:opacity-60'
                  }`}
                >
                  {inscrito ? <BellRing size={14} /> : <Bell size={14} />}
                  {inscrevendo
                    ? 'Inscrevendo...'
                    : inscrito
                      ? 'Acompanhando'
                      : 'Receber alertas'}
                </button>
              </div>
            ) : (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                <Link to="/login" onClick={onClose} className="text-blue-600 dark:text-blue-400 hover:underline">
                  Entre na sua conta
                </Link>{' '}
                para receber alertas sobre esta ocorrência.
              </p>
            )}

            {feedbackNotificacao && (
              <p
                className={`text-xs ${
                  inscrito
                    ? 'text-green-700 dark:text-green-300'
                    : 'text-red-600 dark:text-red-400'
                }`}
              >
                {feedbackNotificacao}
              </p>
            )}
          </div>

          {/* Histórico de Mudanças de Status (US03) */}
          <div className="border-t dark:border-gray-700 pt-3">
            <h5 className="flex items-center gap-1.5 text-xs font-semibold text-gray-700 dark:text-gray-300 mb-2">
              <History size={14} /> Histórico de Atualizações
            </h5>

            {logs.length === 0 ? (
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Nenhuma mudança de status registrada até o momento.
              </p>
            ) : (
              <ul className="flex flex-col gap-2 max-h-36 overflow-y-auto pr-1">
                {logs.map((log) => {
                  const novoCfg = STATUS_CONFIG[log.status_novo];
                  return (
                    <li
                      key={log.id}
                      className="p-2 rounded-lg bg-gray-50 dark:bg-gray-700/50 text-xs flex flex-col gap-0.5"
                    >
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-semibold text-gray-800 dark:text-gray-200">
                          {novoCfg ? novoCfg.label : log.status_novo}
                        </span>
                        <span className="text-gray-500 dark:text-gray-400">
                          {formatarDataHora(log.registrado_em)}
                        </span>
                      </div>
                      <span className="text-gray-600 dark:text-gray-300">{log.mensagem}</span>
                    </li>
                  );
                })}
              </ul>
            )}
          </div>

          <div className="flex justify-end pt-1">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg text-sm font-medium transition"
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </ModalBase>
  );
}