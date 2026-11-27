import { useState, useEffect, useCallback, useMemo } from 'react';
import { Link } from 'react-router-dom';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import { Plus, Filter, X, RefreshCw } from 'lucide-react';
import { categoriasService, ocorrenciasService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import {
  STATUS_CONFIG,
  LISTA_STATUS,
  criarIconeMarcador,
  formatarDataHora,
} from '../utils/ocorrencias';
import { ModalRegistrarOcorrencia } from '../components/modals/ModalRegistrarOcorrencia';
import { ModalDetalheOcorrencia } from '../components/modals/ModalDetalheOcorrencia';

const CENTRO_PADRAO = [-15.7942, -47.8822];

function EventosMapa({ filtrarPorArea, onClicarMapa, onMoverMapa }) {
  useMapEvents({
    click(e) {
      if (e.originalEvent?.target?.closest?.('.leaflet-popup, .leaflet-marker-icon')) {
        return;
      }
      onClicarMapa(e.latlng);
    },
    moveend(e) {
      if (!filtrarPorArea) return;
      const bounds = e.target.getBounds();
      onMoverMapa({
        sul: bounds.getSouth(),
        oeste: bounds.getWest(),
        norte: bounds.getNorth(),
        leste: bounds.getEast(),
      });
    },
  });
  return null;
}

/**
 * Página principal com o mapa interativo de ocorrências urbanas (US01 e US02).
 * Permite filtrar ocorrências por categoria, status e área visível (bounding box),
 * visualizar detalhes e acionar o registro de novas ocorrências via GPS ou clique no mapa.
 *
 * @returns {JSX.Element} Interface completa do mapa interativo e barra de filtros.
 */
export function MapaOcorrencias() {
  const { autenticado } = useAuth();

  const [ocorrencias, setOcorrencias] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [carregando, setCarregando] = useState(true);
  const [erro, setErro] = useState('');

  const [mostrarFiltros, setMostrarFiltros] = useState(false);
  const [categoriasSelecionadas, setCategoriasSelecionadas] = useState([]);
  const [statusSelecionados, setStatusSelecionados] = useState([]);
  const [dataInicio, setDataInicio] = useState('');
  const [dataFim, setDataFim] = useState('');
  const [filtrarPorArea, setFiltrarPorArea] = useState(false);
  const [limitesMapa, setLimitesMapa] = useState(null);

  const [isRegistrarOpen, setIsRegistrarOpen] = useState(false);
  const [modoSelecao, setModoSelecao] = useState(false);
  const [pontoSelecionado, setPontoSelecionado] = useState(null);
  const [ocorrenciaDetalheId, setOcorrenciaDetalheId] = useState(null);

  const mapaCategorias = useMemo(() => {
    const mapa = {};
    categorias.forEach((c) => {
      mapa[c.id] = c.nome;
    });
    return mapa;
  }, [categorias]);

  

  useEffect(() => {
    categoriasService
      .listarPublicas()
      .then(setCategorias)
      .catch(() => {});
  }, []);

  const carregarOcorrencias = useCallback(async () => {
    setCarregando(true);
    setErro('');

    try {
      const filtros = {};

      if (categoriasSelecionadas.length > 0) {
        filtros.categorias = categoriasSelecionadas;
      }
      if (statusSelecionados.length > 0) {
        filtros.status = statusSelecionados;
      }
      if (dataInicio) {
        filtros.inicio = new Date(`${dataInicio}T00:00:00`).toISOString();
      }
      if (dataFim) {
        filtros.fim = new Date(`${dataFim}T23:59:59.999`).toISOString();
      }
      if (filtrarPorArea && limitesMapa) {
        Object.assign(filtros, limitesMapa);
      }

      const resposta = await ocorrenciasService.listar(filtros);
      setOcorrencias(resposta.itens || []);
    } catch (err) {
      setErro(err.message || 'Erro ao buscar ocorrências.');
    } finally {
      setCarregando(false);
    }
  }, [
    categoriasSelecionadas,
    statusSelecionados,
    dataInicio,
    dataFim,
    filtrarPorArea,
    limitesMapa,
  ]);

  useEffect(() => {
    carregarOcorrencias();
  }, [carregarOcorrencias]);

  const alternarItem = (lista, setLista, valor) => {
    setLista((atual) =>
      atual.includes(valor) ? atual.filter((item) => item !== valor) : [...atual, valor]
    );
  };

  const limparFiltros = () => {
    setCategoriasSelecionadas([]);
    setStatusSelecionados([]);
    setDataInicio('');
    setDataFim('');
    setFiltrarPorArea(false);
  };

  const handleClicarMapa = (latlng) => {
    setPontoSelecionado(latlng);
    if (modoSelecao) {
      setModoSelecao(false);
      setIsRegistrarOpen(true);
    }
  };

  const handleRegistrar = async (dados) => {
    await ocorrenciasService.registrar(dados);
    setPontoSelecionado(null);
    await carregarOcorrencias();
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold">Mapa de Ocorrências Urbanas</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {carregando
              ? 'Atualizando ocorrências...'
              : `${ocorrencias.length} ocorrência(s) exibida(s)`}
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={() => setMostrarFiltros((prev) => !prev)}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition ${
              mostrarFiltros
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200'
            }`}
          >
            <Filter size={16} />
            Filtros
          </button>

          <button
            type="button"
            onClick={carregarOcorrencias}
            className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-200 transition"
            title="Atualizar mapa"
          >
            <RefreshCw size={16} className={carregando ? 'animate-spin' : ''} />
          </button>

          {autenticado ? (
            <button
              type="button"
              onClick={() => {
                setModoSelecao(false);
                setIsRegistrarOpen(true);
              }}
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 text-sm font-medium transition"
            >
              <Plus size={18} />
              Nova Ocorrência
            </button>
          ) : (
            <Link
              to="/login"
              className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 text-white hover:bg-blue-700 text-sm font-medium transition"
            >
              Entrar para registrar
            </Link>
          )}
        </div>
      </div>

      {mostrarFiltros && (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow p-4 flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">Filtrar ocorrências</h3>
            <button
              type="button"
              onClick={limparFiltros}
              className="text-xs text-blue-600 dark:text-blue-400 hover:underline"
            >
              Limpar filtros
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <span className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                Status (vazio = ativas)
              </span>
              <div className="flex flex-wrap gap-1.5">
                {LISTA_STATUS.map((st) => {
                  const ativo = statusSelecionados.includes(st.valor);
                  return (
                    <button
                      key={st.valor}
                      type="button"
                      onClick={() => alternarItem(statusSelecionados, setStatusSelecionados, st.valor)}
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
                        ativo
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-gray-50 text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'
                      }`}
                    >
                      {st.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <span className="block text-xs font-medium text-gray-500 dark:text-gray-400 mb-1.5">
                Categorias
              </span>
              <div className="flex flex-wrap gap-1.5 max-h-24 overflow-y-auto">
                {categorias.map((cat) => {
                  const selecionada = categoriasSelecionadas.includes(cat.id);
                  return (
                    <button
                      key={cat.id}
                      type="button"
                      onClick={() =>
                        alternarItem(categoriasSelecionadas, setCategoriasSelecionadas, cat.id)
                      }
                      className={`px-2.5 py-1 rounded-full text-xs font-medium border transition ${
                        selecionada
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-gray-50 text-gray-700 border-gray-300 dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'
                      }`}
                    >
                      {cat.nome}
                    </button>
                  );
                })}
              </div>
            </div>

            <div className="flex flex-col gap-2">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                    De
                  </label>
                  <input
                    type="date"
                    value={dataInicio}
                    onChange={(e) => setDataInicio(e.target.value)}
                    className="w-full p-1.5 text-xs border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600"
                  />
                </div>
                <div>
                  <label className="block text-xs text-gray-500 dark:text-gray-400 mb-0.5">
                    Até
                  </label>
                  <input
                    type="date"
                    value={dataFim}
                    onChange={(e) => setDataFim(e.target.value)}
                    className="w-full p-1.5 text-xs border rounded-lg bg-gray-50 dark:bg-gray-700 dark:border-gray-600"
                  />
                </div>
              </div>

              <label className="flex items-center gap-2 text-xs cursor-pointer select-none">
                <input
                  type="checkbox"
                  checked={filtrarPorArea}
                  onChange={(e) => setFiltrarPorArea(e.target.checked)}
                  className="rounded border-gray-300 text-blue-600"
                />
                <span>Filtrar apenas pela área visível do mapa</span>
              </label>
            </div>
          </div>
        </div>
      )}

      {modoSelecao && (
        <div className="p-3 rounded-xl bg-blue-600 text-white flex items-center justify-between text-sm shadow">
          <span>Clique em qualquer ponto do mapa para definir o local da ocorrência.</span>
          <button
            type="button"
            onClick={() => setModoSelecao(false)}
            className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-blue-700 hover:bg-blue-800 text-xs"
          >
            <X size={14} /> Cancelar
          </button>
        </div>
      )}

      {erro && (
        <div className="p-3 rounded-lg bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300 text-sm">
          {erro}
        </div>
      )}

      <div className="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden relative z-0">
        <MapContainer
          center={CENTRO_PADRAO}
          zoom={12}
          className={`w-full h-[65vh] min-h-[420px] ${modoSelecao ? 'cursor-crosshair' : ''}`}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          <EventosMapa
            filtrarPorArea={filtrarPorArea}
            onClicarMapa={handleClicarMapa}
            onMoverMapa={setLimitesMapa}
          />

          {pontoSelecionado && (
            <Marker
              position={[pontoSelecionado.lat, pontoSelecionado.lng]}
              icon={criarIconeMarcador('SELECAO')}
            >
              <Popup>
                <div
                  className="text-gray-800 text-xs flex flex-col gap-1.5"
                  onClick={(e) => {
                    e.stopPropagation();
                    e.nativeEvent?.stopImmediatePropagation?.();
                  }}
                >
                  <span className="font-semibold">Local selecionado</span>
                  <span>
                    {pontoSelecionado.lat.toFixed(5)}, {pontoSelecionado.lng.toFixed(5)}
                  </span>
                  {autenticado && (
                    <div className="mt-1 flex gap-1.5">
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          e.nativeEvent?.stopImmediatePropagation?.();
                          setIsRegistrarOpen(true);
                        }}
                        className="py-1 px-2.5 bg-green-600 text-white rounded font-medium hover:bg-green-700 transition"
                      >
                        Registrar aqui
                      </button>
                      <button
                        type="button"
                        onClick={(e) => {
                          e.stopPropagation();
                          e.nativeEvent?.stopImmediatePropagation?.();
                          setPontoSelecionado(null);
                        }}
                        className="py-1 px-2 bg-gray-200 text-gray-700 rounded font-medium hover:bg-gray-300 transition"
                      >
                        Remover
                      </button>
                    </div>
                  )}
                </div>
              </Popup>
            </Marker>
          )}

          {ocorrencias.map((oc) => {
            const st = STATUS_CONFIG[oc.status] || STATUS_CONFIG.REGISTRADO;
            return (
              <Marker
                key={oc.id}
                position={[oc.latitude, oc.longitude]}
                icon={criarIconeMarcador(oc.status)}
              >
                <Popup>
                  <div className="text-gray-800 min-w-[180px] flex flex-col gap-1.5">
                    <span className="font-bold text-sm leading-snug">{oc.titulo}</span>
                    <span className="text-xs text-gray-500">
                      {mapaCategorias[oc.categoria_id] || `Categoria #${oc.categoria_id}`}
                    </span>
                    <div className="flex items-center justify-between gap-2 text-xs">
                      <span className={`px-2 py-0.5 rounded-full font-semibold ${st.badgeClass}`}>
                        {st.label}
                      </span>
                      <span className="text-gray-400">{formatarDataHora(oc.criado_em)}</span>
                    </div>
                    <button
                      type="button"
                      onClick={() => setOcorrenciaDetalheId(oc.id)}
                      className="mt-1 w-full py-1 px-2.5 bg-blue-600 text-white rounded text-xs font-medium hover:bg-blue-700 transition"
                    >
                      Ver detalhes
                    </button>
                  </div>
                </Popup>
              </Marker>
            );
          })}

        </MapContainer>

        <div className="px-4 py-2.5 border-t dark:border-gray-700 flex flex-wrap items-center gap-4 text-xs text-gray-600 dark:text-gray-300">
          <span className="font-medium">Legenda:</span>
          {LISTA_STATUS.map((st) => (
            <span key={st.valor} className="flex items-center gap-1.5">
              <span
                className="w-3 h-3 rounded-full inline-block"
                style={{ backgroundColor: st.corHex }}
              />
              {st.label}
            </span>
          ))}
        </div>
      </div>

      <ModalRegistrarOcorrencia
        isOpen={isRegistrarOpen}
        onClose={() => {
          setIsRegistrarOpen(false);
          setPontoSelecionado(null);
        }}
        categorias={categorias}
        coordenadasIniciais={pontoSelecionado}
        onEscolherNoMapa={() => {
          setIsRegistrarOpen(false);
          setModoSelecao(true);
        }}
        onRegistrar={handleRegistrar}
      />

      <ModalDetalheOcorrencia
        isOpen={Boolean(ocorrenciaDetalheId)}
        onClose={() => setOcorrenciaDetalheId(null)}
        ocorrenciaId={ocorrenciaDetalheId}
        mapaCategorias={mapaCategorias}
      />
    </div>
  );
}