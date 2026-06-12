// Inside src/components/education/StatsDashboard.tsx
import React from 'react';

interface StatsProps {
  algorithmic_depth: number;
  systems_architecture: number;
  tooling_fluency: number;
  domain_specialization: number;
}

export function NotionCharacterSheet({ stats }: { stats: StatsProps }) {
  const statRows = [
    { label: "⚔️ Algorithmic Depth", value: stats.algorithmic_depth, color: "#4c6ef5" },
    { label: "🛡️ Systems Architecture", value: stats.systems_architecture, color: "#e8590c" },
    { label: "🔧 Tooling & Fluency", value: stats.tooling_fluency, color: "#0b7285" },
    { label: "🔮 Domain Specialization", value: stats.domain_specialization, color: "#9c36b5" }
  ];

  return (
    <div className="notion-card" style={{ fontFamily: 'Inter, sans-serif', border: '1px solid #e9ecef', padding: '20px', borderRadius: '8px', maxWidth: '450px', backgroundColor: '#fff' }}>
      <h3 style={{ margin: '0 0 16px 0', fontSize: '16px', fontWeight: 600, color: '#343a40' }}>🎮 Developer Attribute Profile</h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {statRows.map((row) => (
          <div key={row.label}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '4px', color: '#495057' }}>
              <span>{row.label}</span>
              <span style={{ fontWeight: 600 }}>LVL {Math.floor(row.value)} <span style={{ color: '#adb5bd', fontSize: '11px' }}>({row.value.toFixed(2)})</span></span>
            </div>
            {/* Elegant Notion-style progress track */}
            <div style={{ width: '100%', height: '8px', backgroundColor: '#f1f3f5', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${row.value}%`, height: '100%', backgroundColor: row.color, transition: 'width 0.4s ease-in-out' }} />
            </div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: '16px', fontSize: '11px', color: '#868e96', fontStyle: 'italic', textAlign: 'center' }}>
        ✨ Stats scale dynamically as agents digest tracked computational coursework.
      </div>
    </div>
  );
}
