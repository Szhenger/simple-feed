import React, { useState } from 'react';
import { ProjectManifestBlock } from '../components/planning/ProjectManifest'; // Assuming we exported the component built earlier

export default function LogisticsHub() {
  const [manifests, setManifests] = useState([
    {
      id: '1', label: 'Tokyo Autumn Trip', destination: 'HND', maxBudget: 800,
      latestBrief: {
        fare: 750, airline: 'ANA', timestamp: '2026-06-13T15:30:00Z',
        aiMarkdown: "• **Favorable Exchange**: 1 USD = 150 JPY.\n• **Weather**: Mild conditions approaching.\n• **Action**: Proceed with booking."
      }
    },
    {
      id: '2', label: 'AWS re:Invent Vegas', destination: 'LAS', maxBudget: 400
    }
  ]);

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 20px' }}>
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#37352f', margin: '0 0 8px 0' }}>Logistics & Manifests</h1>
        <p style={{ color: '#787774', margin: 0, fontSize: '15px' }}>Asynchronous polling for travel, events, and spatial execution.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '32px', alignItems: 'start' }}>
        
        {/* Left Column: Draft New Manifest */}
        <div className="notion-card" style={{ padding: '24px', border: '1px solid #e9e9e7', borderRadius: '8px', background: '#fcfcfc' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', color: '#37352f' }}>Draft New Manifest</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <label style={labelStyle}>Project Label</label>
              <input placeholder="e.g., Q3 Architecture Summit" style={inputStyle} />
            </div>
            <div style={{ display: 'flex', gap: '12px' }}>
              <div style={{ flex: 1 }}>
                <label style={labelStyle}>Origin Code</label>
                <input placeholder="JFK" style={inputStyle} />
              </div>
              <div style={{ flex: 1 }}>
                <label style={labelStyle}>Dest. Code</label>
                <input placeholder="SFO" style={inputStyle} />
              </div>
            </div>
            <div>
              <label style={labelStyle}>Max Budget Ceiling (USD)</label>
              <input type="number" placeholder="500" style={inputStyle} />
            </div>
            <div>
              <label style={labelStyle}>AI Reporting Directive</label>
              <textarea placeholder="Specify constraints, weather checks, or local conditions..." rows={4} style={{ ...inputStyle, resize: 'vertical' }} />
            </div>
            <button style={btnStylePrimary}>Deploy Manifest</button>
          </div>
        </div>

        {/* Right Column: Active Manifest Feed */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          {manifests.map(manifest => (
            <ProjectManifestBlock key={manifest.id} data={manifest} />
          ))}
        </div>

      </div>
    </div>
  );
}

// --- Shared UI Styles ---
const labelStyle: React.CSSProperties = { display: 'block', fontSize: '12px', fontWeight: 600, color: '#787774', marginBottom: '6px' };
const inputStyle: React.CSSProperties = { width: '100%', padding: '8px 12px', borderRadius: '4px', border: '1px solid #d4d4d2', fontSize: '14px', boxSizing: 'border-box' };
const btnStylePrimary: React.CSSProperties = { background: '#2eaadc', color: '#fff', border: 'none', padding: '8px 16px', borderRadius: '4px', fontSize: '14px', fontWeight: 600, cursor: 'pointer' };
const btnStyleSecondary: React.CSSProperties = { background: '#ebebeb', color: '#37352f', border: 'none', padding: '8px 16px', borderRadius: '4px', fontSize: '14px', fontWeight: 600, cursor: 'pointer' };
