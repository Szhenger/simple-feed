import React, { useState } from 'react';

interface ManifestProps {
  label: string;
  destination: string;
  maxBudget: number;
  latestBrief?: {
    fare: number;
    airline: string;
    aiMarkdown: string;
    timestamp: string;
  };
}

export function ProjectManifestBlock({ data }: { data: ManifestProps }) {
  return (
    <div className="notion-card" style={{ border: '1px solid #e9e9e7', borderRadius: '8px', padding: '24px', background: '#fff', fontFamily: 'Inter, sans-serif' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', borderBottom: '1px solid #eee', paddingBottom: '16px', marginBottom: '16px' }}>
        <div>
          <h2 style={{ margin: '0 0 4px 0', fontSize: '20px', color: '#37352f' }}>🛫 {data.label}</h2>
          <span style={{ fontSize: '13px', color: '#787774' }}>Target: {data.destination} | Threshold: ${data.maxBudget}</span>
        </div>
        <div style={{ padding: '6px 12px', background: '#e6f4ea', color: '#0b6b43', borderRadius: '4px', fontSize: '12px', fontWeight: 600, height: 'fit-content' }}>
          Agent Active
        </div>
      </div>

      {/* AI Briefing Render */}
      {data.latestBrief ? (
        <div style={{ background: '#f9f9f8', padding: '16px', borderRadius: '6px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
            <span style={{ fontSize: '24px', fontWeight: 700, color: '#e03131' }}>${data.latestBrief.fare}</span>
            <span style={{ fontSize: '14px', color: '#495057', fontWeight: 500 }}>Found via {data.latestBrief.airline}</span>
          </div>
          
          <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: '#787774', marginBottom: '8px' }}>🤖 Executive Briefing</h4>
          <div style={{ fontSize: '14px', color: '#37352f', lineHeight: '1.6' }} 
               dangerouslySetInnerHTML={{ __html: renderMarkdown(data.latestBrief.aiMarkdown) }} />
               
          <div style={{ marginTop: '16px', fontSize: '11px', color: '#adb5bd', textAlign: 'right' }}>
            Last polled: {new Date(data.latestBrief.timestamp).toLocaleString()}
          </div>
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: '32px', color: '#adb5bd', fontSize: '14px' }}>
          Agent is polling daily. Waiting for flights to drop below ${data.maxBudget}.
        </div>
      )}
    </div>
  );
}

// Mock markdown parser for the example
const renderMarkdown = (text: string) => text.replace(/\n/g, '<br/>');
