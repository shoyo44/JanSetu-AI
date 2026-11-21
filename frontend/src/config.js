const trimTrailingSlash = (value) => value ? value.replace(/\/+$/, '') : '';

const envApiBase = import.meta.env.VITE_API_BASE_URL;
const envWsBase = import.meta.env.VITE_WS_BASE_URL;

// Check if running in Vite dev server (port 5173 on localhost)
const isViteDev = typeof window !== 'undefined' && window.location.port === '5173';

// When served in production/container (via Nginx reverse proxy), use relative '/api/v1'
// so all requests seamlessly match the current host and port (e.g. EC2 public IP or custom domain).
// When in local Vite dev server, route directly to the backend at port 8000.
const defaultApiBase = isViteDev ? 'http://127.0.0.1:8000/api/v1' : '/api/v1';

export const API_BASE = trimTrailingSlash(
  envApiBase && !envApiBase.includes('onrender.com') ? envApiBase : defaultApiBase
);

const getWsBase = () => {
  if (envWsBase && !envWsBase.includes('onrender.com')) {
    return trimTrailingSlash(envWsBase);
  }
  if (typeof window !== 'undefined') {
    if (isViteDev) {
      return 'ws://127.0.0.1:8000/api/v1';
    }
    const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${proto}//${window.location.host}/api/v1`;
  }
  return 'ws://127.0.0.1:8000/api/v1';
};

export const WS_BASE = getWsBase();

export const TENANT_ID = import.meta.env.VITE_TENANT_ID || 'tenant-123';
