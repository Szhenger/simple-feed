import React from 'react';
import { Handle, Position } from '@xyflow/react';

// --- 1. THE ASSET TRIGGER NODE ---
export function AssetNode({ data }: { data: any }) {
  return (
    <div className="notion-node asset-node" style={nodeStyle('#2eaadc')}>
      <div style={headerStyle}>📈 Asset Trigger</div>
      <div style={{ padding: '10px' }}>
        <select defaultValue={data.ticker} style={inputStyle}>
          <option value="SPY">SPY (S&P 500)</option>
          <option value="XLV">XLV (Health Care)</option>
          <option value="VIX">VIX (Volatility)</option>
        </select>
      </div>
      <Handle type="source" position={Position.Right} style={handleStyle} />
    </div>
  );
}

// --- 2. THE QUANTITATIVE MATH NODE ---
export function QuantNode({ data }: { data: any }) {
  return (
    <div className="notion-node quant-node" style={nodeStyle('#e5a100')}>
      <Handle type="target" position={Position.Left} style={handleStyle} />
      <div style={headerStyle}>📐 Quant Boundary</div>
      <div style={{ padding: '10px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <select defaultValue={data.indicator} style={inputStyle}>
          <option value="Z_SCORE">Rolling Z-Score</option>
          <option value="RSI">RSI (14-Day)</option>
          <option value="MACD">MACD Crossover</option>
        </select>
        <div style={{ display: 'flex', gap: '4px', alignItems: 'center' }}>
          <select defaultValue={data.operator} style={{ ...inputStyle, width: '40px' }}>
            <option value="<">&lt;</option>
            <option value=">">&gt;</option>
          </select>
          <input type="number" defaultValue={data.value} style={inputStyle} />
        </div>
      </div>
      <Handle type="source" position={Position.Right} style={handleStyle} />
    </div>
  );
}

// --- 3. THE AI QUALITATIVE NODE ---
export function AINode({ data }: { data: any }) {
  return (
    <div className="notion-node ai-node" style={nodeStyle('#0b6b43')}>
      <Handle type="target" position={Position.Left} style={handleStyle} />
      <div style={headerStyle}>🧠 AI Context Filter</div>
      <div style={{ padding: '10px' }}>
        <textarea 
          defaultValue={data.prompt} 
          rows={3} 
          placeholder="Enter LLM systemic directive..."
          style={{ ...inputStyle, resize: 'none', height: '60px' }}
        />
      </div>
      <Handle type="source" position={Position.Right} style={handleStyle} />
    </div>
  );
}

// --- SHARED STYLES (To mimic Notion's clean borders) ---
const nodeStyle = (borderColor: string): React.CSSProperties => ({
  background: 'var(--bg-color, #ffffff)',
  border: `2px solid ${borderColor}`,
  borderRadius: '8px',
  minWidth: '220px',
  boxShadow: '0 4px 6px rgba(0,0,0,0.05)',
  fontFamily: 'Inter, sans-serif'
});

const headerStyle: React.CSSProperties = {
  padding: '8px 10px',
  background: '#f7f7f5',
  borderBottom: '1px solid #e9e9e7',
  borderTopLeftRadius: '6px',
  borderTopRightRadius: '6px',
  fontSize: '12px',
  fontWeight: 600,
  color: '#37352f'
};

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '6px',
  borderRadius: '4px',
  border: '1px solid #e9e9e7',
  fontSize: '12px',
  background: '#fafafa'
};

const handleStyle: React.CSSProperties = {
  background: '#555',
  width: '8px',
  height: '8px'
};
