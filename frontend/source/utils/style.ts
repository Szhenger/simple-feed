import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * Utility for intelligently merging Tailwind classes without conflict.
 * Ensures dynamic states (e.g., active vs inactive axiom buttons) render deterministically.
 */
export const cn = (...inputs: ClassValue[]) => {
  return twMerge(clsx(inputs));
};
