export type IssueCategory = 
  | 'water_leak'
  | 'electrical'
  | 'furniture'
  | 'hvac'
  | 'internet_it'
  | 'cleanliness'
  | 'security'
  | 'other';

export type UrgencyLevel = 'low' | 'medium' | 'high' | 'critical';

export type CaseStatus = 
  | 'submitted'
  | 'held_for_review'
  | 'assigned'
  | 'in_progress'
  | 'resolved'
  | 'rejected';

export interface GemmaExtractionResult {
  issue_type: IssueCategory;
  confidence: number;
  building_block: string;
  floor_or_room?: string | null;
  specific_location_hint: string;
  clean_summary: string;
  detected_urgency: UrgencyLevel;
  estimated_priority_score: number;
  raw_entities: Record<string, any>;
}

export interface DuplicateEvidence {
  matched_case_id: string;
  matched_case_title: string;
  matched_created_at: string;
  semantic_similarity: number;
  location_match_score: number;
  time_window_score: number;
  overall_hybrid_score: number;
  is_duplicate_candidate: boolean;
  reason: string;
  visual_similarity?: number | null;
}

export interface VisualAnalysis {
  brightness: number;
  contrast: number;
  sharpness: number;
  resolution: string;
  aspect_ratio: number;
  is_blurry: boolean;
  is_dark: boolean;
  is_overexposed?: boolean;
}

export interface ProblemImage {
  id: string;
  public_id: string;
  secure_url: string;
  thumbnail_url: string;
  original_filename: string;
  content_type: string;
  byte_size: number;
  width: number;
  height: number;
  perceptual_hash: string;
  blur_variance: number;
  quality_warning?: string | null;
  uploaded_at: string;
  visual_analysis?: VisualAnalysis | null;
}

export interface DispatchEvent {
  event_id: string;
  timestamp: string;
  idempotency_key: string;
  action_taken: string;
  assigned_team?: string | null;
  n8n_execution_id?: string | null;
  workflow_branch: string;
  status_code: number;
  details: Record<string, any>;
}

export interface CaseRecord {
  id: string;
  case_number: string;
  created_at: string;
  raw_complaint: string;
  student_name: string;
  student_email: string;
  extraction: GemmaExtractionResult;
  duplicate_candidates: DuplicateEvidence[];
  is_held_as_duplicate: boolean;
  parent_case_id?: string | null;
  suspected_parent_case_id?: string | null;
  review_status?: 'not_required' | 'pending_human_review' | 'confirmed_duplicate' | 'rejected_duplicate';
  images: ProblemImage[];
  affected_people?: number | null;
  corroborating_report_count: number;
  priority_score: number;
  priority_level: UrgencyLevel;
  priority_reasons: string[];
  last_updated_at?: string | null;
  status: CaseStatus;
  assigned_team?: string | null;
  history: Array<{ timestamp: string; event: string }>;
  n8n_dispatch?: DispatchEvent | null;
  human_review_notes?: string | null;
}

export interface ComplaintCreate {
  raw_text: string;
  student_name?: string;
  student_email?: string;
  reported_block?: string;
  reported_floor?: string;
  affected_people?: number;
}

export interface CaseDecisionRequest {
  decision: 'approve' | 'reject' | 'merge_duplicate';
  reviewer_notes?: string;
  target_team?: string;
  parent_case_id?: string;
}

export interface EvaluationMetrics {
  total_benchmark_cases: number;
  category_macro_f1: number;
  precision_heldout: number;
  recall_heldout: number;
  f1_heldout: number;
  n8n_workflow_success_rate: number;
  ablation_comparison: Record<string, {
    precision: number;
    recall: number;
    f1_score: number;
    false_positive_rate: number;
  }>;
  confusion_matrix: Record<string, Record<string, number>>;
}

export interface DashboardStats {
  total_cases: number;
  held_for_review: number;
  in_progress_or_assigned: number;
  resolved: number;
  duplicates_detected: number;
  critical_priority_cases?: number;
  n8n_webhook_health: string;
  gemma_extraction_health: string;
  cloudinary_configured?: boolean;
  notion_configured?: boolean;
}

export interface UserSession {
  username: string;
  role: 'admin' | 'tester';
  display_name: string;
}

export interface AuthStatusResponse {
  authenticated: boolean;
  user?: UserSession | null;
  demo_mode: boolean;
}

export interface LoginResponse {
  user: UserSession;
  demo_mode: boolean;
  message: string;
  token?: string;
}

export interface NotionStatusResponse {
  configured: boolean;
  parent_page_id?: string | null;
  database_id?: string | null;
  documentation_page_id?: string | null;
  last_synced_at?: string | null;
}

export interface NotionSyncResult {
  status: string;
  page_id?: string | null;
  message: string;
  synced_at: string;
}
