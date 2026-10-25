import React, { useState, useEffect } from 'react';
import { 
  Search, 
  CheckCircle2, 
  Clock, 
  AlertTriangle, 
  UserCheck, 
  CopyCheck, 
  ShieldCheck, 
  MapPin, 
  Sparkles, 
  Image as ImageIcon,
  ChevronRight,
  ExternalLink,
  History
} from 'lucide-react';
import { CaseRecord, CaseStatus } from '../types';
import { apiService } from '../services/api';

interface TrackComplaintPageProps {
  initialTicketId?: string;
}

export const TrackComplaintPage: React.FC<TrackComplaintPageProps> = ({ initialTicketId = '' }) => {
  const [searchInput, setSearchInput] = useState(initialTicketId);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [trackedCase, setTrackedCase] = useState<CaseRecord | null>(null);
  const [recentTickets, setRecentTickets] = useState<string[]>([]);

  useEffect(() => {
    try {
      const stored = localStorage.getItem('resolveai_recent_tickets');
      if (stored) {
        setRecentTickets(JSON.parse(stored));
      }
    } catch {
      // Ignore localStorage errors
    }
  }, []);

  useEffect(() => {
    if (initialTicketId) {
      setSearchInput(initialTicketId);
      performSearch(initialTicketId);
    }
  }, [initialTicketId]);

  const performSearch = async (ticketQuery: string) => {
    if (!ticketQuery.trim()) {
      setError('Please enter a ticket number or case ID.');
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await apiService.trackComplaint(ticketQuery.trim());
      setTrackedCase(data);
      // Save to recent tickets in localStorage
      try {
        const updated = Array.from(new Set([data.case_number, ...recentTickets])).slice(0, 6);
        setRecentTickets(updated);
        localStorage.setItem('resolveai_recent_tickets', JSON.stringify(updated));
      } catch {
        // Ignore localStorage error
      }
    } catch (err: any) {
      setTrackedCase(null);
      setError(
        err?.response?.data?.detail || 
        `No complaint found for "${ticketQuery}". Check your ticket number (e.g. RES-2026-101) and try again.`
      );
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    performSearch(searchInput);
  };

  const getStatusBadge = (status: CaseStatus, isHeld: boolean) => {
    if (isHeld || status === 'held_for_review') {
      return (
        <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300">
          <CopyCheck className="w-3.5 h-3.5 text-amber-700" />
          <span>Held for Review (Duplicate Candidate)</span>
        </span>
      );
    }
    switch (status) {
      case 'assigned':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-blue-100 text-blue-900 border border-blue-200">
            <UserCheck className="w-3.5 h-3.5 text-blue-700" />
            <span>Assigned to Department</span>
          </span>
        );
      case 'in_progress':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-indigo-100 text-indigo-900 border border-indigo-200">
            <Clock className="w-3.5 h-3.5 text-indigo-700" />
            <span>Work In Progress</span>
          </span>
        );
      case 'resolved':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-200">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-700" />
            <span>Resolved</span>
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700 capitalize">
            {status}
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8 py-6">
      {/* Title */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-red-100 text-red-800 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Public Ticket Tracker</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900">Track Campus Maintenance Ticket</h1>
        <p className="text-slate-600 max-w-xl mx-auto text-sm">
          Check live dispatch status, department assignment, Gemma analysis, and audit timeline for your campus reports.
        </p>
      </div>

      {/* Search Bar */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 space-y-4">
        <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 absolute left-3.5 top-3.5 text-slate-400" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="Enter Ticket ID (e.g. RES-2026-101) or Case ID..."
              className="w-full pl-10 pr-4 py-2.5 rounded-xl border border-slate-300 text-sm focus:border-red-600 focus:ring-2 focus:ring-red-600/20 outline-none"
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="px-6 py-2.5 rounded-xl bg-red-700 hover:bg-red-800 text-white font-semibold text-sm transition-all shadow-md shadow-red-700/20 disabled:opacity-50 shrink-0"
          >
            {loading ? "Searching..." : "Track Status"}
          </button>
        </form>

        {/* Quick Recent / Seed Ticket suggestions */}
        <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100 text-xs">
          <span className="text-slate-500 font-medium">Quick Track:</span>
          {['RES-2026-101', 'RES-2026-102', 'RES-2026-103', ...recentTickets]
            .filter((val, idx, arr) => arr.indexOf(val) === idx)
            .slice(0, 5)
            .map((ticketId) => (
              <button
                key={ticketId}
                type="button"
                onClick={() => {
                  setSearchInput(ticketId);
                  performSearch(ticketId);
                }}
                className="px-2.5 py-1 rounded-lg bg-slate-100 hover:bg-red-50 hover:text-red-700 text-slate-700 font-mono text-[11px] font-semibold transition-colors"
              >
                {ticketId}
              </button>
            ))}
        </div>

        {error && (
          <div className="p-3.5 rounded-xl bg-red-50 border border-red-200 text-red-800 text-xs flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-red-600 shrink-0" />
            <span>{error}</span>
          </div>
        )}
      </div>

      {/* Case Details Card */}
      {trackedCase && (
        <div className="bg-white rounded-2xl border-2 border-slate-200 shadow-xl p-6 sm:p-8 space-y-6">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-100 pb-5">
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-sm font-mono font-bold text-red-700 bg-red-50 px-2.5 py-0.5 rounded-lg border border-red-200">
                  {trackedCase.case_number}
                </span>
                <span className="text-xs text-slate-400">
                  Reported {new Date(trackedCase.created_at).toLocaleString()}
                </span>
              </div>
              <h2 className="text-xl font-bold text-slate-900 mt-1.5">
                {trackedCase.extraction.clean_summary || trackedCase.raw_complaint}
              </h2>
            </div>
            <div>
              {getStatusBadge(trackedCase.status, trackedCase.is_held_as_duplicate)}
            </div>
          </div>

          {/* Metadata Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block font-medium">Assigned Team</span>
              <span className="text-slate-900 font-bold block mt-1">
                {trackedCase.assigned_team || 'Pending Assignment'}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block font-medium">Category</span>
              <span className="text-slate-900 font-bold capitalize block mt-1">
                {trackedCase.extraction.issue_type.replace('_', ' ')}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block font-medium">Location</span>
              <span className="text-slate-900 font-bold block mt-1">
                {trackedCase.extraction.building_block}
              </span>
              <span className="text-[11px] text-slate-500">
                {trackedCase.extraction.floor_or_room || trackedCase.extraction.specific_location_hint}
              </span>
            </div>
            <div className="p-3.5 rounded-xl bg-slate-50 border border-slate-200">
              <span className="text-slate-400 block font-medium">Priority Score</span>
              <span className="text-slate-900 font-bold uppercase block mt-1">
                {trackedCase.priority_level} ({trackedCase.priority_score}/10)
              </span>
              <span className="text-[11px] text-slate-500">
                {trackedCase.corroborating_report_count} corroborating report{trackedCase.corroborating_report_count === 1 ? '' : 's'}
              </span>
            </div>
          </div>

          {/* Raw submission quote */}
          <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-1 text-xs">
            <span className="font-bold text-slate-500 uppercase tracking-wider text-[11px]">Reporter Description</span>
            <p className="text-slate-800 italic">"{trackedCase.raw_complaint}"</p>
            <p className="text-[11px] text-slate-400 pt-1">
              Submitted by {trackedCase.student_name} ({trackedCase.student_email})
            </p>
          </div>

          {/* Duplicate review alert if held */}
          {trackedCase.is_held_as_duplicate && (
            <div className="p-4 rounded-xl bg-amber-50 border border-amber-200 space-y-1.5 text-xs">
              <div className="flex items-center space-x-1.5 text-amber-900 font-bold">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                <span>Notice: Similar Active Report Detected</span>
              </div>
              <p className="text-slate-700">
                Our hybrid duplicate engine flagged that this issue might correspond to an ongoing maintenance ticket in this area. A campus facility supervisor will review before final dispatch.
              </p>
            </div>
          )}

          {/* Stored OpenCV / Cloudinary Image Evidence */}
          {trackedCase.images.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
                <ImageIcon className="w-3.5 h-3.5 text-red-600" />
                <span>OpenCV-Validated Evidence (Stored in Cloudinary)</span>
              </h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {trackedCase.images.map((image) => (
                  <div key={image.id} className="rounded-xl overflow-hidden border border-slate-200 bg-white">
                    <a href={image.secure_url} target="_blank" rel="noreferrer" className="block relative group">
                      <img src={image.thumbnail_url} alt={image.original_filename} className="h-28 w-full object-cover group-hover:opacity-90 transition-opacity" />
                      <div className="absolute top-1.5 right-1.5 bg-slate-900/80 text-[10px] text-white px-1.5 py-0.5 rounded font-mono">
                        {image.width}×{image.height}
                      </div>
                    </a>
                    <div className="p-2.5 space-y-1 text-xs">
                      <div className="text-[11px] font-semibold text-slate-800 truncate" title={image.original_filename}>
                        {image.original_filename}
                      </div>
                      {image.visual_analysis && (
                        <div className="text-[10px] text-slate-500 font-mono">
                          Sharpness: {image.visual_analysis.sharpness} · Brightness: {image.visual_analysis.brightness}
                        </div>
                      )}
                      {image.quality_warning ? (
                        <div className="text-[10px] text-amber-700 bg-amber-50 px-1.5 py-0.5 rounded border border-amber-200">
                          {image.quality_warning}
                        </div>
                      ) : (
                        <div className="text-[10px] text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                          ✓ OpenCV Integrity Verified
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Audit Trail Timeline */}
          <div className="space-y-3 pt-2 border-t border-slate-100">
            <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center space-x-1.5">
              <History className="w-3.5 h-3.5 text-slate-500" />
              <span>Ticket Resolution History</span>
            </h3>
            <div className="space-y-2 border-l-2 border-red-200 pl-4 ml-2">
              {trackedCase.history.map((h, i) => (
                <div key={i} className="text-xs relative">
                  <div className="w-2.5 h-2.5 rounded-full bg-red-600 absolute -left-[21px] top-1" />
                  <span className="font-medium text-slate-800">{h.event}</span>
                  <span className="text-[10px] text-slate-400 ml-2 font-mono">
                    {new Date(h.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
