import { describe, it, expect } from 'vitest';
import { Node, Edge } from '@xyflow/react';

// Assume we extracted the serialization logic from the React component into a pure function
import { serializeGraphToPipeline } from '../../utils/graphCompiler';

describe('Financial DAG Serializer', () => {
  it('correctly maps visual X/Y nodes into a linear logical pipeline', () => {
    // Simulate Brick dragging nodes onto the canvas
    const mockNodes: Node[] = [
      { id: 'asset_1', type: 'asset', position: { x: 0, y: 0 }, data: { ticker: 'BTC' } },
      { id: 'ai_1', type: 'ai', position: { x: 200, y: 0 }, data: { prompt: 'Check Github.' } },
      { id: 'quant_1', type: 'quant', position: { x: 100, y: 0 }, data: { indicator: 'RSI', operator: '<', value: 30 } }
    ];

    // Simulate Brick connecting: Asset -> Quant -> AI
    const mockEdges: Edge[] = [
      { id: 'e1', source: 'asset_1', target: 'quant_1' },
      { id: 'e2', source: 'quant_1', target: 'ai_1' }
    ];

    const payload = serializeGraphToPipeline(mockNodes, mockEdges);

    // Validate the frontend compiled the payload perfectly for the API
    expect(payload.ticker).toBe('BTC');
    expect(payload.quant_rule.indicator).toBe('RSI');
    expect(payload.quant_rule.value).toBe(30);
    expect(payload.ai_rule.prompt).toBe('Check Github.');
  });
});
