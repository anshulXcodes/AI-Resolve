import React, { useState, useEffect, useCallback } from 'react';
import { Navbar } from './components/Navbar';
import { PortalSelectionPage } from './pages/PortalSelectionPage';
import { LandingPage } from './pages/LandingPage';
import { SubmitPage } from './pages/SubmitPage';
import { TrackComplaintPage } from './pages/TrackComplaintPage';
import { DashboardPage } from './pages/DashboardPage';
import { WorkflowView } from './pages/WorkflowView';
import { BenchmarkPage } from './pages/BenchmarkPage';
import { NotionDocsPage } from './pages/NotionDocsPage';
import { LoginModal } from './components/LoginModal';
import { CaseRecord, UserSession } from './types';
import { apiService } from './services/api';
import { RotateCcw } from 'lucide-react';

export function App() {
  // Parse initial state from URL query parameters
  const [currentPortal, setCurrentPortal] = useState<'selection' | 'user' | 'admin' | 'testing'>('selection');
  const [currentTab, setCurrentTab] = useState<string>('overview');
  const [trackedTicketId, setTrackedTicketId] = useState<string>('');

  const [session, setSession] = useState<UserSession | null>(null);
  const [loginModalRole, setLoginModalRole] = useState<'admin' | 'tester' | null>(null);

  const [cases, setCases] = useState<CaseRecord[]>([]);
  const [selectedCaseDetail, setSelectedCaseDetail] = useState<CaseRecord | null>(null);
  const [initialSubmitText, setInitialSubmitText] = useState<string>('');

  // Synchronize URL query params
  const syncUrl = useCallback((portal: string, tab: string, ticket?: string) => {
    const params = new URLSearchParams();
    if (portal !== 'selection') {
      params.set('portal', portal);
      if (tab) params.set('tab', tab);
    }
    if (ticket) {
      params.set('ticket', ticket);
    }
    const newQuery = params.toString() ? `?${params.toString()}` : window.location.pathname;
    window.history.replaceState(null, '', newQuery);
  }, []);

  // Fetch session on initial load
  const verifySession = useCallback(async () => {
    try {
      const auth = await apiService.getAuthStatus();
      if (auth.authenticated && auth.user) {
        setSession(auth.user);
        return auth.user;
      } else {
        setSession(null);
        return null;
      }
    } catch {
      setSession(null);
      return null;
    }
  }, []);

  // Load cases safely based on active role
  const fetchCasesForRole = useCallback(async (activeSession: UserSession | null) => {
    if (!activeSession) return;
    try {
      if (activeSession.role === 'admin') {
        const data = await apiService.getCases();
        setCases(data);
      } else if (activeSession.role === 'tester') {
        const data = await apiService.getTestingCases();
        setCases(data);
      }
    } catch (err) {
      console.error("Failed to load role cases:", err);
    }
  }, []);

  // Initial mount: check URL & authenticate
  useEffect(() => {
    const init = async () => {
      const activeUser = await verifySession();
      const params = new URLSearchParams(window.location.search);
      const portalParam = params.get('portal');
      const tabParam = params.get('tab');
      const ticketParam = params.get('ticket');

      if (ticketParam) {
        setTrackedTicketId(ticketParam);
      }

      if (portalParam === 'admin') {
        if (activeUser?.role === 'admin') {
          setCurrentPortal('admin');
          setCurrentTab(tabParam || 'triage');
          fetchCasesForRole(activeUser);
        } else {
          setCurrentPortal('admin');
          setLoginModalRole('admin');
        }
      } else if (portalParam === 'testing') {
        if (activeUser?.role === 'tester') {
          setCurrentPortal('testing');
          setCurrentTab(tabParam || 'workflow');
          fetchCasesForRole(activeUser);
        } else {
          setCurrentPortal('testing');
          setLoginModalRole('tester');
        }
      } else if (portalParam === 'user') {
        setCurrentPortal('user');
        setCurrentTab(tabParam || (ticketParam ? 'track' : 'overview'));
      } else {
        setCurrentPortal('selection');
      }
    };

    init();

    // Listen to browser back/forward
    const handlePopState = () => {
      const params = new URLSearchParams(window.location.search);
      const portal = (params.get('portal') as any) || 'selection';
      const tab = params.get('tab') || 'overview';
      setCurrentPortal(portal);
      setCurrentTab(tab);
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [verifySession, fetchCasesForRole]);

  // Handle portal selection from landing or navigation
  const handleSelectPortal = (portal: 'selection' | 'user' | 'admin' | 'testing') => {
    if (portal === 'user') {
      setCurrentPortal('user');
      setCurrentTab('overview');
      setLoginModalRole(null);
      syncUrl('user', 'overview');
    } else if (portal === 'admin') {
      if (session?.role === 'admin') {
        setCurrentPortal('admin');
        setCurrentTab('triage');
        setLoginModalRole(null);
        syncUrl('admin', 'triage');
        fetchCasesForRole(session);
      } else {
        setLoginModalRole('admin');
      }
    } else if (portal === 'testing') {
      if (session?.role === 'tester') {
        setCurrentPortal('testing');
        setCurrentTab('workflow');
        setLoginModalRole(null);
        syncUrl('testing', 'workflow');
        fetchCasesForRole(session);
      } else {
        setLoginModalRole('tester');
      }
    } else {
      setCurrentPortal('selection');
      setLoginModalRole(null);
      syncUrl('selection', '');
    }
  };

  const handleSelectTab = (tab: string) => {
    setCurrentTab(tab);
    syncUrl(currentPortal, tab);
  };

  const handleLoginSuccess = (newSession: UserSession) => {
    setSession(newSession);
    const targetPortal = newSession.role === 'admin' ? 'admin' : 'testing';
    const defaultTab = targetPortal === 'admin' ? 'triage' : 'workflow';
    setCurrentPortal(targetPortal);
    setCurrentTab(defaultTab);
    setLoginModalRole(null);
    syncUrl(targetPortal, defaultTab);
    fetchCasesForRole(newSession);
  };

  const handleLogout = async () => {
    try {
      await apiService.logout();
    } catch {
      // Ignore
    }
    setSession(null);
    setCurrentPortal('selection');
    setLoginModalRole(null);
    syncUrl('selection', '');
  };

  const handleStartDemo = (demoType: 'unique' | 'paraphrased') => {
    if (demoType === 'unique') {
      setInitialSubmitText("Water across B-block stairway, puddles forming near the second landing and students are slipping.");
    } else {
      setInitialSubmitText("Leaking pipe near the stairs in block B causing water to pool on the walkway.");
    }
    setCurrentPortal('user');
    setCurrentTab('submit');
    syncUrl('user', 'submit');
  };

  const handleCaseCreated = (createdCase: CaseRecord) => {
    if (session?.role === 'admin') {
      fetchCasesForRole(session);
    }
  };

  const handleTrackTicket = (ticketId: string) => {
    setTrackedTicketId(ticketId);
    setCurrentPortal('user');
    setCurrentTab('track');
    syncUrl('user', 'track', ticketId);
  };

  const handleResetDemo = async () => {
    if (window.confirm("Reset all cases back to initial benchmark state for clean hackathon demo?")) {
      try {
        await apiService.resetDemo();
        if (session) {
          await fetchCasesForRole(session);
        }
        alert("Demo state successfully reset.");
      } catch (e) {
        console.error("Reset error:", e);
      }
    }
  };

  const pendingReviewCount = cases.filter(c => c.status === 'held_for_review').length;

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col text-slate-900 selection:bg-red-200">
      <Navbar 
        currentPortal={currentPortal}
        currentTab={currentTab} 
        onSelectPortal={handleSelectPortal}
        onSelectTab={handleSelectTab} 
        pendingReviewCount={pendingReviewCount} 
        session={session}
        onLogout={handleLogout}
        onResetDemo={session?.role === 'tester' ? handleResetDemo : undefined}
      />

      <main className="flex-1 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full pb-16">
        {/* 1. PORTAL SELECTION LANDING PAGE */}
        {currentPortal === 'selection' && (
          <PortalSelectionPage 
            onSelectPortal={handleSelectPortal}
            onStartDemo={handleStartDemo}
            userRole={session?.role}
          />
        )}

        {/* 2. USER PORTAL (PUBLIC) */}
        {currentPortal === 'user' && (
          <>
            {currentTab === 'overview' && (
              <LandingPage 
                onStartDemo={handleStartDemo} 
                onNavigateToTab={(t) => {
                  if (t === 'submit') handleSelectTab('submit');
                  else if (t === 'dashboard') handleSelectPortal('admin');
                  else if (t === 'workflow' || t === 'benchmark') handleSelectPortal('testing');
                }} 
              />
            )}

            {currentTab === 'submit' && (
              <SubmitPage 
                onCaseCreated={handleCaseCreated} 
                initialText={initialSubmitText} 
                onTrackTicket={handleTrackTicket}
              />
            )}

            {currentTab === 'track' && (
              <TrackComplaintPage 
                initialTicketId={trackedTicketId}
              />
            )}
          </>
        )}

        {/* 3. ADMIN PORTAL (PROTECTED) */}
        {currentPortal === 'admin' && session?.role === 'admin' && (
          <>
            {currentTab === 'triage' && (
              <DashboardPage 
                cases={cases} 
                onRefresh={() => fetchCasesForRole(session)} 
                onSelectCase={(c) => setSelectedCaseDetail(c)} 
              />
            )}
          </>
        )}

        {/* 4. TESTING PORTAL (PROTECTED) */}
        {currentPortal === 'testing' && session?.role === 'tester' && (
          <>
            {currentTab === 'workflow' && (
              <WorkflowView cases={cases} />
            )}

            {currentTab === 'benchmark' && (
              <BenchmarkPage />
            )}

            {currentTab === 'notion' && (
              <NotionDocsPage />
            )}
          </>
        )}
      </main>

      {/* Login Modal for Protected Portals */}
      {loginModalRole && (
        <LoginModal 
          portalRole={loginModalRole}
          onLoginSuccess={handleLoginSuccess}
          onCancel={() => {
            setLoginModalRole(null);
            setCurrentPortal('selection');
            syncUrl('selection', '');
          }}
        />
      )}

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
                  <div className="font-bold text-slate-800">{selectedCaseDetail.priority_score}/10 ({selectedCaseDetail.priority_level})</div>
                </div>
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                  <div className="text-slate-400">Confidence</div>
                  <div className="font-bold text-slate-800">{(selectedCaseDetail.extraction.confidence * 100).toFixed(0)}%</div>
                </div>
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs">
              <div className="font-bold text-slate-700 uppercase tracking-wider">Priority evidence</div>
              <p className="text-slate-600 mt-1">{selectedCaseDetail.corroborating_report_count} corroborating report{selectedCaseDetail.corroborating_report_count === 1 ? '' : 's'}</p>
              <ul className="list-disc ml-4 mt-1 space-y-0.5 text-slate-600">
                {selectedCaseDetail.priority_reasons.map((reason, index) => <li key={index}>{reason}</li>)}
              </ul>
            </div>

            {selectedCaseDetail.images.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wider">OpenCV & Cloudinary Evidence</h4>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {selectedCaseDetail.images.map((image) => (
                    <div key={image.id} className="rounded-xl overflow-hidden border border-slate-200 bg-white">
                      <a href={image.secure_url} target="_blank" rel="noreferrer" className="block relative group">
                        <img src={image.thumbnail_url} alt={image.original_filename} className="h-28 w-full object-cover group-hover:opacity-90 transition-opacity" />
                        <div className="absolute top-1.5 right-1.5 bg-slate-900/80 text-[10px] text-white px-1.5 py-0.5 rounded font-mono">
                          {image.width}×{image.height}
                        </div>
                      </a>
                      <div className="p-2 text-[10px] space-y-0.5 text-slate-600">
                        <div className="truncate font-medium">{image.original_filename}</div>
                        {image.visual_analysis && (
                          <div className="font-mono text-slate-500">
                            Sharpness: {image.visual_analysis.sharpness} · Brightness: {image.visual_analysis.brightness}
                          </div>
                        )}
                        {image.quality_warning ? (
                          <div className="text-amber-700 font-medium">Quality review suggested</div>
                        ) : (
                          <div className="text-emerald-700 font-medium">✓ OpenCV Validated</div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Duplicate Candidates Breakdown */}
            {selectedCaseDetail.duplicate_candidates && selectedCaseDetail.duplicate_candidates.length > 0 && (
              <div className="space-y-2">
                <h4 className="text-xs font-bold text-amber-800 uppercase tracking-wider">Duplicate Candidate Evidence</h4>
                {selectedCaseDetail.duplicate_candidates.map((cand, idx) => (
                  <div key={idx} className="p-3.5 rounded-xl bg-amber-50/80 border border-amber-200 text-xs space-y-1">
                    <div className="font-bold text-slate-900">Matches: #{cand.matched_case_id} — {cand.matched_case_title}</div>
                    <p className="text-slate-600">{cand.reason}</p>
                    <div className="font-mono text-[11px] text-amber-900 pt-1">
                      Hybrid: {(cand.overall_hybrid_score * 100).toFixed(1)}% | Semantic: {(cand.semantic_similarity * 100).toFixed(1)}% | Location: {(cand.location_match_score * 100).toFixed(1)}% | Time: {(cand.time_window_score * 100).toFixed(1)}%{cand.visual_similarity !== null && cand.visual_similarity !== undefined ? ` | Visual: ${(cand.visual_similarity * 100).toFixed(1)}%` : ''}
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
    </div>
  );
}

export default App;
