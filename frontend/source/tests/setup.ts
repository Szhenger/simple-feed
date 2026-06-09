import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach } from 'vitest';

// Automatically unmount and clean up the DOM tree after each isolated execution
afterEach(() => {
  cleanup();
});
