import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import BlockEditor from '../BlockEditor';

describe('BlockEditor Functional Engine', () => {
  it('should parse and render the initial state block matrix cleanly', () => {
    render(<BlockEditor />);
    
    // Check for our baseline architectural blocks
    expect(screen.getByText('Engineering Architecture')).toBeInTheDocument();
    expect(screen.getByText(/Welcome to the synchronized workspace context/i)).toBeInTheDocument();
    expect(screen.getByText(/Architectural Axiom:/i).parentElement).toHaveClass('block-callout');
  });

  it('should dynamically append a new empty paragraph block when the Enter key is pressed', () => {
    render(<BlockEditor />);
    
    // Target the first heading block element
    const initialHeading = screen.getByText('Engineering Architecture');
    
    // Execute a simulated browser-level keydown intercept
    fireEvent.keyDown(initialHeading, { key: 'Enter', code: 'Enter', charCode: 13 });

    // Because the custom logic hooks on Enter to append a blank block with an empty string,
    // we verify that the total editable nodes increase or that an empty placeholder is now available.
    const editableElements = screen.getAllByContentEditable();
    
    // Initial data had 3 blocks. The enter command should result in exactly 4 blocks on the DOM canvas.
    expect(editableElements).toHaveLength(4);
  });

  it('should remove an empty block when the Backspace key is triggered', () => {
    render(<BlockEditor />);
    
    const initialHeading = screen.getByText('Engineering Architecture');
    
    // 1. Fire Enter to generate the empty block node
    fireEvent.keyDown(initialHeading, { key: 'Enter' });
    let editableElements = screen.getAllByContentEditable();
    expect(editableElements).toHaveLength(4);

    // 2. The new block is appended at index 1. Target and hit Backspace while it is completely empty.
    const newEmptyBlock = editableElements[1];
    fireEvent.keyDown(newEmptyBlock, { key: 'Backspace' });

    // 3. Confirm the system array safely dropped the element out of the active loop
    editableElements = screen.getAllByContentEditable();
    expect(editableElements).toHaveLength(3);
  });
});
