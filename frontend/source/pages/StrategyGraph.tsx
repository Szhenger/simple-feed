import React, { useCallback, useState } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
  Connection,
  Edge
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { AssetNode, QuantNode, AINode } from '../components/finance/CustomNodes';

// Register custom nodes with the ReactFlow engine
const nodeTypes = {
  asset: AssetNode,
  quant: QuantNode,
  ai: AINode,
};

// Define Brick's initial starting strategy as a visual layout
const initialNodes = [
  {
    id: 'asset_1',
    type: 'asset',
    position: { x: 50, y: 150 },
    data: { ticker: 'XLV' },
  },
  {
    id: 'quant_1',
    type: 'quant',
    position: { x: 350, y: 125 },
    data: { indicator: 'Z_SCORE', operator: '<', value: -2.0 },
  },
  {
    id: 'ai_1',
    type: 'ai',
    position: { x: 650, y: 110 },
    data: { prompt: 'Analyze recent news for this ETF. Alert me only if the drop is due to a macro overreaction.' },
  },
];

const initialEdges = [
  { id: 'e1-2', source: 'asset_1', target: 'quant_1', animated: true, style: { stroke: '#e5a100', strokeWidth: 2 } },
  { id: 'e2-3', source: 'quant_1', target: 'ai_1', animated: true, style: { stroke: '#0b6b43', strokeWidth: 2 } },
];

export default function StrategyGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isDeploying, setIsDeploying] = useState(false);

  // Handle users drawing lines between logic blocks
  const onConnect = useCallback(
    (params: Connection | Edge) => setEdges((eds) => addEdge({ ...params, animated: true }, eds)),
    [setEdges],
  );

  // Compile visual state into a JSON payload for the Celery Backend
  const handleDeploy = () => {
    setIsDeploying(true);
    
    // In production, we traverse the graph using the edges array to build a JSON execution tree.
    // We trace source -> target starting from the 'asset' node.
    const strategyPayload = {
        graph_id: "strat_" + Date.now(),
        nodes: nodes,
        connections: edges
    };
    
    console.log("🚀 Deploying compiled strategy payload to Celery Workers:", strategyPayload);
    
    setTimeout(() => {
        setIsDeploying(false);
        alert("Strategy successfully deployed to the quantitative engine.");
    }, 1200);
  };

  return (
    <div style={{ width: '100%', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Application Header */}
      <header className="notion-header" style={{ padding: '16px 24px', display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid var(--border-color)' }}>
        <div style={{ display: 'flex', flexDirection: 'column' }}>
          <h1 style={{ fontSize: '18px', margin: 0 }}>Mean Reversion Thesis</h1>
          <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>Status: Draft</span>
        </div>
        <button 
          onClick={handleDeploy}
          disabled={isDeploying}
          style={{
            background: isDeploying ? '#e0e0e0' : '#2eaadc',
            color: isDeploying ? '#888' : '#fff',
            border: 'none',
            padding: '8px 16px',
            borderRadius: '4px',
            cursor: isDeploying ? 'not-allowed' : 'pointer',
            fontWeight: 500
          }}
        >
          {isDeploying ? 'Compiling...' : 'Deploy to Engine'}
        </button>
      </header>

      {/* The Infinite Canvas */}
      <div style={{ flexGrow: 1, background: '#fcfcfc' }}>
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          nodeTypes={nodeTypes}
          fitView
        >
          <Controls />
          <MiniMap 
            nodeColor={(node) => {
              switch (node.type) {
                case 'asset': return '#2eaadc';
                case 'quant': return '#e5a100';
                case 'ai': return '#0b6b43';
                default: return '#eee';
              }
            }} 
          />
          <Background gap={24} size={1} color="#e9e9e7" />
        </ReactFlow>
      </div>
    </div>
  );
}
