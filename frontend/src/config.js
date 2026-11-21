const trimTrailingSlash = (value) => value ? value.replace(/\/+$/, '') : '';

// If running locally, automatically connect to the active local backend server
const isLocalDev = typeof window !== 'undefined' && (
  window.location.hostname === 'localhost' || 
  window.location.hostname === '127.0.0.1'
);

const envApiBase = import.meta.env.VITE_API_BASE_URL;
const envWsBase = import.meta.env.VITE_WS_BASE_URL;

export const API_BASE = trimTrailingSlash(
  isLocalDev
    ? (envApiBase && !envApiBase.includes('onrender.com') ? envApiBase : 'http://127.0.0.1:8000/api/v1')
    : (envApiBase || 'http://127.0.0.1:8000/api/v1')
);

export const WS_BASE = trimTrailingSlash(
  isLocalDev
    ? (envWsBase && !envWsBase.includes('onrender.com') ? envWsBase : 'ws://127.0.0.1:8000/api/v1')
    : (envWsBase || API_BASE.replace(/^http/, 'ws'))
);

export const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'tenant-123';
