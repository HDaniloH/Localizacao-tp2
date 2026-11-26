import { useState, useEffect } from 'react';
import { Crosshair, MapPin } from 'lucide-react';
import { ModalBase } from './ModalBase';

/**
 * Modal de formulário para registro de uma nova ocorrência georreferenciada (US01).
 * Suporta captura automática de coordenadas via API de Geolocalização do navegador
 * ou seleção manual de ponto diretamente no mapa.
 *
 * @param {Object} props - Propriedades do componente.
 * @param {boolean} props.isOpen - Controla a visibilidade do modal.
 * @param {Function} props.onClose - Callback executado ao fechar o modal.
 * @param {Array<Object>} props.categorias - Lista de categorias ativas disponíveis.
 * @param {{lat: number, lng: number}|null} props.coordenadasIniciais - Coordenadas pré-selecionadas no mapa.
 * @param {Function} props.onEscolherNoMapa - Ativa o modo de seleção de ponto no mapa.
 * @param {Function} props.onRegistrar - Submete os dados da nova ocorrência para a API.
 * @returns {JSX.Element|null} Formulário modal de registro de ocorrência.
 */
export function ModalRegistrarOcorrencia({
  isOpen,
  onClose,
  categorias,
  coordenadasIniciais,
  onEscolherNoMapa,
  onRegistrar,
}) {
  const [titulo, setTitulo] = useState('');
  const [categoriaId, setCategoriaId] = useState('');
  const [descricao, setDescricao] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [erro, setErro] = useState('');
  const [buscandoGps, setBuscandoGps] = useState(false);
  const [enviando, setEnviando] = useState(false);

  useEffect(() => {
    if (coordenadasIniciais) {
      setLatitude(String(coordenadasIniciais.lat.toFixed(6)));
      setLongitude(String(coordenadasIniciais.lng.toFixed(6)));
    }
  }, [coordenadasIniciais]);

  useEffect(() => {
    if (isOpen && !categoriaId && categorias.length > 0) {
      setCategoriaId(String(categorias[0].id));
    }
  }, [isOpen, categorias, categoriaId]);

  const handleUsarGps = () => {
    if (!navigator.geolocation) {
      setErro('Geolocalização não é suportada neste navegador.');
      return;
    }

    setErro('');
    setBuscandoGps(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setLatitude(String(pos.coords.latitude.toFixed(6)));
        setLongitude(String(pos.coords.longitude.toFixed(6)));
        setBuscandoGps(false);
      },
      () => {
        setErro('Não foi possível obter sua localização. Verifique a permissão de GPS ou clique no mapa.');
        setBuscandoGps(false);
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErro('');

    const latNum = Number(latitude);
    const lngNum = Number(longitude);

    if (!titulo.trim()) {
      setErro('Informe o título da ocorrência.');
      return;
    }
    if (!categoriaId) {
      setErro('Selecione uma categoria.');
      return;
    }
    if (!descricao.trim()) {
      setErro('Descreva o problema encontrado.');
      return;
    }
    if (Number.isNaN(latNum) || Number.isNaN(lngNum) || latitude === '' || longitude === '') {
      setErro('Defina a localização usando o GPS ou clicando no mapa.');
      return;
    }

    setEnviando(true);
    try {
      await onRegistrar({
        titulo: titulo.trim(),
        categoria_id: Number(categoriaId),
        descricao: descricao.trim(),
        latitude: latNum,
        longitude: lngNum,
      });
      setTitulo('');
      setDescricao('');
      setLatitude('');
      setLongitude('');
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao registrar ocorrência.');
    } finally {
      setEnviando(false);
    }
  };

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Registrar Ocorrência">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
        {erro && (
          <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
            {erro}
          </div>
        )}

        <div>
          <label className="block mb-1 text-sm font-medium">Título</label>
          <input
            type="text"
            value={titulo}
            onChange={(e) => setTitulo(e.target.value)}
            placeholder="Ex: Buraco próximo à faixa de pedestres"
            maxLength={120}
            className="w-full p-2.5 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
            required
          />
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Categoria</label>
          <select
            value={categoriaId}
            onChange={(e) => setCategoriaId(e.target.value)}
            className="w-full p-2.5 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none text-sm"
            required
          >
            {categorias.length === 0 ? (
              <option value="">Nenhuma categoria ativa</option>
            ) : (
              categorias.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.nome}
                </option>
              ))
            )}
          </select>
        </div>

        <div>
          <label className="block mb-1 text-sm font-medium">Descrição</label>
          <textarea
            value={descricao}
            onChange={(e) => setDescricao(e.target.value)}
            placeholder="Detalhe o problema e pontos de referência..."
            maxLength={2000}
            rows={3}
            className="w-full p-2.5 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-none"
            required
          />
        </div>

        <div className="border-t dark:border-gray-700 pt-3">
          <div className="flex items-center justify-between mb-2">
            <label className="text-sm font-medium">Localização</label>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={handleUsarGps}
                disabled={buscandoGps}
                className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-blue-50 text-blue-700 hover:bg-blue-100 dark:bg-blue-900/40 dark:text-blue-300 transition"
              >
                <Crosshair size={14} />
                {buscandoGps ? 'Buscando...' : 'Usar GPS'}
              </button>
              <button
                type="button"
                onClick={onEscolherNoMapa}
                className="flex items-center gap-1 text-xs px-2.5 py-1.5 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 transition"
              >
                <MapPin size={14} />
                Marcar no mapa
              </button>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-0.5">Latitude</label>
              <input
                type="number"
                step="any"
                value={latitude}
                onChange={(e) => setLatitude(e.target.value)}
                placeholder="-15.7942"
                className="w-full p-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 text-sm outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-xs text-gray-500 dark:text-gray-400 mb-0.5">Longitude</label>
              <input
                type="number"
                step="any"
                value={longitude}
                onChange={(e) => setLongitude(e.target.value)}
                placeholder="-47.8822"
                className="w-full p-2 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 text-sm outline-none"
                required
              />
            </div>
          </div>
        </div>

        <div className="flex justify-end gap-2 mt-2">
          <button
            type="button"
            onClick={onClose}
            disabled={enviando}
            className="px-4 py-2 text-gray-600 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-gray-700 rounded-lg transition text-sm"
          >
            Cancelar
          </button>
          <button
            type="submit"
            disabled={enviando || categorias.length === 0}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-60 transition text-sm font-medium"
          >
            {enviando ? 'Enviando...' : 'Registrar'}
          </button>
        </div>
      </form>
    </ModalBase>
  );
}