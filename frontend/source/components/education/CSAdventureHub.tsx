import React, { useState, useEffect } from 'react';
import { NotionCharacterSheet } from '../components/education/StatsDashboard';
import { PipelineBuilder } from '../components/education/PipelineBuilder';
import { ActivePipelines } from '../components/education/ActivePipelines';

export default function CSAdventureHub() {
  const [isDeploying, setIsDeploying] = useState(false);
  const [pipelines, setPipelines] = useState([]);
  
  // Mock data for Shubert's current transition stats
  const [stats, setStats] = useState({
    algorithmic_depth: 42.5,
    systems_architecture: 15.2,
    tooling_fluency: 28.0,
    domain_specialization: 5.0
  });

  const handleDeployPipeline = async (payload: any) => {
    setIsDeploying(true);
    console.log("🚀 Sending to backend:", payload);
    
    // Simulate API call to backend/education/views.py
    setTimeout(() => {
      const newPipeline = {
        id: `pipe_${Date.now()}`,
        label: payload.label,
        resource_type: payload.resourceType,
        is_active: true
      };
      setPipelines([newPipeline, ...pipelines]);
      setIsDeploying(false);
    }, 800);
  };

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '40px 20px', fontFamily: 'Inter, sans-serif' }}>
      
      <header style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#37352f', margin: '0 0 8px 0' }}>Computer Science Curriculum</h1>
        <p style={{ color: '#787774', margin: 0, fontSize: '15px' }}>Track academic whitepapers, OCW, and framework documentation to build production readiness.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px', alignItems: 'start' }}>
        
        {/* Left Column: The RPG Motivation */}
        <div style={{ position: 'sticky', top: '40px' }}>
          <NotionCharacterSheet stats={stats} />
        </div>

        {/* Right Column: Action & Management */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
          <PipelineBuilder onDeploy={handleDeployPipeline} isDeploying={isDeploying} />
          <ActivePipelines pipelines={pipelines} />
        </div>

      </div>
    </div>
  );
}
