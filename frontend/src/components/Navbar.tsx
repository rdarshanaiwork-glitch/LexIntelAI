import React from 'react';
import { Scale, Cpu } from 'lucide-react';

interface NavbarProps {
  currentView: string;
  onNavigate: (view: string) => void;
  user?: any;
}

export const Navbar: React.FC<NavbarProps> = ({ currentView, onNavigate }) => {
  return (
    <header className="sticky top-0 z-50 bg-[#060913]/90 backdrop-blur-md border-b border-slate-800/80 px-6 py-3.5">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Brand */}
        <div 
          onClick={() => onNavigate('landing')} 
          className="flex items-center gap-3 cursor-pointer group"
        >
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-700 via-indigo-600 to-sky-400 p-0.5 shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform duration-200">
            <div className="w-full h-full bg-[#070b14] rounded-[10px] flex items-center justify-center">
              <Scale className="w-5 h-5 text-blue-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-lg tracking-tight text-white font-['Cinzel',serif]">
                LEXINTEL
              </span>
              <span className="text-[10px] uppercase tracking-widest font-black px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">
                AI 2.0
              </span>
            </div>
            <p className="text-[11px] text-slate-400 tracking-wider">
              Autonomous Multi-Agent Legal Intelligence
            </p>
          </div>
        </div>

        {/* Middle Badges */}
        <div className="hidden md:flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs text-slate-300">
            <Cpu className="w-3.5 h-3.5 text-blue-400" />
            <span>Orchestration: <strong className="text-white">LangGraph v0.2</strong></span>
          </div>
          <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-950/50 border border-emerald-500/30 text-xs text-emerald-400">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
            <span>4 Department Super-Agents Online</span>
          </div>
        </div>

        {/* User Profile / Navigation */}
        <div className="flex items-center gap-3">
          <button
            onClick={() => onNavigate('dashboard')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-colors ${
              currentView === 'dashboard' ? 'bg-blue-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
            }`}
          >
            Dashboard
          </button>
          <button
            onClick={() => onNavigate('new-case')}
            className="px-3.5 py-1.5 rounded-lg bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold shadow-md shadow-blue-500/25 transition-all"
          >
            + New Matter
          </button>
          <div className="h-4 w-px bg-slate-800 hidden sm:block" />
          <div className="flex items-center gap-2 pl-2">
            <div className="w-8 h-8 rounded-full bg-blue-950 border border-blue-700/50 flex items-center justify-center text-blue-300 text-xs font-bold">
              LC
            </div>
            <div className="hidden sm:block text-left">
              <div className="text-xs font-medium text-white leading-tight">Lead Counsel</div>
              <div className="text-[10px] text-slate-400">Senior Partner</div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};