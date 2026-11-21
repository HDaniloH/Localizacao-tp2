import { useState, useEffect } from 'react';
import { MapPin, Calendar, Tag } from 'lucide-react';
import { ModalBase } from './ModalBase';
import { ocorrenciasService } from '../../services/api';
import { STATUS_CONFIG, formatarDataHora } from '../../utils/ocorrencias';

export function ModalDetalheOcorrencia({ isOpen, onClose, ocorrenciaId, mapaCategorias }) {
  const [detalhe, setDetalhe] = useState(null);
  const [carregando, setCarregando] = useState(false);
  const [erro, setErro] = useState('');

  useEffect(() => {
    if (!isOpen || !ocorrenciaId) return;

    let ativo = true;
    setCarregando(true);
    setErro('');
    setDetalhe(null);

    ocorrenciasService
      .detalhar(ocorrenciaId)
      .then((dados) => {
        if (ativo) setDetalhe(dados);
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
              <span className={`shrink-0 px-2.5 py-1 rounded-full text-xs font-semibold ${statusInfo.badgeClass}`}>
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

          <div className="flex justify-end">
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