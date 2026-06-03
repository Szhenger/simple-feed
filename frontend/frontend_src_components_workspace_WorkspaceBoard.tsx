import React from 'react';
import { useUIStore } from '../../store/uiStore';
import { FeedCard } from '../common/FeedCard';
import { FeedItem } from '../../types';

// Deterministic mock data to visualize the strict type contracts before the backend connects
const MOCK_ITEMS: FeedItem[] = [
  {
    id: '1',
    workspaceId: 'ws-123',
    sourceUri: 'https://research.google/pubs/',
    title: 'Optimizing AVX-512 Instruction Pipelines in C++20',
    contentSnippet: 'A deep dive into reducing cache latency and loop unrolling for high-throughput string tokenization algorithms.',
    publishedAt: new Date().toISOString(),
    axiomCategory: 'EDUCATION',
    state: 'DISCOVERED',
    triageMetadata: { score: 0.94, centroidDistance: 0.05 },
  },
  {
    id: '2',
    workspaceId: 'ws-123',
    sourceUri: 'https://news.ycombinator.com',
    title: 'PostgreSQL Range Partitioning strategies for Time-Series',
    contentSnippet: 'Scaling a database beyond 1TB using declarative partitioning and pgvector indexes.',
    publishedAt: new Date(Date.now() - 86400000).toISOString(),
    axiomCategory: 'CAREER',
    state: 'VECTOR_TRIAGED',
    triageMetadata: { score: 0.88, centroidDistance: 0.12 },
  }
];

export const WorkspaceBoard: React.FC = () => {
  const activeAxiom = useUIStore((state) => state.activeAxiom);
  
  const filteredItems = activeAxiom === 'ALL' 
    ? MOCK_ITEMS 
    : MOCK_ITEMS.filter(i => i.axiomCategory === activeAxiom);

  return (
    <div className="flex-1 overflow-y-auto bg-gray-50 p-8">
      <header className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 tracking-tight">
            {activeAxiom === 'ALL' ? 'Global Command Center' : `${activeAxiom} Workspace`}
          </h1>
          <p className="text-gray-500 text-sm mt-1">Filtering vector-triaged feeds (τ ≥ 0.72)</p>
        </div>
      </header>

      {filteredItems.length === 0 ? (
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <p className="text-gray-500">No signals detected for this axiom.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 auto-rows-max">
          {filteredItems.map(item => (
            <FeedCard key={item.id} item={item} />
          ))}
        </div>
      )}
    </div>
  );
};
