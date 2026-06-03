/**
 * Core Axiom Definitions for SimpleFeed++ Information Architecture
 */

export type AxiomCategory = 'EDUCATION' | 'CAREER' | 'FINANCE' | 'LIFE_PLANNING';

export interface AxiomMetrics {
  category: AxiomCategory;
  totalIngested: number;
  triagedCount: number;
  meanTriageScore: number; // Moving average tracking vector alignment drift
  lastActivityAt: string;  // ISO timestamp
}

export interface VectorCentroidConfig {
  category: AxiomCategory;
  dimensions: number;      // Typically 1536 for text-embedding-ada-002 or 384 for miniLM
  weights: number[];       // Core architectural signature vector for the axiom
}
