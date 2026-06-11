import React, { useState } from 'react';

// Define the shape of a Hybrid Strategy
interface StrategyRule {
  id: string;
  asset: string;
  quantTrigger: string;
  aiContextPrompt: string;
  status: 'active' | 'paused';
}

const INITIAL_STRATEGIES: StrategyRule[] = [
  {
    id: 'strat_1',
    asset: 'XLV (Health Care Select Sector)',
    quantTrigger: 'Z-Score < -2.0 (Mean Reversion)',
    aiContextPrompt: 'Analyze recent news for this ETF. Is the drop due to macroeconomic factors, or a systemic failure in a top holding? Alert me only if it is a macro overreaction.',
    status: 'active'
  }
];

export default function FinanceStrategy() {
  const [strategies, setStrategies] = useState<StrategyRule[]>(INITIAL_STRATEGIES);

  return (
    <div className="notion-board-container" style={{ maxWidth: '900px', margin: '0 auto' }}>
      <div className="board-header-block">
        <h1 className="page-title">Algorithmic Orchestration</h1>
        <p className="block-paragraph">
          Define hybrid execution strategies. The engine will monitor standard quantitative 
          deviations and dispatch frontier AI models for qualitative sentiment verification.
        </p>
      </div>

      {/* Global Quant Analytics Snapshot */}
      <div className="quant-dashboard" style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
        <MetricCard title="VIX Volatility" value="14.2" trend="-1.2%" />
        <MetricCard title="SPY Implied Skew" value="-0.45" trend="Stable" />
        <MetricCard title="Active AI Triggers" value="1" trend="Monitoring" />
      </div>

      <div className="login-divider"></div>
      <h3 style={{ marginTop: '24px', marginBottom: '16px' }}>Active Theses</h3>

      {/* Strategy Block Builder */}
      <div className="strategy-list" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {strategies.map((strat) => (
          <div key={strat.id} className="kanban-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span className="badge badge-finance">{strat.asset}</span>
              <span className={`column-status-dot ${strat.status === 'active' ? 'completed' : 'backlog'}`}></span>
            </div>
            
            <div className="rule-block" style={{ marginBottom: '12px' }}>
              <strong style={{ fontSize: '12px', color: 'var(--text-muted)' }}>QUANTITATIVE BOUND</strong>
              <p className="card-title-text" style={{ fontSize: '16px' }}>{strat.quantTrigger}</p>
            </div>

            <div className="rule-block" style={{ background: 'var(--sidebar-bg)', padding: '12px', borderRadius: '4px' }}>
              <strong style={{ fontSize: '12px', color: 'var(--text-muted)' }}>AI QUALITATIVE FILTER</strong>
              <p className="card-body-text" style={{ fontStyle: 'italic', marginTop: '4px' }}>
                "{strat.aiContextPrompt}"
              </p>
            </div>
          </div>
        ))}

        <button className="notion-login-btn" style={{ justifyContent: 'flex-start', padding: '12px' }}>
          <span style={{ color: 'var(--text-muted)' }}>+ Add new hybrid strategy...</span>
        </button>
      </div>
    </div>
  );
}

// Minimal sub-component for institutional metrics
function MetricCard({ title, value, trend }: { title: string, value: string, trend: string }) {
  return (
    <div style={{ flex: 1, border: '1px solid var(--border-color)', borderRadius: '6px', padding: '16px' }}>
      <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '8px' }}>{title}</div>
      <div style={{ fontSize: '24px', fontWeight: 600 }}>{value}</div>
      <div style={{ fontSize: '12px', color: '#0b6b43', marginTop: '4px' }}>{trend}</div>
    </div>
  );
}
