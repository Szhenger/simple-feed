import React, { useEffect } from 'react';
import { X, ExternalLink, Archive, PlaySquare, ArrowRight, Cpu } from 'lucide-react';
import { useWorkspaceStore } from '../../store/workspaceStore';
import clsx from 'clsx';

export const ArticleReader: React.FC = () => {
  const { activeArticle, closeArticle } = useWorkspaceStore();

  // Close on Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') closeArticle();
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [closeArticle]);

  if (!activeArticle) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-gray-900/20 backdrop-blur-sm z-40 transition-opacity"
        onClick={closeArticle}
      />
      
      {/* Slide-over Panel */}
      <div className="fixed inset-y-0 right-0 w-full max-w-2xl bg-white shadow-2xl z-50 flex flex-col border-l border-gray-200 transform transition-transform duration-300 ease-in-out overflow-hidden">
        
        {/* Header */}
        <header className="px-6 py-4 border-b border-gray-100 flex items-center justify-between bg-gray-50/80 backdrop-blur">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center gap-1 bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-1 rounded-md">
              {activeArticle.axiomCategory}
            </span>
            <div className="flex items-center gap-1 text-xs font-mono text-emerald-700 bg-emerald-50 border border-emerald-100 px-2 py-1 rounded-md">
              <Cpu className="w-3 h-3" />
              Vector Triage: τ = {activeArticle.triageMetadata.score.toFixed(2)}
            </div>
          </div>
          <button 
            onClick={closeArticle}
            className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </header>

        {/* Content Scroll Area */}
        <div className="flex-1 overflow-y-auto p-8">
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight leading-tight mb-4">
            {activeArticle.title}
          </h1>
          
          <div className="flex items-center text-sm text-gray-500 font-mono mb-8 space-x-4">
            <time>{new Date(activeArticle.publishedAt).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</time>
            <span>•</span>
            <span className="uppercase tracking-wider font-semibold text-gray-400">STATE: {activeArticle.state}</span>
          </div>

          <div className="prose prose-blue max-w-none text-gray-700 leading-relaxed">
            {/* In a real scenario, this renders the sanitized HTML from the native C++ parser */}
            <p className="text-lg text-gray-600 font-medium mb-6">
              {activeArticle.contentSnippet}
            </p>
            <div className="p-4 bg-gray-50 border border-gray-100 rounded-lg text-sm text-gray-500 italic flex items-center gap-2">
              <ExternalLink className="w-4 h-4" />
              Full HTML content is isolated. Click the source link below to view the original payload securely.
            </div>
          </div>
        </div>

        {/* State Machine Action Bar */}
        <footer className="px-6 py-4 border-t border-gray-100 bg-gray-50 flex items-center justify-between">
          <a 
            href={activeArticle.sourceUri} 
            target="_blank" 
            rel="noopener noreferrer"
            className="text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors flex items-center gap-2"
          >
            View Original Source
            <ExternalLink className="w-4 h-4" />
          </a>
          
          <div className="flex items-center gap-3">
            <button className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 shadow-sm flex items-center gap-2 transition-all">
              <Archive className="w-4 h-4 text-gray-400" />
              Archive
            </button>
            <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 shadow-sm flex items-center gap-2 transition-all">
              <PlaySquare className="w-4 h-4" />
              Mark Actionable
              <ArrowRight className="w-4 h-4 opacity-50" />
            </button>
          </div>
        </footer>
      </div>
    </>
  );
};
