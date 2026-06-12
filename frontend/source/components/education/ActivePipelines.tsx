import React from 'react';

interface Pipeline {
  id: string;
  label: string;
  resource_type: string;
  is_active: boolean;
}

export function ActivePipelines({ pipelines }: { pipelines: Pipeline[] }) {
  return (
    <div className="notion-card" style={cardStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '16px', color: '#37352f' }}>⚙️ Active Operations</h3>
      </div>
      <div style={{ padding: '12px 20px' }}>
        {pipelines.length === 0 ? (
          <div style={{ padding: '20px', textAlign: 'center', color: '#787774', fontSize: '13px' }}>
            No agents deployed. Configure a tracker above.
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            {pipelines.map(p => (
              <div key={p.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', border: '1px solid #e9e9e7', borderRadius: '6px', background: '#fafafa' }}>
                <div style={{ display: 'flex', flexDirection: 'column' }}>
                  <span style={{ fontSize: '14px', fontWeight: 600, color: '#37352f' }}>{p.label}</span>
                  <span style={{ fontSize: '11px', color: '#787774', textTransform: 'uppercase' }}>{p.resource_type}</span>
                </div>
                <div>
                  <span style={{ 
                    display: 'inline-block', width: '8px', height: '8px', borderRadius: '50%', 
                    background: p.is_active ? '#0b6b43' : '#e03131', marginRight: '6px' 
                  }} />
                  <span style={{ fontSize: '12px', color: '#37352f' }}>{p.is_active ? 'Polling' : 'Paused'}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
