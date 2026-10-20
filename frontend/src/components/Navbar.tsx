import React from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Cpu, 
  Workflow, 
  BarChart2, 
  FilePlus, 
  CheckCircle2,
  AlertTriangle
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  pendingReviewCount: number;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab, pendingReviewCount }) => {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setCurrentTab('landing')}>
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-700 to-rose-600 flex items-center justify-center text-white shadow-md shadow-red-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">RESOLVE<span className="text-red-700">AI</span></span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-800 border border-red-200">
                  Reforged '26
                </span>
              </div>
              <p className="text-[11px] text-slate-500 font-medium hidden sm:block">Intelligent Campus Maintenance Resolution • HackShift_404</p>
            </div>
          </div>

          {/* Navigation Links */}
          <nav className="flex items-center space-x-1 sm:space-x-2">
            <button
              onClick={() => setCurrentTab('landing')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
                currentTab === 'landing'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setCurrentTab('submit')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition-all ${
                currentTab === 'submit'
                  ? 'bg-red-700 text-white shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <FilePlus className="w-4 h-4" />
              <span>Submit Issue</span>
            </button>
            <button
              onClick={() => setCurrentTab('dashboard')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition-all relative ${
                currentTab === 'dashboard'
                  ? 'bg-slate-900 text-white'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Layers className="w-4 h-4" />
              <span>Admin Triage</span>
              {pendingReviewCount > 0 && (
                <span className="ml-1 px-1.5 py-0.5 text-[10px] font-bold rounded-full bg-amber-500 text-white">
                  {pendingReviewCount}
                </span>
              )}
            </button>
            <button
              onClick={() => setCurrentTab('workflow')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition-all ${
                currentTab === 'workflow'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <Workflow className="w-4 h-4 text-red-600" />
              <span className="hidden md:inline">n8n Workflow</span>
            </button>
            <button
              onClick={() => setCurrentTab('benchmark')}
              className={`px-3 py-1.5 rounded-lg text-sm font-medium flex items-center space-x-1.5 transition-all ${
                currentTab === 'benchmark'
                  ? 'bg-slate-100 text-slate-900 font-semibold'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
              }`}
            >
              <BarChart2 className="w-4 h-4" />
              <span className="hidden md:inline">Benchmark & USP</span>
            </button>
          </nav>
        </div>
      </div>
    </header>
  );
};
