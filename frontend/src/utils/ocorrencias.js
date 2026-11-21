import L from 'leaflet';

export const STATUS_CONFIG = {
  REGISTRADO: {
    label: 'Registrado',
    corHex: '#ef4444',
    badgeClass: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',
  },
  EM_ANALISE: {
    label: 'Em análise',
    corHex: '#f59e0b',
    badgeClass: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',
  },
  RESOLVIDO: {
    label: 'Resolvido',
    corHex: '#10b981',
    badgeClass: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',
  },
};

export const LISTA_STATUS = Object.entries(STATUS_CONFIG).map(([valor, cfg]) => ({
  valor,
  ...cfg,
}));

export function criarIconeMarcador(status) {
  const cor = STATUS_CONFIG[status]?.corHex || '#3b82f6';

  return L.divIcon({
    className: 'bg-transparent border-0',
    html: `
      <svg xmlns="http://www.w3.org/2000/svg" width="28" height="36" viewBox="0 0 28 36">
        <path d="M14 0C6.268 0 0 6.268 0 14c0 9.625 14 22 14 22s14-12.375 14-22C28 6.268 21.732 0 14 0z"
              fill="${cor}" stroke="#ffffff" stroke-width="2"/>
        <circle cx="14" cy="14" r="5" fill="#ffffff"/>
      </svg>
    `,
    iconSize: [28, 36],
    iconAnchor: [14, 36],
    popupAnchor: [0, -34],
  });
}

export function formatarDataHora(isoString) {
  if (!isoString) return '-';
  return new Date(isoString).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}