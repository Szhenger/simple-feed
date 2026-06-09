import React from 'react';

interface SidebarProps {
  activeView: 'doc' | 'metrics' | 'board';
  setActiveView: (view: 'doc' | 'metrics' | 'board') => void;
}

export default function Sidebar({ activeView, setActiveView }: SidebarProps) {
  return (
    <aside className="notion-sidebar">
      <div className="sidebar-header">
        <div className="workspace-selector">
          <span className="avatar">🚀</span>
          <span className="workspace-name">SimpleFeed++</span>
        </div>
      </div>
      
      <nav className="sidebar-menu">
        <div className="menu-section-title">Favorites</div>
        
        <button 
          className={`menu-item ${activeView === 'doc' ? 'active' : ''}`}
          onClick={() => setActiveView('doc')}
        >
          📄 Engineering Architecture
        </button>
        
        <button 
          className={`menu-item ${activeView === 'metrics' ? 'active' : ''}`}
          onClick={() => setActiveView('metrics')}
        >
          📊 Vector Metrics
        </button>

        <button 
          className={`menu-item ${activeView === 'board' ? 'active' : ''}`}
          onClick={() => setActiveView('board')}
        >
          📋 Triage Board
        </button>
        
        <div className="menu-section-title">Private</div>
        <button className="menu-item">⚙️ Settings & Members</button>
        <button className="menu-item">🗑️ Trash</button>
      </nav>
    </aside>
  );
}
