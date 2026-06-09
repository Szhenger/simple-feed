import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import ArchitectureDoc from './pages/ArchitectureDoc';
import VectorMetrics from './pages/VectorMetrics';
// import KanbanBoard from './pages/KanbanBoard';

export default function App() {
  // Simple state-based routing for demonstration
  const [activeView, setActiveView] = useState<'doc' | 'metrics' | 'board'>('doc');

  return (
    <div className="notion-app-container">
      <Sidebar activeView={activeView} setActiveView={setActiveView} />
      
      <main className="notion-main">
        {/* Sticky Top Header */}
        <header className="notion-header">
          <div className="breadcrumbs">
            <span className="crumb">Workspaces</span>
            <span className="divider">/</span>
            <span className="crumb current">
              {activeView === 'doc' && 'Engineering Architecture'}
              {activeView === 'metrics' && 'Vector Metrics'}
              {activeView === 'board' && 'Triage Board'}
            </span>
          </div>
          <div className="header-actions">
            <button className="btn-action">Share</button>
            <button className="btn-action">Edited just now</button>
          </div>
        </header>

        {/* Dynamic View Rendering */}
        {activeView === 'doc' && <ArchitectureDoc />}
        {activeView === 'metrics' && <VectorMetrics />}
        {/* {activeView === 'board' && <KanbanBoard />} */}
      </main>
    </div>
  );
}
