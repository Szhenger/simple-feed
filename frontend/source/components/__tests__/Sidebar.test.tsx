import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import Sidebar from '../Sidebar';

describe('Sidebar Component Context', () => {
  it('should visually highlight the active view button via the CSS class', () => {
    render(<Sidebar activeView="doc" setActiveView={vi.fn()} />);
    
    const docButton = screen.getByText(/Engineering Architecture/i);
    const metricsButton = screen.getByText(/Vector Metrics/i);

    expect(docButton).toHaveClass('active');
    expect(metricsButton).not.toHaveClass('active');
  });

  it('should trigger the state modifier callback with the correct target string on user click', async () => {
    const mockSetActiveView = vi.fn();
    const user = userEvent.setup();

    render(<Sidebar activeView="doc" setActiveView={mockSetActiveView} />);
    
    const metricsButton = screen.getByText(/Vector Metrics/i);
    await user.click(metricsButton);

    // Verify the integration boundary contract was preserved perfectly
    expect(mockSetActiveView).toHaveBeenCalledTimes(1);
    expect(mockSetActiveView).toHaveBeenCalledWith('metrics');
  });
});
