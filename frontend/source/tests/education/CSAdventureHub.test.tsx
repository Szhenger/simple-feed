import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import CSAdventureHub from '../../pages/CSAdventureHub';
import { NotionCharacterSheet } from '../../components/education/StatsDashboard';

describe('Computer Science Adventure UI', () => {

  it('renders character sheet stats and bounds levels correctly', () => {
    const mockStats = {
      algorithmic_depth: 42.5,
      systems_architecture: 15.2,
      tooling_fluency: 28.0,
      domain_specialization: 5.0
    };
    
    render(<NotionCharacterSheet stats={mockStats} />);
    
    // Check if the floor math (Level rounding) works
    expect(screen.getByText(/LVL 42/i)).toBeInTheDocument();
    expect(screen.getByText(/\(42.50\)/i)).toBeInTheDocument();
    expect(screen.getByText(/LVL 15/i)).toBeInTheDocument();
  });

  it('adds a new tracking pipeline to the active roster on submit', async () => {
    render(<CSAdventureHub />);
    
    // Initially, the active pipelines list should prompt the user to configure one
    expect(screen.getByText(/No agents deployed/i)).toBeInTheDocument();

    // Fill out the Pipeline Builder form
    fireEvent.change(screen.getByPlaceholderText(/e.g., MIT 6.824/i), {
      target: { value: 'Rust Memory Model' }
    });
    fireEvent.change(screen.getByPlaceholderText(/https:\/\//i), {
      target: { value: 'https://doc.rust-lang.org/nomicon/' }
    });

    // Submit the form
    fireEvent.click(screen.getByRole('button', { name: /Deploy Tracking Agent/i }));

    // Verify button changes to deploying state
    expect(screen.getByRole('button', { name: /Deploying Agent.../i })).toBeDisabled();

    // Wait for the mock async operation to complete
    await waitFor(() => {
      // The new pipeline should now be in the Active Roster
      expect(screen.getByText('Rust Memory Model')).toBeInTheDocument();
      expect(screen.getByText('DOCUMENTATION')).toBeInTheDocument(); // Defaults to docs
      // The "No agents deployed" message should be gone
      expect(screen.queryByText(/No agents deployed/i)).not.toBeInTheDocument();
    });
  });

});
