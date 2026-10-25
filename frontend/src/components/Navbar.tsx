import React from 'react';
import { 
  ShieldCheck, 
  Layers, 
  Workflow, 
  BarChart2, 
  FilePlus, 
  FileText,
  Search,
  ArrowLeft,
  LogOut,
  RotateCcw,
  Lock,
  User,
  Sparkles
} from 'lucide-react';
import { UserSession } from '../types';

interface NavbarProps {
  currentPortal: 'selection' | 'user' | 'admin' | 'testing';
  currentTab: string;
  onSelectPortal: (portal: 'selection' | 'user' | 'admin' | 'testing') => void;
  onSelectTab: (tab: string) => void;
  pendingReviewCount: number;
  session: UserSession | null;
  onLogout: () => void;
  onResetDemo?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentPortal,
  currentTab,
  onSelectPortal,
  onSelectTab,
  pendingReviewCount,
  session,
  onLogout,
  onResetDemo,
}) => {
  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur border-b border-slate-200 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16 gap-3">
          {/* Logo & Brand */}
          <div 
            className="flex items-center space-x-3 cursor-pointer shrink-0" 
            onClick={() => onSelectPortal('selection')}
            title="Return to Portal Selection"
          >
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-red-700 to-rose-600 flex items-center justify-center text-white shadow-md shadow-red-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-slate-900">
                  RESOLVE<span className="text-red-700">AI</span>
                </span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-800 border border-red-200">
                  Reforged '26
                </span>
              </div>
              <p className="text-[10px] text-slate-500 font-medium hidden sm:block">
                {currentPortal === 'user' && 'User Portal • Public Access'}
                {currentPortal === 'admin' && 'Admin Portal • Maintenance Triage'}
                {currentPortal === 'testing' && 'Testing Portal • Workflows & Evaluation'}
                {currentPortal === 'selection' && 'Intelligent Campus Maintenance • HackShift_404'}
              </p>
            </div>
          </div>

          {/* Portal-Specific Navigation Tabs */}
          <div className="flex items-center space-x-1 sm:space-x-2 overflow-x-auto">
            {/* PORTAL SELECTION VIEW */}
            {currentPortal === 'selection' && (
              <>
                <button
                  onClick={() => onSelectPortal('user')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors flex items-center space-x-1"
                >
                  <FilePlus className="w-3.5 h-3.5 text-red-600" />
                  <span>User Portal</span>
                </button>
                <button
                  onClick={() => onSelectPortal('admin')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors flex items-center space-x-1"
                >
                  <Layers className="w-3.5 h-3.5 text-slate-700" />
                  <span>Admin Portal</span>
                </button>
                <button
                  onClick={() => onSelectPortal('testing')}
                  className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors flex items-center space-x-1"
                >
                  <Workflow className="w-3.5 h-3.5 text-red-600" />
                  <span>Testing Portal</span>
                </button>
              </>
            )}

            {/* USER PORTAL TABS */}
            {currentPortal === 'user' && (
              <>
                <button
                  onClick={() => onSelectTab('overview')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                    currentTab === 'overview'
                      ? 'bg-slate-100 text-slate-900 font-bold'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  Overview
                </button>
                <button
                  onClick={() => onSelectTab('submit')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'submit'
                      ? 'bg-red-700 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <FilePlus className="w-3.5 h-3.5" />
                  <span>Submit Issue</span>
                </button>
                <button
                  onClick={() => onSelectTab('track')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'track'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Search className="w-3.5 h-3.5" />
                  <span>Track Complaint</span>
                </button>
              </>
            )}

            {/* ADMIN PORTAL TABS */}
            {currentPortal === 'admin' && (
              <>
                <button
                  onClick={() => onSelectTab('triage')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'triage'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Layers className="w-3.5 h-3.5" />
                  <span>Admin Triage</span>
                  {pendingReviewCount > 0 && (
                    <span className="ml-1 px-1.5 py-0.2 text-[10px] font-bold rounded-full bg-amber-500 text-white">
                      {pendingReviewCount}
                    </span>
                  )}
                </button>
              </>
            )}

            {/* TESTING PORTAL TABS */}
            {currentPortal === 'testing' && (
              <>
                <button
                  onClick={() => onSelectTab('workflow')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'workflow'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <Workflow className="w-3.5 h-3.5 text-red-400" />
                  <span>n8n Workflow</span>
                </button>
                <button
                  onClick={() => onSelectTab('benchmark')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'benchmark'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <BarChart2 className="w-3.5 h-3.5" />
                  <span>Benchmark & USP</span>
                </button>
                <button
                  onClick={() => onSelectTab('notion')}
                  className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition-all ${
                    currentTab === 'notion'
                      ? 'bg-slate-900 text-white shadow-sm'
                      : 'text-slate-600 hover:text-slate-900 hover:bg-slate-50'
                  }`}
                >
                  <FileText className="w-3.5 h-3.5 text-red-400" />
                  <span>Notion Docs</span>
                </button>
              </>
            )}
          </div>

          {/* Right Controls: Role Badge, Back to Portal Selection & Logout */}
          <div className="flex items-center space-x-2 shrink-0">
            {currentPortal !== 'selection' && (
              <button
                onClick={() => onSelectPortal('selection')}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center space-x-1 transition-colors"
                title="Back to Portal Selection"
              >
                <ArrowLeft className="w-3.5 h-3.5 text-slate-500" />
                <span className="hidden md:inline">Portal Selection</span>
              </button>
            )}

            {/* If in testing portal and resetDemo prop provided */}
            {currentPortal === 'testing' && onResetDemo && (
              <button
                onClick={onResetDemo}
                className="px-2.5 py-1.5 rounded-lg border border-slate-200 hover:bg-slate-100 text-slate-700 text-xs font-semibold flex items-center space-x-1 transition-colors"
                title="Reset benchmark & test data"
              >
                <RotateCcw className="w-3.5 h-3.5 text-red-600" />
                <span className="hidden sm:inline">Reset Demo</span>
              </button>
            )}

            {/* Session Indicator & Logout */}
            {session ? (
              <div className="flex items-center space-x-1.5">
                <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-800 text-[11px] font-mono font-semibold border border-slate-200 hidden sm:inline-flex items-center space-x-1">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>{session.username}</span>
                  <span className="text-slate-400">({session.role})</span>
                </span>
                <button
                  onClick={onLogout}
                  className="px-2.5 py-1.5 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-red-700 text-slate-700 text-xs font-semibold flex items-center space-x-1 transition-colors"
                  title="Logout demo session"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  <span className="hidden sm:inline">Logout</span>
                </button>
              </div>
            ) : currentPortal !== 'user' && currentPortal !== 'selection' ? (
              <span className="px-2 py-1 rounded-lg bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold flex items-center space-x-1">
                <Lock className="w-3 h-3 text-amber-600" />
                <span>Protected</span>
              </span>
            ) : null}
          </div>
        </div>
      </div>
    </header>
  );
};
