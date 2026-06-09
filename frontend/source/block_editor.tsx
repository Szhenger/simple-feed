import React, { useState, useRef, useEffect } from 'react';

// Define the mathematical shape of our data
export interface Block {
  id: string;
  type: 'h1' | 'h2' | 'p' | 'callout';
  content: string;
}

const INITIAL_BLOCKS: Block[] = [
  { id: '1', type: 'h1', content: 'Engineering Architecture' },
  { id: '2', type: 'p', content: 'Welcome to the synchronized workspace context.' },
  { id: '3', type: 'callout', content: 'Architectural Axiom: The similarity engine strictly filters outbound database entities down to a hard constraint threshold of \\tau \\ge 0.72.' },
];

export default function BlockEditor() {
  const [blocks, setBlocks] = useState<Block[]>(INITIAL_BLOCKS);

  const updateBlock = (id: string, newContent: string) => {
    setBlocks(blocks.map(b => b.id === id ? { ...b, content: newContent } : b));
  };

  const handleKeyDown = (e: React.KeyboardEvent, index: number, blockId: string) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      // Insert a new empty paragraph block directly after the current one
      const newBlock: Block = { id: Date.now().toString(), type: 'p', content: '' };
      const newBlocks = [...blocks];
      newBlocks.splice(index + 1, 0, newBlock);
      setBlocks(newBlocks);
    }
    
    if (e.key === 'Backspace' && blocks[index].content === '' && blocks.length > 1) {
      e.preventDefault();
      // Delete empty block
      setBlocks(blocks.filter(b => b.id !== blockId));
    }
  };

  return (
    <article className="notion-canvas">
      {blocks.map((block, index) => (
        <BlockRenderer 
          key={block.id} 
          block={block} 
          onChange={(content) => updateBlock(block.id, content)}
          onKeyDown={(e) => handleKeyDown(e, index, block.id)}
        />
      ))}
    </article>
  );
}

// Sub-component to render individual node types
function BlockRenderer({ block, onChange, onKeyDown }: { 
  block: Block, 
  onChange: (c: string) => void,
  onKeyDown: (e: React.KeyboardEvent) => void 
}) {
  const contentEditableRef = useRef<HTMLElement>(null);

  // Prevent cursor jumping by only updating innerText if it doesn't match state
  useEffect(() => {
    if (contentEditableRef.current && contentEditableRef.current.innerText !== block.content) {
      contentEditableRef.current.innerText = block.content;
    }
  }, [block.content]);

  const props = {
    ref: contentEditableRef as any,
    contentEditable: true,
    suppressContentEditableWarning: true,
    onInput: (e: React.FormEvent<HTMLElement>) => onChange(e.currentTarget.innerText),
    onKeyDown: onKeyDown,
    className: `block-${block.type === 'p' ? 'paragraph' : 'heading-' + block.type.replace('h', '')}`
  };

  if (block.type === 'callout') {
    return (
      <div className="block-callout">
        <span className="callout-emoji">💡</span>
        <div 
          className="callout-content" 
          {...props} 
          className="callout-content" 
        />
      </div>
    );
  }

  // Dynamically render the correct HTML tag based on block.type
  const Tag = block.type as keyof JSX.IntrinsicElements;
  return <Tag {...props} />;
}
