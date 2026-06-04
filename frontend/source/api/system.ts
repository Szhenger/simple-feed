import { apiClient } from './client';
import { ApiResponseEnvelope } from '../types';

export interface TelemetryMetrics {
  activeWorkers: number;
  kernelLoaded: boolean;
  currentVectorThreshold: number;
  activeDatabasePartition: string;
}

export const SystemAPI = {
  /**
   * Fetches internal infrastructure telemetry for the Settings Dashboard.
   */
  async getTelemetry(): Promise<TelemetryMetrics> {
    const { data } = await apiClient.get<ApiResponseEnvelope<TelemetryMetrics>>('/system/telemetry');
    return data.data;
  },

  /**
   * Adjusts the mathematical threshold for the pgvector cosine similarity index.
   */
  async updateVectorThreshold(tau: number): Promise<void> {
    if (tau < 0.5 || tau > 0.99) throw new Error("Threshold out of architectural bounds.");
    await apiClient.put('/system/vector-config', { threshold: tau });
  },
  
  /**
   * Triggers a C++ parsing kernel diagnostic health-check.
   */
  async pingKernel(): Promise<boolean> {
    const { status } = await apiClient.get('/system/kernel-health');
    return status === 200;
  }
};
