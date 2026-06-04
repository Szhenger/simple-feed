import axios, { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiErrorResponse, ApiErrorCode } from '../types';
import { useUIStore } from '../store/uiStore'; // To optionally pull active workspace context

/**
 * Custom Error class that mathematically aligns with our utils/error.ts translation matrix.
 */
export class SystemApiError extends Error implements ApiErrorResponse {
  public code: ApiErrorCode;
  public details?: Record<string, string[]>;

  constructor(message: string, code: ApiErrorCode, details?: Record<string, string[]>) {
    super(message);
    this.name = 'SystemApiError';
    this.code = code;
    this.details = details;
  }
}

/**
 * The core deterministic Axios client.
 * Enforces the Row-Level Security (RLS) boundary via headers.
 */
export const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10s strict timeout to prevent thread hanging
});

// Request Interceptor: Cryptographic & Tenant Identity Injection
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('sz_session_token');
    const activeWorkspaceId = localStorage.getItem('sz_active_workspace');

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Inject tenant boundary for the PostgreSQL RLS guard
    if (activeWorkspaceId) {
      config.headers['X-Workspace-ID'] = activeWorkspaceId;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor: Envelope validation and Error routing
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    // If the backend drops the ApiResponseEnvelope meta-data, we can log profiling here
    if (response.data?.meta?.executionTimeMs > 500) {
      console.warn(`[API Profiler] Slow Query detected on ${response.config.url}: ${response.data.meta.executionTimeMs}ms`);
    }
    return response;
  },
  (error: AxiosError<ApiErrorResponse>) => {
    if (error.response?.data?.code) {
      // The Python backend threw a properly formatted architectural error
      const { code, error: message, details } = error.response.data;
      throw new SystemApiError(message, code, details);
    }

    if (error.response?.status === 401 || error.response?.status === 403) {
      throw new SystemApiError("Authentication or RLS boundary failed.", 'UNAUTHORIZED_ACCESS');
    }

    if (error.code === 'ECONNABORTED' || error.response?.status === 504) {
      throw new SystemApiError("The C++ kernel or database shard exceeded latency budgets.", 'SHARD_OFFLINE');
    }

    throw new SystemApiError(error.message, 'VALIDATION_FAILED');
  }
);
