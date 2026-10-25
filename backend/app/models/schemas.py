from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class IssueCategory(str, Enum):
    WATER_LEAK = "water_leak"
    ELECTRICAL = "electrical"
    FURNITURE = "furniture"
    HVAC = "hvac"
    INTERNET_IT = "internet_it"
    CLEANLINESS = "cleanliness"
    SECURITY = "security"
    OTHER = "other"

class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CaseStatus(str, Enum):
    SUBMITTED = "submitted"
    HELD_FOR_REVIEW = "held_for_review" # Duplicate candidate or ambiguous
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    REJECTED = "rejected"

class ReviewStatus(str, Enum):
    NOT_REQUIRED = "not_required"
    PENDING_HUMAN_REVIEW = "pending_human_review"
    CONFIRMED_DUPLICATE = "confirmed_duplicate"
    REJECTED_DUPLICATE = "rejected_duplicate"

class ProblemImage(BaseModel):
    """Cloud-hosted evidence plus the OpenCV features used for matching."""
    id: str
    public_id: str
    secure_url: str
    thumbnail_url: str
    original_filename: str
    content_type: str
    byte_size: int
    width: int
    height: int
    perceptual_hash: str
    blur_variance: float
    quality_warning: Optional[str] = None
    uploaded_at: str
    visual_analysis: Optional[Dict[str, Any]] = None

# Authentication & Session Schemas
class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)

class UserSessionInfo(BaseModel):
    username: str
    role: str
    display_name: str

class LoginResponse(BaseModel):
    user: UserSessionInfo
    demo_mode: bool = True
    message: str
    token: Optional[str] = None

class AuthStatusResponse(BaseModel):
    authenticated: bool
    user: Optional[UserSessionInfo] = None
    demo_mode: bool = True

class NotionStatusResponse(BaseModel):
    configured: bool
    has_api_key: Optional[bool] = None
    parent_page_id: Optional[str] = None
    database_id: Optional[str] = None
    documentation_page_id: Optional[str] = None
    last_synced_at: Optional[str] = None
    missing_configuration: Optional[List[str]] = None

# Student complaint submission
class ComplaintCreate(BaseModel):
    raw_text: str = Field(..., min_length=5, description="Unstructured complaint text from student/staff")
    student_name: Optional[str] = "Anonymous Student"
    student_email: Optional[str] = "student@campus.edu"
    reported_block: Optional[str] = None
    reported_floor: Optional[str] = None
    photo_url: Optional[str] = None
    affected_people: Optional[int] = Field(default=None, ge=0, le=100000)

# Structured Gemma Extraction Output
class GemmaExtractionResult(BaseModel):
    issue_type: IssueCategory
    confidence: float = Field(..., ge=0.0, le=1.0)
    building_block: str
    floor_or_room: Optional[str] = None
    specific_location_hint: str
    clean_summary: str
    detected_urgency: UrgencyLevel
    estimated_priority_score: int = Field(..., ge=1, le=10)
    raw_entities: Dict[str, Any] = Field(default_factory=dict)

# Duplicate Evidence
class DuplicateEvidence(BaseModel):
    matched_case_id: str
    matched_case_title: str
    matched_created_at: str
    semantic_similarity: float
    location_match_score: float
    time_window_score: float
    overall_hybrid_score: float
    is_duplicate_candidate: bool
    reason: str
    visual_similarity: Optional[float] = None

# n8n Dispatch & Routing Event
class DispatchEvent(BaseModel):
    event_id: str
    timestamp: str
    idempotency_key: str
    action_taken: str # e.g., "routed_to_plumbing", "held_for_review", "flagged_urgent"
    assigned_team: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    workflow_branch: str # "duplicate_hold", "direct_assignment", "escalation"
    status_code: int = 200
    details: Dict[str, Any] = Field(default_factory=dict)

# Full Case Representation
class CaseRecord(BaseModel):
    id: str
    case_number: str
    created_at: str
    raw_complaint: str
    student_name: str
    student_email: str
    
    # Extraction
    extraction: GemmaExtractionResult
    
    # Duplicate Analysis
    duplicate_candidates: List[DuplicateEvidence] = Field(default_factory=list)
    is_held_as_duplicate: bool = False
    parent_case_id: Optional[str] = None
    suspected_parent_case_id: Optional[str] = None
    review_status: ReviewStatus = ReviewStatus.NOT_REQUIRED

    # Evidence and prioritisation are stored with the case so dashboard values
    # remain authoritative even when a client is refreshed.
    images: List[ProblemImage] = Field(default_factory=list)
    affected_people: Optional[int] = None
    corroborating_report_count: int = Field(default=1, ge=1)
    priority_score: int = Field(default=5, ge=1, le=10)
    priority_level: UrgencyLevel = UrgencyLevel.MEDIUM
    priority_reasons: List[str] = Field(default_factory=list)
    last_updated_at: Optional[str] = None
    
    # Workflow & Audit
    status: CaseStatus
    assigned_team: Optional[str] = None
    history: List[Dict[str, Any]] = Field(default_factory=list)
    n8n_dispatch: Optional[DispatchEvent] = None
    human_review_notes: Optional[str] = None

# Human Review Decision
class CaseDecisionRequest(BaseModel):
    decision: str # "approve", "reject", "merge_duplicate", "reassign"
    reviewer_notes: Optional[str] = "Approved by facility administrator"
    target_team: Optional[str] = None
    parent_case_id: Optional[str] = None

class CaseStatusUpdate(BaseModel):
    status: CaseStatus
    note: Optional[str] = Field(default=None, max_length=500)

class NotionSyncResult(BaseModel):
    status: str
    page_id: Optional[str] = None
    message: str
    synced_at: str

# Evaluation Metric Data
class EvaluationMetrics(BaseModel):
    total_benchmark_cases: int
    category_macro_f1: float
    precision_heldout: float
    recall_heldout: float
    f1_heldout: float
    n8n_workflow_success_rate: float
    ablation_comparison: Dict[str, Dict[str, float]]
    confusion_matrix: Dict[str, Dict[str, int]]
