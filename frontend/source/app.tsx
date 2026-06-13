import React, { useState } from 'react';
import CSAdventureHub from './pages/CSAdventureHub';
import QuantitativeHub from './pages/QuantitativeHub';
import LogisticsHub from './pages/LogisticsHub';

export default function SimpleFeedApp() {
  const [activeTab, setActiveTab] = useState('education');

  return (
    <div style={{ display: 'flex', height: '100vh', width: '100vw', overflow: 'hidden', fontFamily: 'Inter, sans-serif' }}>
      
      {/* Sidebar Navigation */}
      <nav style={{ 
        width: '240px', background: '#f7f7f5', borderRight: '1px solid #e9e9e7', 
        padding: '24px 12px', display: 'flex', flexDirection: 'column', gap: '4px' 
      }}>
        <div style={{ padding: '0 12px', marginBottom: '24px' }}>
          <h2 style={{ margin: 0, fontSize: '14px', fontWeight: 600, color: '#37352f' }}>SimpleFeed++</h2>
          <span style={{ fontSize: '11px', color: '#787774' }}>Workspace Kernel</span>
        </div>

        <NavItem 
          label="📖 Computer Science" isActive={activeTab === 'education'} 
          onClick={() => setActiveTab('education')} 
        />
        <NavItem 
          label="📈 Quantitative Finance" isActive={activeTab === 'finance'} 
          onClick={() => setActiveTab('finance')} 
        />
        <NavItem 
          label="🛫 Logistics & Planning" isActive={activeTab === 'planning'} 
          onClick={() => setActiveTab('planning')} 
        />
      </nav>

      {/* Main Content Area */}
      <main style={{ flex: 1, overflowY: 'auto', background: '#ffffff' }}>
        {activeTab === 'education' && <CSAdventureHub />}
        {activeTab === 'finance' && <QuantitativeHub />}
        {activeTab === 'planning' && <LogisticsHub />}
      </main>
    </div>
  );
}

// --- Sidebar Helper ---
function NavItem({ label, isActive, onClick }: { label: string, isActive: boolean, onClick: () => void }) {
  return (
    <button 
      onClick={onClick}
      style={{
        display: 'flex', alignItems: 'center', width: '100%', padding: '8px 12px',
        background: isActive ? '#ebebeb' : 'transparent', border: 'none',
        borderRadius: '6px', cursor: 'pointer', textAlign: 'left',
        fontSize: '14px', color: '#37352f', fontWeight: isActive ? 500 : 400,
        transition: 'background 0.1s ease'
      }}
    >
      {label}
    </button>
  );
}
