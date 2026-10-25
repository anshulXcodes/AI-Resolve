import React, { useRef, useState } from 'react';
import { 
  Send, 
  Sparkles, 
  MapPin, 
  User, 
  Mail, 
  AlertTriangle, 
  CheckCircle, 
  CopyCheck, 
  Loader2,
  ImagePlus,
  Trash2,
  UploadCloud,
  Users
} from 'lucide-react';
import { ComplaintCreate, CaseRecord } from '../types';
import { apiService } from '../services/api';

interface SubmitPageProps {
  onCaseCreated: (createdCase: CaseRecord) => void;
  initialText?: string;
  onTrackTicket?: (ticketId: string) => void;
}

interface SelectedImage {
  file: File;
  previewUrl: string;
}

export const SubmitPage: React.FC<SubmitPageProps> = ({ onCaseCreated, initialText = '', onTrackTicket }) => {
  const [complaintText, setComplaintText] = useState(initialText);
  const [studentName, setStudentName] = useState('Ananya Sen');
  const [studentEmail, setStudentEmail] = useState('ananya.s@campus.edu');
  const [reportedBlock, setReportedBlock] = useState('Block B');
  const [reportedFloor, setReportedFloor] = useState('2nd Floor');
  const [affectedPeople, setAffectedPeople] = useState('');
  const [selectedImages, setSelectedImages] = useState<SelectedImage[]>([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const imageInputRef = useRef<HTMLInputElement>(null);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastSubmittedCase, setLastSubmittedCase] = useState<CaseRecord | null>(null);

  const addImages = (fileList: FileList | File[]) => {
    const files = Array.from(fileList);
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'webp'];
    const invalid = files.find((file) => {
      const extension = file.name.split('.').pop()?.toLowerCase();
      return !allowedExtensions.includes(extension || '') || file.size > 8 * 1024 * 1024;
    });
    if (invalid) {
      setError(`${invalid.name} is not supported. Use a JPG, PNG, or WEBP image up to 8 MB.`);
      return;
    }
    if (selectedImages.length + files.length > 4) {
      setError('You can attach up to four images to one report.');
      return;
    }
    setError(null);
    setSelectedImages((current) => [
      ...current,
      ...files.map((file) => ({ file, previewUrl: URL.createObjectURL(file) })),
    ]);
  };

  const removeImage = (index: number) => {
    setSelectedImages((current) => {
      URL.revokeObjectURL(current[index].previewUrl);
      return current.filter((_, currentIndex) => currentIndex !== index);
    });
    if (imageInputRef.current) imageInputRef.current.value = '';
  };

  const sampleComplaints = [
    {
      title: "Slide 4 Case 1: Unique Complaint",
      text: "Water across B-block stairway, puddles forming near the second landing and students are slipping.",
      block: "Block B",
      floor: "2nd Floor"
    },
    {
      title: "Slide 4 Case 2: Paraphrased Duplicate Candidate",
      text: "Leaking pipe near the stairs in block B causing water to pool on the walking path.",
      block: "Block B",
      floor: "2nd Floor"
    },
    {
      title: "Urgent Electrical Fire Hazard",
      text: "Sparking switchboard and burning wire smell in Library 3rd floor reading hall near table 14.",
      block: "Central Library",
      floor: "3rd Floor"
    },
    {
      title: "Broken Furniture Report",
      text: "Classroom 204 in Block A has 3 broken student chairs with jagged iron frames sticking out.",
      block: "Block A",
      floor: "Room 204"
    }
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!complaintText.trim() || complaintText.length < 5) {
      setError("Please describe the issue in at least 5 characters.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const payload: ComplaintCreate = {
        raw_text: complaintText,
        student_name: studentName,
        student_email: studentEmail,
        reported_block: reportedBlock,
        reported_floor: reportedFloor,
        affected_people: affectedPeople ? Number(affectedPeople) : undefined,
      };

      const result = await apiService.submitComplaint(
        payload,
        selectedImages.map((image) => image.file),
        setUploadProgress,
      );
      setLastSubmittedCase(result);
      onCaseCreated(result);
      selectedImages.forEach((image) => URL.revokeObjectURL(image.previewUrl));
      setSelectedImages([]);
      setUploadProgress(0);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Failed to process complaint. Please check backend connection.");
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample: typeof sampleComplaints[0]) => {
    setComplaintText(sample.text);
    setReportedBlock(sample.block);
    setReportedFloor(sample.floor);
  };

  const handleDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    addImages(event.dataTransfer.files);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-10 py-6">
      {/* Header */}
      <div className="text-center space-y-2">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-red-100 text-red-800 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Student & Staff Portal</span>
        </div>
        <h1 className="text-3xl font-extrabold text-slate-900">Report a Campus Maintenance Issue</h1>
        <p className="text-slate-600 max-w-xl mx-auto text-sm">
          Describe the problem in plain English. Gemma parses location & urgency, and our hybrid duplicate engine checks against existing reports before automated dispatch.
        </p>
      </div>

      {/* Preset quick test buttons (Mirrors PPT test cases) */}
      <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-500">
            Quick Load Benchmark Scenarios
          </span>
          <span className="text-xs text-red-700 font-medium">Click to populate form</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
          {sampleComplaints.map((sample, idx) => (
            <button
              key={idx}
              type="button"
              onClick={() => loadSample(sample)}
              className="text-left p-3 rounded-xl border border-slate-200 hover:border-red-400 hover:bg-red-50/50 transition-all text-xs space-y-1"
            >
              <div className="font-semibold text-slate-800">{sample.title}</div>
              <div className="text-slate-500 truncate">"{sample.text}"</div>
            </button>
          ))}
        </div>
      </div>

      {/* Complaint Form */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Free-form text */}
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-slate-900">
              Complaint Description <span className="text-red-600">*</span>
            </label>
            <textarea
              rows={4}
              value={complaintText}
              onChange={(e) => setComplaintText(e.target.value)}
              placeholder="e.g. Water across B-block stairway, puddle forming near second landing..."
              className="w-full px-4 py-3 rounded-xl border border-slate-300 focus:border-red-600 focus:ring-2 focus:ring-red-600/20 outline-none text-slate-800 text-sm transition-all"
              required
            />
            <p className="text-xs text-slate-500">
              Include any sensory details, exact floor, room numbers, or hazards.
            </p>
          </div>

          {/* Student metadata */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1.5">
                <User className="w-3.5 h-3.5 text-slate-400" />
                <span>Reporter Name</span>
              </label>
              <input
                type="text"
                value={studentName}
                onChange={(e) => setStudentName(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:border-red-600 outline-none"
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1.5">
                <Mail className="w-3.5 h-3.5 text-slate-400" />
                <span>Reporter Email</span>
              </label>
              <input
                type="email"
                value={studentEmail}
                onChange={(e) => setStudentEmail(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:border-red-600 outline-none"
              />
            </div>
          </div>

          {/* Location cues */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700 flex items-center space-x-1.5">
                <MapPin className="w-3.5 h-3.5 text-slate-400" />
                <span>Building Block Hint</span>
              </label>
              <select
                value={reportedBlock}
                onChange={(e) => setReportedBlock(e.target.value)}
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:border-red-600 outline-none bg-white"
              >
                <option value="Block A">Block A</option>
                <option value="Block B">Block B</option>
                <option value="Block C">Block C</option>
                <option value="Block D">Block D</option>
                <option value="Central Library">Central Library</option>
                <option value="Hostel 1">Hostel 1</option>
                <option value="Hostel 2">Hostel 2</option>
                <option value="Cafeteria">Cafeteria</option>
                <option value="Main Campus">Main Campus</option>
              </select>
            </div>

           {/* Image evidence */}
           <div className="space-y-2">
             <div className="flex items-center justify-between gap-3">
               <label className="text-sm font-semibold text-slate-900 flex items-center gap-2">
                 <ImagePlus className="w-4 h-4 text-red-700" />
                 Photo evidence <span className="font-normal text-slate-500 text-xs">(optional)</span>
               </label>
               <span className="text-[11px] text-slate-500">JPG, PNG, WEBP · up to 8 MB each</span>
             </div>
             <input
               ref={imageInputRef}
               type="file"
               accept="image/jpeg,image/png,image/webp,.jpg,.jpeg,.png,.webp"
               multiple
               className="hidden"
               onChange={(event) => event.target.files && addImages(event.target.files)}
             />
             <div
               role="button"
               tabIndex={0}
               onClick={() => imageInputRef.current?.click()}
               onKeyDown={(event) => event.key === 'Enter' && imageInputRef.current?.click()}
               onDragOver={(event) => event.preventDefault()}
               onDrop={handleDrop}
               className="cursor-pointer rounded-xl border-2 border-dashed border-slate-300 hover:border-red-400 bg-slate-50 hover:bg-red-50/40 px-5 py-6 text-center transition-colors"
             >
               <UploadCloud className="w-6 h-6 text-slate-400 mx-auto mb-2" />
               <p className="text-sm font-semibold text-slate-700">Drag photos here or choose files</p>
               <p className="text-xs text-slate-500 mt-1">OpenCV checks image integrity and quality before secure storage.</p>
             </div>
             {selectedImages.length > 0 && (
               <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-1">
                 {selectedImages.map((image, index) => (
                   <div key={`${image.file.name}-${index}`} className="relative overflow-hidden rounded-xl border border-slate-200 bg-white">
                     <img src={image.previewUrl} alt={`Selected evidence ${index + 1}`} className="h-24 w-full object-cover" />
                     <div className="p-2 pr-8 text-[10px] text-slate-600 truncate" title={image.file.name}>{image.file.name}</div>
                     <button
                       type="button"
                       onClick={(event) => { event.stopPropagation(); removeImage(index); }}
                       className="absolute right-1.5 top-1.5 rounded-full bg-slate-900/80 p-1 text-white hover:bg-red-700"
                       aria-label={`Remove ${image.file.name}`}
                     >
                       <Trash2 className="w-3 h-3" />
                     </button>
                   </div>
                 ))}
               </div>
             )}
           </div>

           <div className="space-y-1.5 max-w-xs">
             <label className="text-xs font-semibold text-slate-700 flex items-center gap-1.5">
               <Users className="w-3.5 h-3.5 text-slate-400" /> Estimated people affected <span className="font-normal text-slate-400">(optional)</span>
             </label>
             <input
               type="number"
               min="0"
               value={affectedPeople}
               onChange={(event) => setAffectedPeople(event.target.value)}
               placeholder="e.g. 50"
               className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:border-red-600 outline-none"
             />
           </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-slate-700">Floor / Room Hint</label>
              <input
                type="text"
                value={reportedFloor}
                onChange={(e) => setReportedFloor(e.target.value)}
                placeholder="e.g. 2nd Floor, Stairway"
                className="w-full px-3.5 py-2 rounded-lg border border-slate-300 text-sm focus:border-red-600 outline-none"
              />
            </div>
          </div>

          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-800 text-sm flex items-center space-x-2">
              <AlertTriangle className="w-5 h-5 text-red-600 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-6 rounded-xl bg-red-700 hover:bg-red-800 text-white font-semibold text-sm shadow-md shadow-red-700/20 flex items-center justify-center space-x-2 transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>{selectedImages.length ? `Uploading evidence ${uploadProgress}% & analysing issue...` : 'Running Gemma Extraction & Hybrid Duplicate Engine...'}</span>
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                <span>Process & Route Complaint</span>
              </>
            )}
          </button>
        </form>
      </div>

      {/* Live Result Feedback Card after submission */}
      {lastSubmittedCase && (
        <div className="bg-white rounded-2xl border-2 border-red-200 shadow-lg p-6 space-y-6">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center font-bold">
                ✓
              </div>
              <div>
                <h3 className="font-bold text-slate-900">Case Created: {lastSubmittedCase.case_number}</h3>
                <p className="text-xs text-slate-500">Processed through Gemma NLP & n8n Router</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {lastSubmittedCase.is_held_as_duplicate ? (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-amber-100 text-amber-900 border border-amber-300 flex items-center space-x-1">
                  <CopyCheck className="w-3.5 h-3.5 text-amber-700" />
                  <span>Held for Human Review (Suspected Duplicate)</span>
                </span>
              ) : (
                <span className="px-3 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-900 border border-emerald-300 flex items-center space-x-1">
                  <CheckCircle className="w-3.5 h-3.5 text-emerald-700" />
                  <span>Assigned: {lastSubmittedCase.assigned_team}</span>
                </span>
              )}
              {onTrackTicket && (
                <button
                  type="button"
                  onClick={() => onTrackTicket(lastSubmittedCase.case_number)}
                  className="px-3 py-1 rounded-full text-xs font-bold bg-slate-900 hover:bg-slate-800 text-white transition-all shadow-sm flex items-center space-x-1"
                >
                  <span>Track Ticket</span>
                  <span>→</span>
                </button>
              )}
            </div>
          </div>

          {/* Extraction summary */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-slate-500 font-medium">Classified Category</div>
              <div className="text-sm font-bold text-slate-900 capitalize mt-0.5">
                {lastSubmittedCase.extraction.issue_type.replace('_', ' ')}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                Confidence: {(lastSubmittedCase.extraction.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-slate-500 font-medium">Location Extracted</div>
              <div className="text-sm font-bold text-slate-900 mt-0.5">
                {lastSubmittedCase.extraction.building_block}
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                {lastSubmittedCase.extraction.floor_or_room || lastSubmittedCase.extraction.specific_location_hint}
              </div>
            </div>

            <div className="p-3 rounded-xl bg-slate-50 border border-slate-200">
              <div className="text-slate-500 font-medium">Priority & Urgency</div>
              <div className="text-sm font-bold text-slate-900 uppercase mt-0.5">
                {lastSubmittedCase.priority_level} ({lastSubmittedCase.priority_score}/10)
              </div>
              <div className="text-[11px] text-slate-500 mt-1">
                {lastSubmittedCase.corroborating_report_count} corroborating report{lastSubmittedCase.corroborating_report_count === 1 ? '' : 's'} · n8n: {lastSubmittedCase.n8n_dispatch?.workflow_branch}
              </div>
            </div>
          </div>

          {/* Duplicate candidates view if any */}
          {lastSubmittedCase.duplicate_candidates && lastSubmittedCase.duplicate_candidates.length > 0 && (
            <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-200 space-y-2">
              <div className="text-xs font-bold text-amber-900 flex items-center space-x-1.5">
                <AlertTriangle className="w-4 h-4 text-amber-700" />
                <span>Duplicate Candidate Matches Detected (Never Auto-Merged):</span>
              </div>
              {lastSubmittedCase.duplicate_candidates.map((cand, i) => (
                <div key={i} className="text-xs bg-white p-3 rounded-lg border border-amber-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="font-semibold text-slate-900">Matches Case #{cand.matched_case_id}:</span> {cand.matched_case_title}
                    <p className="text-[11px] text-slate-500 mt-0.5">{cand.reason}</p>
                    {cand.visual_similarity !== null && cand.visual_similarity !== undefined && (
                      <p className="text-[11px] text-slate-500">Visual similarity: {(cand.visual_similarity * 100).toFixed(0)}%</p>
                    )}
                  </div>
                  <div className="text-right shrink-0">
                    <span className="px-2 py-0.5 rounded font-mono font-bold bg-amber-100 text-amber-800 text-xs">
                      Hybrid Score: {(cand.overall_hybrid_score * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
          {lastSubmittedCase.images.length > 0 && (
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-700">OpenCV-Validated Evidence (Cloudinary Stored)</div>
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                {lastSubmittedCase.images.map((image) => (
                  <div key={image.id} className="rounded-xl overflow-hidden border border-slate-200 bg-white">
                    <a href={image.secure_url} target="_blank" rel="noreferrer" className="block relative group">
                      <img src={image.thumbnail_url} alt={image.original_filename} className="h-28 w-full object-cover group-hover:opacity-90 transition-opacity" />
                      <div className="absolute top-1.5 right-1.5 bg-slate-900/80 text-[10px] text-white px-1.5 py-0.5 rounded font-mono">
                        {image.width}×{image.height}
                      </div>
                    </a>
                    <div className="p-2.5 space-y-1">
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
        </div>
      )}
    </div>
  );
};
