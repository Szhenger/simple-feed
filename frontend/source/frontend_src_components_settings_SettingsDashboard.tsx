import React from 'react';
import { Database, Cpu, Activity, ShieldCheck, HardDrive } from 'lucide-react';

export const SettingsDashboard: React.FC = () => {
  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-8 h-full">
      <header className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900 tracking-tight flex items-center gap-3">
          <Database className="w-6 h-6 text-blue-600" />
          Infrastructure Configuration
        </h1>
        <p className="text-gray-500 text-sm mt-1">Manage vector thresholds, parsing kernels, and data partitioning.</p>
      </header>

      <div className="max-w-4xl grid gap-6">
        {/* Vector Triage Settings */}
        <section className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
          <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-100">
            <Cpu className="w-5 h-5 text-emerald-600" />
            <h2 className="text-lg font-semibold text-gray-900">AI Vector Triage Threshold</h2>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current Tolerance (τ)</label>
              <div className="flex items-center gap-4">
                <input 
                  type="range" 
                  min="0.5" 
                  max="0.99" 
                  step="0.01" 
                  defaultValue="0.72"
                  className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                />
                <span className="font-mono text-sm bg-gray-100 px-3 py-1 rounded text-gray-700 font-bold border border-gray-200">
                  0.72
                </span>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Higher values restrict feed ingestion strictly to the four axioms. Values below 0.6 may introduce signal noise.
              </p>
            </div>
            
            <button className="bg-blue-50 text-blue-700 border border-blue-200 px-4 py-2 rounded text-sm font-medium hover:bg-blue-100 transition-colors">
              Re-calculate Vector Embeddings
            </button>
          </div>
        </section>

        {/* Distributed Worker Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <section className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
             <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-100">
              <Activity className="w-5 h-5 text-purple-600" />
              <h2 className="text-lg font-semibold text-gray-900">Ingestion Fleet Status</h2>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Active Workers (Celery)</span>
                <span className="font-mono font-bold text-gray-900">8 Nodes</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">C++ Native Kernel</span>
                <span className="flex items-center gap-1 text-emerald-600 text-xs font-bold uppercase tracking-wider">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span> 
                  Loaded (AVX-512)
                </span>
              </div>
               <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Polling Strategy</span>
                <span className="font-mono text-gray-900 text-xs bg-gray-100 px-2 py-0.5 rounded">Exponential Backoff</span>
              </div>
            </div>
          </section>

          {/* Shard Status */}
          <section className="bg-white border border-gray-200 rounded-lg p-6 shadow-sm">
             <div className="flex items-center gap-2 mb-4 pb-4 border-b border-gray-100">
              <HardDrive className="w-5 h-5 text-orange-600" />
              <h2 className="text-lg font-semibold text-gray-900">Storage Shard Map</h2>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600 flex items-center gap-2">
                  <ShieldCheck className="w-4 h-4 text-gray-400" />
                  RLS Gateway
                </span>
                <span className="text-emerald-600 text-xs font-bold uppercase tracking-wider bg-emerald-50 px-2 py-0.5 rounded border border-emerald-100">Enforced</span>
              </div>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Active Shard</span>
                <span className="font-mono text-gray-900 text-xs bg-gray-100 px-2 py-0.5 rounded border border-gray-200">shard_0</span>
              </div>
               <div className="flex justify-between items-center text-sm">
                <span className="text-gray-600">Current Partition</span>
                <span className="font-mono text-gray-900 text-xs">feed_item_2026_06</span>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};
