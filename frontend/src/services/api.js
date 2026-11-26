/**
 * Camada de comunicação HTTP com a API RESTful do backend FastAPI.
 * Encapsula chamadas de autenticação, usuários, categorias e ocorrências georreferenciadas.
 * @module services/api
 */
const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('access_token');
}

function extrairMensagemErro(data, fallback) {
  if (!data) return fallback;
  if (typeof data.detail === 'string') return data.detail;
  if (data.detail && typeof data.detail.mensagem === 'string') {
    return data.detail.mensagem;
  }
  if (Array.isArray(data.detail) && data.detail.length > 0) {
    return data.detail.map((err) => err.msg).join(' | ');
  }
  return fallback;
}

async function request(endpoint, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };

  if (!(options.body instanceof URLSearchParams) && !(options.body instanceof FormData)) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }

  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    const mensagem = extrairMensagemErro(data, `Erro HTTP ${response.status}`);
    const erro = new Error(mensagem);
    erro.status = response.status;
    throw erro;
  }

  return data;
}

export const authService = {
  async login(email, senha) {
    const form = new URLSearchParams();
    form.append('username', email);
    form.append('password', senha);

    return request('/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: form,
    });
  },

  registrar({ nome, email, senha }) {
    return request('/auth/registrar', {
      method: 'POST',
      body: JSON.stringify({ nome, email, senha }),
    });
  },

  me() {
    return request('/auth/me');
  },
};

export const categoriasService = {
  listarPublicas() {
    return request('/categorias');
  },

  listarAdmin(ativa = null) {
    const query = ativa === null ? '' : `?ativa=${ativa}`;
    return request(`/admin/categorias${query}`);
  },

  criar({ nome, descricao }) {
    return request('/admin/categorias', {
      method: 'POST',
      body: JSON.stringify({ nome, descricao: descricao || null }),
    });
  },

  atualizar(id, { nome, descricao }) {
    return request(`/admin/categorias/${id}`, {
      method: 'PATCH',
      body: JSON.stringify({ nome, descricao: descricao || null }),
    });
  },

  inativar(id) {
    return request(`/admin/categorias/${id}/inativar`, {
      method: 'PATCH',
    });
  },

  reativar(id) {
    return request(`/admin/categorias/${id}/reativar`, {
      method: 'PATCH',
    });
  },
};

export const usuariosService = {
  listar(ativo = null) {
    const query = ativo === null ? '' : `?ativo=${ativo}`;
    return request(`/usuarios${query}`);
  },

  criar({ nome, email, senha, is_admin = false }) {
    return request('/usuarios', {
      method: 'POST',
      body: JSON.stringify({ nome, email, senha, is_admin }),
    });
  },

  obter(id) {
    return request(`/usuarios/${id}`);
  },

  atualizar(id, dados) {
    return request(`/usuarios/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(dados),
    });
  },

  inativar(id) {
    return request(`/usuarios/${id}`, {
      method: 'DELETE',
    });
  },
};

export const ocorrenciasService = {
  registrar({ titulo, categoria_id, descricao, latitude, longitude }) {
    return request('/ocorrencias', {
      method: 'POST',
      body: JSON.stringify({
        titulo,
        categoria_id: Number(categoria_id),
        descricao,
        latitude: Number(latitude),
        longitude: Number(longitude),
      }),
    });
  },

  listar(filtros = {}) {
    const params = new URLSearchParams();

    if (Array.isArray(filtros.categorias)) {
      filtros.categorias.forEach((id) => params.append('categorias', String(id)));
    }
    if (Array.isArray(filtros.status)) {
      filtros.status.forEach((st) => params.append('status', st));
    }
    if (filtros.inicio) params.append('inicio', filtros.inicio);
    if (filtros.fim) params.append('fim', filtros.fim);

    if (
      filtros.sul !== undefined &&
      filtros.oeste !== undefined &&
      filtros.norte !== undefined &&
      filtros.leste !== undefined
    ) {
      params.append('sul', String(filtros.sul));
      params.append('oeste', String(filtros.oeste));
      params.append('norte', String(filtros.norte));
      params.append('leste', String(filtros.leste));
    }

    if (filtros.limite !== undefined) params.append('limite', String(filtros.limite));
    if (filtros.offset !== undefined) params.append('offset', String(filtros.offset));

    const query = params.toString();
    return request(`/ocorrencias${query ? `?${query}` : ''}`);
  },

  detalhar(id) {
    return request(`/ocorrencias/${id}`);
  },
};