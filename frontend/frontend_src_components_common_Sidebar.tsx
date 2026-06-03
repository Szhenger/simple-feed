import React from 'react';
import { BookOpen, Briefcase, BadgeDollarSign, CalendarDays, LayoutGrid } from 'lucide-react';
import { useUIStore } from '../../store/uiStore';
import { AxiomCategory } from '../../types';
import clsx from 'clsx';

const AXIOMS: { id: AxiomCategory | 'ALL'; label: string; icon: React.FC<any> }[] = [
  { id: 'ALL', label: 'Global View', icon: LayoutGrid },
  { id: 'EDUCATION', label: 'Education', icon: BookOpen },
  { id: 'CAREER', label: 'Career Advancement', icon: Briefcase },
  { id: 'FINANCE', label: 'Finances', icon: BadgeDollarSign },
  { id: 'LIFE_PLANNING', label: 'Life Planning', icon: CalendarDays },
];

export const Sidebar: React.FC = () => {
  const { activeAxiom, setActiveAxiom } = useUIStore();

  return (
    <aside className="w-64 bg-gray-900 text-gray-300 flex flex-col h-full border-r border-gray-800">
      <div className="p-6">
        <h2 className="text-xl font-bold tracking-tight text-white flex items-center gap-2">
          <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs">SZ</span>
          SimpleFeed++
        </h2>
      </div>
      <nav className="flex-1 px-4 space-y-1">
        {AXIOMS.map((axiom) => {
          const Icon = axiom.icon;
          const isActive = activeAxiom === axiom.id;
          return (
            <button
              key={axiom.id}
              onClick={() => setActiveAxiom(axiom.id)}
              className={clsx(
                'w-full flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors',
                isActive
                  ? 'bg-gray-800 text-white'
                  : 'hover:bg-gray-800 hover:text-white'
              )}
            >
              <Icon className="w-4 h-4" />
              {axiom.label}
            </button>
          );
        })}
      </nav>
      <div className="p-4 border-t border-gray-800 text-xs text-gray-500 font-mono">
        System Core: Online<br />
        Vector Triage: Active
      </div>
    </aside>
  );
};
