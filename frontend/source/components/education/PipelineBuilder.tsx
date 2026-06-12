import React, { useState } from 'react';

interface PipelineBuilderProps {
  onDeploy: (payload: any) => void;
  isDeploying: boolean;
}

export function PipelineBuilder({ onDeploy, isDeploying }: PipelineBuilderProps) {
  const [label, setLabel] = useState('');
  const [url, setUrl] = useState('');
  const [resourceType, setResourceType] = useState('documentation');
  const [directive, setDirective] = useState('');

  const handleSumbit = (e: React.FormEvent) => {
    e.preventDefault();
    onDeploy({ label, url, resourceType, directive });
    // Reset form on success
    setLabel(''); setUrl(''); setDirective('');
  };

  return (
    <div className="notion-card" style={cardStyle}>
      <div style={headerStyle}>
        <h3 style={{ margin: 0, fontSize: '16px', color: '#37352f' }}>📡 Dispatch Tracking Agent</h3>
        <span style={{ fontSize: '12px', color: '#787774' }}>Configure a new educational data source.</span>
      </div>

      <form onSubmit={handleSumbit} style={{ padding: '20px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
        
        {/* Source Configuration */}
        <div style={{ display: 'flex', gap: '12px' }}>
          <div style={{ flex: 2 }}>
            <label style={labelStyle}>Tracker Label</label>
            <input 
              required
              value={label}
              onChange={(e) => setLabel(e.target.value)}
              placeholder="e.g., MIT 6.824 Distributed Systems" 
              style={inputStyle} 
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={labelStyle}>Resource Type</label>
            <select value={resourceType} onChange={(e) => setResourceType(e.target.value)} style={inputStyle}>
              <option value="ocw">OpenCourseWare</option>
              <option value="whitepaper">Academic Whitepaper</option>
              <option value="documentation">API / Docs</option>
              <option value="media">Tech Media / YT</option>
            </select>
          </div>
        </div>

        <div>
          <label style={labelStyle}>Target URL</label>
          <input 
            required
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://..." 
            style={inputStyle} 
          />
        </div>

        {/* The Agentic Directive with Fallback UX */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '6px' }}>
            <label style={{ ...labelStyle, marginBottom: 0 }}>Agentic Directive (Optional)</label>
            {!directive && (
              <span style={{ fontSize: '11px', color: '#0b6b43', fontWeight: 500, background: '#e6f4ea', padding: '2px 6px', borderRadius: '4px' }}>
                ✓ System Defaults Active
              </span>
            )}
          </div>
          <textarea 
            value={directive}
            onChange={(e) => setDirective(e.target.value)}
            placeholder="Specify what the AI should look for. Leave blank to use institutional SWE defaults." 
            rows={3}
            style={{ ...inputStyle, resize: 'vertical', minHeight: '60px' }} 
          />
        </div>

        <button 
          type="submit" 
          disabled={isDeploying}
          style={buttonStyle(isDeploying)}
        >
          {isDeploying ? 'Deploying Agent...' : 'Deploy Tracking Agent'}
        </button>
      </form>
    </div>
  );
}

// --- Shared Styles ---
const cardStyle: React.CSSProperties = {
  background: '#fff', border: '1px solid #e9e9e7', borderRadius: '8px', boxShadow: '0 1px 3px rgba(0,0,0,0.05)', overflow: 'hidden'
};
const headerStyle: React.CSSProperties = {
  padding: '16px 20px', borderBottom: '1px solid #e9e9e7', background: '#fcfcfc'
};
const labelStyle: React.CSSProperties = {
  display: 'block', fontSize: '12px', fontWeight: 600, color: '#37352f', marginBottom: '6px'
};
const inputStyle: React.CSSProperties = {
  width: '100%', padding: '8px 12px', borderRadius: '4px', border: '1px solid #d4d4d2', fontSize: '14px', boxSizing: 'border-box'
};
const buttonStyle = (disabled: boolean): React.CSSProperties => ({
  background: disabled ? '#e0e0e0' : '#2eaadc', color: disabled ? '#888' : '#fff', border: 'none', padding: '10px 16px', borderRadius: '4px', fontSize: '14px', fontWeight: 600, cursor: disabled ? 'not-allowed' : 'pointer', marginTop: '8px'
});
