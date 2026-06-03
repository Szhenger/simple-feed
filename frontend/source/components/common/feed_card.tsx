import React from 'react';
import { FeedItem } from '../../types';
import { ExternalLink, Cpu } from 'lucide-react';

interface FeedCardProps {
  item: FeedItem;
}

export const FeedCard: React.FC<FeedCardProps> = ({ item }) => {
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow group">
      <div className="flex justify-between items-start mb-2">
        <span className="inline-flex items-center gap-1 bg-blue-50 text-blue-700 text-xs font-medium px-2 py-1 rounded">
          {item.axiomCategory}
        </span>
        <div className="flex items-center gap-1 text-xs font-mono text-gray-500 bg-gray-50 px-2 py-1 rounded" title="AI Vector Triage Score">
          <Cpu className="w-3 h-3 text-emerald-500" />
          τ = {item.triageMetadata.score.toFixed(2)}
        </div>
      </div>
      <a href={item.sourceUri} target="_blank" rel="noopener noreferrer" className="block mt-2">
        <h3 className="text-lg font-bold text-gray-900 group-hover:text-blue-600 transition-colors flex items-center gap-2">
          {item.title}
          <ExternalLink className="w-4 h-4 opacity-0 group-hover:opacity-100 transition-opacity text-gray-400" />
        </h3>
      </a>
      <p className="text-sm text-gray-600 mt-2 line-clamp-3">{item.contentSnippet}</p>
      <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center text-xs text-gray-500">
        <span>{new Date(item.publishedAt).toLocaleDateString()}</span>
        <span className="uppercase tracking-wider font-semibold text-gray-400">{item.state}</span>
      </div>
    </div>
  );
};
