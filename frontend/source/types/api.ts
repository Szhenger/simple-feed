/**
 * Network Data Transfer Envelopes and Error Schemas
 */

export interface ApiResponseEnvelope<T> {
  data: T;
  meta: {
    timestamp: string;
    shardId: string;        // Identifies source database engine instance (shard_0..shard_N)
    executionTimeMs: number;// Profiling optimization data
    apiVersion: string;
  };
}

export interface PaginatedResponse<T> {
  results: T[];
  next: string | null;
  previous: string | null;
  count: number;
}

export type ApiErrorCode = 
  | 'UNAUTHORIZED_ACCESS' 
  | 'RLS_VIOLATION' 
  | 'SHARD_OFFLINE' 
  | 'VALIDATION_FAILED' 
  | 'KERNEL_CRASH'
  | 'VECTOR_TIMEOUT';

export interface ApiErrorResponse {
  error: string;
  code: ApiErrorCode;
  details?: Record<string, string[]>; // Field-specific constraint violations
}
