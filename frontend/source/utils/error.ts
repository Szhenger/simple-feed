import { ApiErrorCode, ApiErrorResponse } from '../types';

/**
 * Maps strict backend architectural errors to actionable UI states.
 */

const ERROR_DICTIONARY: Record<ApiErrorCode, string> = {
  UNAUTHORIZED_ACCESS: "Authentication boundary failed. JWT signature invalid or expired.",
  RLS_VIOLATION: "Security Exception: Attempted to access memory space outside your active Workspace ID (Row-Level Security violation).",
  SHARD_OFFLINE: "Database Engine Exception: The primary shard hosting this workspace is currently unreachable.",
  VALIDATION_FAILED: "Payload rejection: The data structure does not match the strict schema requirements.",
  KERNEL_CRASH: "C++ Ingestion Fault: The native parsing kernel encountered a fatal memory segment error.",
  VECTOR_TIMEOUT: "pgvector Exception: Embedding proximity calculation exceeded the maximum allowed latency."
};

export const translateApiError = (errorResponse: ApiErrorResponse): string => {
  const baseMessage = ERROR_DICTIONARY[errorResponse.code] || "An unknown architectural fault occurred.";
  
  // Append specific field violations if the API provided them
  if (errorResponse.details && Object.keys(errorResponse.details).length > 0) {
    const specifics = Object.entries(errorResponse.details)
      .map(([field, issues]) => `${field}: ${issues.join(', ')}`)
      .join(' | ');
    return `${baseMessage} [Details: ${specifics}]`;
  }

  return baseMessage;
};
