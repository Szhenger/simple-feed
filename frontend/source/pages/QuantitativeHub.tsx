import React, { useState } from 'react';

export default function QuantitativeHub() {
  // Mock state representing the HybridStrategies from the Django backend
  const [strategies, setStrategies] = useState([
    { id: '1', ticker: 'NVDA', zScoreThreshold: 2.5, currentZ: 2.81, aiStatus: 'ANALYZING', directive: 'Flag hardware supply chain issues.' },
    { id: '2', ticker: 'BND', zScoreThreshold: -1.5, currentZ: -0.4, aiStatus: 'STANDBY', directive: 'Monitor fed interest rate notes.' }
  ]);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 20px' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#37352f', margin: '0 0 8px 0' }}>Quantitative Operations</h1>
        <p style={{ color: '#787774', margin: 0, fontSize: '15px' }}>Manage C++ statistical bounds and AI qualitative fallbacks.</p>
      </header>

      {/* Deployment Action Bar */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        <button style={btnStylePrimary}>+ New Hybrid Strategy</button>
        <button style={btnStyleSecondary}>Force Kernel Sync</button>
      </div>

      {/* Notion-style Database Table */}
      <div style={{ border: '1px solid #e9e9e7', borderRadius: '8px', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '14px' }}>
          <thead style={{ background: '#fcfcfc', color: '#787774', borderBottom: '1px solid #e9e9e7' }}>
            <tr>
              <th style={thStyle}>Ticker</th>
              <th style={thStyle}>C++ Z-Score (Cur / Trg)</th>
              <th style={thStyle}>AI Engine Status</th>
              <th style={thStyle}>Agentic Directive</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map(strat => {
              const isTriggered = Math.abs(strat.currentZ) >= Math.abs(strat.zScoreThreshold);
              return (
                <tr key={strat.id} style={{ borderBottom: '1px solid #e9e9e7' }}>
                  <td style={{ ...tdStyle, fontWeight: 600, color: '#37352f' }}>{strat.ticker}</td>
                  <td style={tdStyle}>
                    <span style={{ 
                      color: isTriggered ? '#e03131' : '#37352f', fontWeight: isTriggered ? 600 : 400 
                    }}>
                      {strat.currentZ.toFixed(2)}
                    </span>
                    <span style={{ color: '#adb5bd' }}> / {strat.zScoreThreshold.toFixed(1)}</span>
                  </td>
                  <td style={tdStyle}>
                    <span style={{
                      padding: '2px 6px', borderRadius: '4px', fontSize: '11px', fontWeight: 600,
                      background: strat.aiStatus === 'ANALYZING' ? '#fff3cd' : '#f8f9fa',
                      color: strat.aiStatus === 'ANALYZING' ? '#856404' : '#6c757d'
                    }}>
                      {strat.aiStatus}
                    </span>
                  </td>
                  <td style={{ ...tdStyle, color: '#787774', maxWidth: '300px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                    {strat.directive}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

const thStyle: React.CSSProperties = { padding: '12px 16px', fontWeight: 500 };
const tdStyle: React.CSSProperties = { padding: '12px 16px', color: '#37352f' };
