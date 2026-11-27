import { useState, useEffect } from 'react';
import { Crosshair, MapPin } from 'lucide-react';
import { MapContainer, TileLayer, Marker, useMap, useMapEvents } from 'react-leaflet';
import { ModalBase } from './ModalBase';
import { criarIconeMarcador } from '../../utils/ocorrencias';

const CENTRO_PADRAO = [-15.7942, -47.8822];

function ControladorMiniMapa({ centro, onSelecionar }) {
  const map = useMap();

  useEffect(() => {
    const timer = setTimeout(() => {
      map.invalidateSize();
    }, 100);
    return () => clearTimeout(timer);
  }, [map]);

  useEffect(() => {
    if (centro) {
      map.setView(centro, Math.max(map.getZoom(), 15));
    }
  }, [map, centro]);

  useMapEvents({
    click(e) {
      onSelecionar(e.latlng);
    },
  });

  return null;
}

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
  const [avisoGps, setAvisoGps] = useState('');
  const [buscandoGps, setBuscandoGps] = useState(false);
  const [enviando, setEnviando] = useState(false);

  const aplicarCoordenadas = (lat, lng) => {
    setLatitude(String(Number(lat).toFixed(6)));
    setLongitude(String(Number(lng).toFixed(6)));
  };

  useEffect(() => {
    if (coordenadasIniciais) {
      aplicarCoordenadas(coordenadasIniciais.lat, coordenadasIniciais.lng);
      setAvisoGps('');
    }
  }, [coordenadasIniciais]);

  useEffect(() => {
    if (isOpen && !categoriaId && categorias.length > 0) {
      setCategoriaId(String(categorias[0].id));
    }
  }, [isOpen, categorias, categoriaId]);

  const buscarLocalizacaoPorRede = async () => {
    const resp = await fetch('https://ipwho.is/');
    if (!resp.ok) throw new Error('Falha na consulta de rede');
    const dados = await resp.json();
    if (!dados.success || typeof dados.latitude !== 'number' || typeof dados.longitude !== 'number') {
      throw new Error('Coordenadas indisponíveis');
    }
    return { lat: dados.latitude, lng: dados.longitude };
  };

  const limparFormulario = () => {
    setTitulo('');
    setDescricao('');
    setLatitude('');
    setLongitude('');
    setErro('');
    setAvisoGps('');
  };

  const handleFechar = () => {
    limparFormulario();
    onClose();
  };

  const handleUsarGps = () => {
    setErro('');
    setAvisoGps('');
    setBuscandoGps(true);

    const tentarFallbackRede = async (motivo) => {
      try {
        const coords = await buscarLocalizacaoPorRede();
        aplicarCoordenadas(coords.lat, coords.lng);
        setAvisoGps(
          `${motivo} Localização aproximada obtida pela rede — clique no mini-mapa abaixo para ajustar o ponto exato.`
        );
      } catch {
        setErro(
          `${motivo} Clique diretamente no mini-mapa abaixo ou use "Marcar no mapa" para definir o local.`
        );
      } finally {
        setBuscandoGps(false);
      }
    };

    if (!navigator.geolocation) {
      tentarFallbackRede('Seu navegador não possui suporte a GPS.');
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        aplicarCoordenadas(pos.coords.latitude, pos.coords.longitude);
        setBuscandoGps(false);
      },
      (err) => {
        const motivos = {
          1: 'Permissão de localização negada no navegador.',
          2: 'O sistema não conseguiu obter sinal de GPS.',
          3: 'Tempo esgotado ao buscar localização pelo navegador.',
        };
        tentarFallbackRede(motivos[err.code] || 'Não foi possível obter localização exata.');
      },
      { enableHighAccuracy: false, timeout: 8000, maximumAge: 60000 }
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
      setErro('Defina a localização clicando no mapa ou usando o GPS.');
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
      limparFormulario();
      onClose();
      setTitulo('');
      setDescricao('');
      setLatitude('');
      setLongitude('');
      setAvisoGps('');
      onClose();
    } catch (err) {
      setErro(err.message || 'Erro ao registrar ocorrência.');
    } finally {
      setEnviando(false);
    }
  };

  const coordsValidas =
    latitude !== '' &&
    longitude !== '' &&
    !Number.isNaN(Number(latitude)) &&
    !Number.isNaN(Number(longitude));

  const centroMiniMapa = coordsValidas ? [Number(latitude), Number(longitude)] : null;

  return (
    <ModalBase isOpen={isOpen} onClose={onClose} title="Registrar Ocorrência">
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
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
            rows={2}
            className="w-full p-2.5 border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600 focus:ring-2 focus:ring-blue-500 outline-none text-sm resize-none"
            required
          />
        </div>

        <div className="border-t dark:border-gray-700 pt-3 flex flex-col gap-2">
          <div className="flex items-center justify-between">
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
                Tela cheia
              </button>
            </div>
          </div>

          {avisoGps && (
            <p className="text-xs p-2 rounded-lg bg-amber-50 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300">
              {avisoGps}
            </p>
          )}

          <div className="overflow-hidden rounded-lg border dark:border-gray-600">
            <MapContainer
              center={centroMiniMapa || CENTRO_PADRAO}
              zoom={centroMiniMapa ? 15 : 12}
              className="w-full h-40 cursor-crosshair z-0"
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              <ControladorMiniMapa
                centro={centroMiniMapa}
                onSelecionar={(latlng) => {
                  setAvisoGps('');
                  aplicarCoordenadas(latlng.lat, latlng.lng);
                }}
              />
              {centroMiniMapa && (
                <Marker position={centroMiniMapa} icon={criarIconeMarcador('SELECAO')} />
              )}
            </MapContainer>
          </div>
          <span className="text-[11px] text-gray-500 dark:text-gray-400">
            Clique em qualquer ponto do mini-mapa acima para definir ou alterar o local.
          </span>

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

        <div className="flex justify-end gap-2 mt-1">
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