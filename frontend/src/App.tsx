import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { LandingPage } from './pages/LandingPage';
import { SubmitPage } from './pages/SubmitPage';
import { DashboardPage } from './pages/DashboardPage';
import { WorkflowView } from './pages/WorkflowView';
import { BenchmarkPage } from './pages/BenchmarkPage';
import { CaseRecord } from './types';
import { apiService } from './services/api';
import { 
  FileText, 
  Clock, 
  CheckCircle, 
  GitBranch, 
  ShieldCheck, 
  RotateCcw,
  Sparkles,
  ExternalLink
} from 'lucide-react';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('landing');
  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [loadingCases, setLoadingCases] = useState<boolean>(true);
  const [selectedCaseDetail, setSelectedCaseDetail] = useState<CaseRecord | null>(null);
  const [initialSubmitText, setInitialSubmitText] = useState<string>('');

  const fetchCases = async () => {
    try {
      const data = await apiService.getCases();
      setCases(data);
    } catch (err) {
      console.error("Failed to load cases:", err);
    } finally {
      setLoadingCases(false);
    }
  };

  useEffect(() => {
    fetchCases();
  }, []);

  const pendingReviewCount = cases.filter(c => c.status === 'held_for_review').length;

  const handleStartDemo = (demoType: 'unique' | 'paraphrased') => {
    if (demoType === 'unique') {
      setInitialSubmitText("Water across B-block stairway, puddles forming near the second landing and students are slipping.");
    } else {
      setInitialSubmitText("Leaking pipe near the stairs in block B causing water to pool on the walkway.");
    }
    setCurrentTab('submit');
  };

  const handleCaseCreated = (newCase: CaseRecord) => {
    fetchCases();
  };

  const handleResetDemo = async () => {
    if (window.confirm("Reset all cases back to initial benchmark state for clean hackathon demo?")) {
      try {
        await apiService.resetDemo();
        await fetchCases();
        alert("Demo state successfully reset.");
      } catch (e) {
        console.error("Reset error:", e);
      }
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 selection:bg-red-200">
      <Navbar 
        currentTab={currentTab} 
        setCurrentTab={setCurrentTab} 
        pendingReviewCount={pendingReviewCount} 
      />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full pb-16">
        {currentTab === 'landing' && (
          <LandingPage 
            onStartDemo={handleStartDemo} 
            onNavigateToTab={setCurrentTab} 
          />
        )}

        {currentTab === 'submit' && (
          <SubmitPage 
            onCaseCreated={handleCaseCreated} 
            initialText={initialSubmitText} 
          />
        )}

        {currentTab === 'dashboard' && (
          <DashboardPage 
            cases={cases} 
            onRefresh={fetchCases} 
            onSelectCase={(c) => setSelectedCaseDetail(c)} 
          />
        )}

        {currentTab === 'workflow' && (
          <WorkflowView cases={cases} />
        )}

        {currentTab === 'benchmark' && (
          <BenchmarkPage />
        )}
      </main>

      {/* Case Detail / Audit Modal */}
      {selectedCaseDetail && (
        <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl max-w-2xl w-full border border-slate-200 shadow-2xl p-6 space-y-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-start border-b border-slate-100 pb-4">
              <div>
                <span className="text-xs font-mono font-bold text-red-700">{selectedCaseDetail.case_number}</span>
                <h3 className="text-xl font-bold text-slate-900 mt-1">Audit Trail & Evidence Record</h3>
              </div>
              <button 
                onClick={() => setSelectedCaseDetail(null)}
                className="text-slate-400 hover:text-slate-600 p-1 rounded-lg text-lg"
              >
                ✕
              </button>
            </div>

            {/* Original Complaint */}
            <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
              <span className="text-xs font-bold text-slate-500 uppercase tracking-wider">Raw Student Submission</span>
              <p className="text-sm text-slate-800 font-medium italic">"{selectedCaseDetail.raw_complaint}"</p>
              <p className="text-xs text-slate-400 pt-1">Reported by {selectedCaseDetail.student_name} ({selectedCaseDetail.student_email})</p>
            </div>

            {/* Gemma Extraction Details */}
            <div className="space-y-2">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Gemma Structured Extraction</h4>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-xs">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-slate-400">Category</div>
                  <div className="font-bold text-slate-800 capitalize">{selectedCaseDetail.extraction.issue_type}</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-slate-400">Building</div>
                  <div className="font-bold text-slate-800">{selectedCaseDetail.extraction.building_block}</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-slate-400">Priority</div>
                  <div className="font-bold text-slate-800">{selectedCaseDetail.extraction.estimated_priority_score}/10 ({selectedCaseDetail.extraction.detected_urgency})</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-slate-400">Confidence</div>
                  <div className="font-bold text-slate-800">{(selectedCaseDetail.extraction.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>

            {/* Duplicate Candidates Breakdown */}
            {selectedCaseDetail.duplicate_candidates && selectedCaseDetail.duplicate_candidates.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider">Duplicate Candidate Evidence</h4>
                {selectedCaseDetail.duplicate_candidates.map((cand, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-xs space-y-1">
                    <div className="font-bold text-slate-900">Matches: #{cand.matched_case_id} — {cand.matched_case_title}</div>
                    <p className="text-slate-600">{cand.reason}</p>
                    <div className="font-mono text-[11px] text-amber-900 pt-1">
                      Hybrid: {(cand.overall_hybrid_score * 100).toFixed(1)}% | Semantic: {(cand.semantic_similarity * 100).toFixed(1)}% | Location: {(cand.location_match_score * 100).toFixed(1)}% | Time: {(cand.time_window_score * 100).toFixed(1)}%
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Event Timeline */}
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">Immutable History Timeline</h4>
              <div className="space-y-2 border-l-2 border-red-200 pl-4 ml-2">
                {selectedCaseDetail.history.map((h, i) => (
                  <div key={i} className="text-xs relative">
                    <div className="w-2.5 h-2.5 rounded-full bg-red-600 absolute -left-[21px] top-1" />
                    <span className="font-medium text-slate-800">{h.event}</span>
                    <span className="text-[10px] text-slate-400 ml-2 font-mono">{new Date(h.timestamp).toLocaleTimeString()}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div className="flex justify-end pt-2 border-t border-slate-100">
              <button
                onClick={() => setSelectedCaseDetail(null)}
                className="px-4 py-2 rounded-xl bg-slate-900 text-white text-xs font-semibold hover:bg-slate-800"
              >
                Close Audit Record
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Floating Demo Reset Button for Judges */}
      <div className="fixed bottom-4 right-4 z-40">
        <button
          onClick={handleResetDemo}
          className="px-3 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-900 text-white text-xs font-semibold flex items-center space-x-1.5 shadow-xl border border-slate-700 backdrop-blur transition-all"
          title="Reset demo data to initial state"
        >
          <RotateCcw className="w-3.5 h-3.5 text-red-400" />
          <span>Reset Demo</span>
        </button>
      </div>
    </div>
  );
}

export default App;
