import React from 'react';
import { 
  LayoutDashboard, FolderPlus, FolderKanban, Database, 
  Layers, ShieldCheck, BarChart3 
} from 'lucide-react';

interface SidebarProps {
  currentView: string;
  onNavigate: (view: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentView, onNavigate }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'new-case', label: 'New Legal Matter', icon: FolderPlus },
    { id: 'cases', label: 'Case Repository', icon: FolderKanban },
    { id: 'evaluation', label: 'Evaluation & Benchmarks', icon: BarChart3 },
    { id: 'knowledge', label: 'Legal Knowledge Base', icon: Database },
    { id: 'architecture', label: 'Agent Topology', icon: Layers },
  ];

  return (
    <aside className="w-64 shrink-0 hidden lg:flex flex-col justify-between border-r border-slate-800/80 bg-[#070b14] min-h-[calc(100vh-61px)] p-4">
      <div className="space-y-6">
        <div>
          <span className="text-[11px] font-bold uppercase tracking-wider text-slate-400 px-3 block mb-2">
            Core Workspace
          </span>
          <nav className="space-y-1">
            {menuItems.map(item => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onNavigate(item.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-lg shadow-blue-600/20'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/80'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Agentic Framework Notice */}
        <div className="p-3.5 rounded-xl bg-gradient-to-b from-blue-950/40 to-slate-900/60 border border-blue-500/20 text-xs">
          <div className="flex items-center gap-2 text-blue-400 font-bold mb-1">
            <ShieldCheck className="w-4 h-4" />
            <span>Agentic AI System</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-relaxed">
            LexIntel AI deploys 4 autonomous Department Super-Agents covering 10 legal reasoning roles with task decomposition and judicial simulation.
          </p>
        </div>
      </div>

      <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400">
        <div className="flex items-center justify-between px-3 py-2">
          <span>LexIntel Platform</span>
          <span className="font-mono text-[10px] text-slate-400">v1.0.0-academic</span>
        </div>
      </div>
    </aside>
  );
};