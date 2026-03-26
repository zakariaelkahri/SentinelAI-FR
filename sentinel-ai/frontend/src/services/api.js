import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const AUTH_STORAGE_KEY = 'sentinelai.auth';

const parseStoredAuth = () => {
  if (typeof window === 'undefined') {
    return null;
  }

  const rawAuth = window.localStorage.getItem(AUTH_STORAGE_KEY);
  if (!rawAuth) {
    return null;
  }

  try {
    return JSON.parse(rawAuth);
  } catch (error) {
    window.localStorage.removeItem(AUTH_STORAGE_KEY);
    return null;
  }
};

const getAccessToken = () => {
  const auth = parseStoredAuth();
  return auth?.accessToken || null;
};

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = getAccessToken();

  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

export const getStoredAuthSession = () => parseStoredAuth();

export const saveAuthSession = (authData) => {
  if (typeof window === 'undefined') {
    return;
  }

  const session = {
    accessToken: authData.access_token,
    tokenType: authData.token_type || 'bearer',
    expiresIn: authData.expires_in || 0,
    user: authData.user || null,
  };

  window.localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session));
};

export const clearAuthSession = () => {
  if (typeof window === 'undefined') {
    return;
  }

  window.localStorage.removeItem(AUTH_STORAGE_KEY);
};

export const authApi = {
  login: async (credentials) => {
    const response = await apiClient.post('/auth/login', credentials);
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await apiClient.get('/auth/me');
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post('/auth/logout');
    return response.data;
  },
};

export const api = {
  checkHealth: async () => {
    const response = await apiClient.get('/health');
    return response.data;
  },

  listModels: async () => {
    const response = await apiClient.get('/api/v1/models');
    return response.data;
  },

  listCameras: async () => {
    const response = await apiClient.get('/api/v1/cameras');
    return response.data;
  },

  getCameraThreatAlert: async (cameraId) => {
    const response = await apiClient.get(`/api/v1/cameras/${cameraId}/threat-alert`);
    return response.data;
  },

  adminCreateUser: async (payload) => {
    const response = await apiClient.post('/users/admin/create-user', payload);
    return response.data;
  },

  adminListUsers: async () => {
    const response = await apiClient.get('/users/admin/users');
    return response.data;
  },

  adminUpdateUser: async (userId, payload) => {
    const response = await apiClient.patch(`/users/admin/users/${userId}`, payload);
    return response.data;
  },

  adminCreateCamera: async (payload) => {
    const response = await apiClient.post('/api/v1/cameras', payload);
    return response.data;
  },

  adminUpdateCamera: async (cameraId, payload) => {
    const response = await apiClient.patch(`/api/v1/cameras/${cameraId}`, payload);
    return response.data;
  },

  adminDeleteCamera: async (cameraId) => {
    await apiClient.delete(`/api/v1/cameras/${cameraId}`);
  },

  getCameraMjpegStreamUrl: (cameraId, stream = 'raw', cacheBuster = null) => {
    const queryParams = new URLSearchParams({ stream });
    const token = getAccessToken();

    if (token) {
      queryParams.set('token', token);
    }

    if (cacheBuster !== null && cacheBuster !== undefined) {
      queryParams.set('t', String(cacheBuster));
    }

    return `${API_BASE_URL}/api/v1/cameras/${cameraId}/mjpeg?${queryParams.toString()}`;
  },

  askSecurityAssistant: async (question) => {
    const response = await apiClient.post('/api/v1/assistant/security/ask', { question });
    return response.data;
  },
};
