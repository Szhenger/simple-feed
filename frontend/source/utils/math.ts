/**
 * Mathematical and AI-Vector utility functions
 * Enforces the deterministic logic of the C++ and pgvector backend.
 */

const SYSTEM_TAU_THRESHOLD = 0.72;

export const formatVectorScore = (score: number): string => {
  return `τ = ${score.toFixed(2)}`;
};

export const isAxiomaticSignal = (score: number, threshold: number = SYSTEM_TAU_THRESHOLD): boolean => {
  return score >= threshold;
};

/**
 * Calculates a simple moving average for vector drift detection.
 * Useful for the Settings Dashboard to show if incoming feeds are drifting away from the centroid.
 */
export const calculateDriftAverage = (currentAverage: number, newScore: number, totalTriaged: number): number => {
  if (totalTriaged === 0) return newScore;
  return ((currentAverage * totalTriaged) + newScore) / (totalTriaged + 1);
};
