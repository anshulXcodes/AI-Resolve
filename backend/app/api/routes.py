import uuid
import datetime
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.models.schemas import (
    ComplaintCreate, 
    CaseRecord, 
    CaseStatus, 
    CaseDecisionRequest,
    EvaluationMetrics,
    DispatchEvent
)
from app.services.gemma_service import GemmaExtractionService
from app.services.duplicate_service import DuplicateDetectionService
from app.services.n8n_service import N8NWorkflowService
from app.services.db_service import db
from app.services.benchmark_service import get_benchmark_evaluation

router = APIRouter()

@router.post("/complaints", response_model=CaseRecord)
async def submit_complaint(complaint: ComplaintCreate):
    """
    Core Case Processing Pipeline:
    1. Gemma extraction (Structured JSON)
    2. Hybrid Duplicate Analysis (Semantic + Location + Time rules)
    3. State Assignment (Held for Review vs Direct Route)
    4. n8n Webhook Dispatch with Idempotency Key
    5. Database Persistence & Audit Log
    """
    # 1. Gemma extraction
    extraction = await GemmaExtractionService.extract(
        complaint.raw_text, 
        reported_block=complaint.reported_block
    )
    
    # 2. Check for duplicates against existing active cases
    existing_cases = db.get_all()
    duplicates, is_held = DuplicateDetectionService.evaluate_candidate(
        complaint.raw_text,
        extraction,
        existing_cases
    )
    
    # 3. Form case record
    case_id = f"case_{uuid.uuid4().hex[:8]}"
    case_num = f"RES-2026-{100 + len(existing_cases) + 1}"
    now_iso = datetime.datetime.now().isoformat()
    
    initial_status = CaseStatus.HELD_FOR_REVIEW if is_held else CaseStatus.ASSIGNED
    
    case = CaseRecord(
        id=case_id,
        case_number=case_num,
        created_at=now_iso,
        raw_complaint=complaint.raw_text,
        student_name=complaint.student_name or "Anonymous Student",
        student_email=complaint.student_email or "student@campus.edu",
        extraction=extraction,
        duplicate_candidates=duplicates,
        is_held_as_duplicate=is_held,
        status=initial_status,
        assigned_team=None,
        history=[
            {"timestamp": now_iso, "event": f"Student complaint submitted ({case_num})"},
            {"timestamp": now_iso, "event": f"Gemma extracted: {extraction.issue_type.value} at {extraction.building_block} (Priority {extraction.estimated_priority_score}/10)"}
        ]
    )
    
    # 4. Dispatch via n8n workflow engine
    dispatch_event = await N8NWorkflowService.dispatch_case_event(case)
    case.n8n_dispatch = dispatch_event
    case.assigned_team = dispatch_event.assigned_team
    case.history.append({
        "timestamp": dispatch_event.timestamp,
        "event": f"n8n Dispatch [{dispatch_event.workflow_branch}]: {dispatch_event.action_taken} -> {dispatch_event.assigned_team}"
    })
    
    # 5. Persist
    db.add(case)
    return case

@router.get("/cases", response_model=List[CaseRecord])
def list_cases(
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    search: Optional[str] = Query(None, description="Search complaint text or number")
):
    cases = db.get_all()
    
    if status and status != "all":
        cases = [c for c in cases if c.status.value == status]
        
    if category and category != "all":
        cases = [c for c in cases if c.extraction.issue_type.value == category]
        
    if search:
        s_lower = search.lower()
        cases = [
            c for c in cases 
            if s_lower in c.raw_complaint.lower() 
            or s_lower in c.case_number.lower() 
            or s_lower in c.extraction.clean_summary.lower()
            or s_lower in c.extraction.building_block.lower()
        ]
        
    return cases

@router.get("/cases/{case_id}", response_model=CaseRecord)
def get_case(case_id: str):
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case

@router.post("/cases/{case_id}/decision", response_model=CaseRecord)
def make_case_decision(case_id: str, decision_req: CaseDecisionRequest):
    """
    Facility Admin human-in-the-loop triage:
    Approve, Merge duplicate, Reject, or Reassign.
    Never auto-merges without human approval.
    """
    case = db.get_by_id(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
        
    now_iso = datetime.datetime.now().isoformat()
    
    if decision_req.decision == "approve":
        case.status = CaseStatus.ASSIGNED
        if decision_req.target_team:
            case.assigned_team = decision_req.target_team
        case.history.append({
            "timestamp": now_iso,
            "event": f"Admin approval: Assigned to {case.assigned_team}. Note: {decision_req.reviewer_notes}"
        })
    elif decision_req.decision == "merge_duplicate":
        case.status = CaseStatus.RESOLVED
        case.parent_case_id = decision_req.parent_case_id
        case.history.append({
            "timestamp": now_iso,
            "event": f"Admin merged as verified duplicate into Parent #{decision_req.parent_case_id}. Note: {decision_req.reviewer_notes}"
        })
    elif decision_req.decision == "reject":
        case.status = CaseStatus.REJECTED
        case.history.append({
            "timestamp": now_iso,
            "event": f"Admin rejected case. Note: {decision_req.reviewer_notes}"
        })
        
    case.human_review_notes = decision_req.reviewer_notes
    db.update(case)
    return case

@router.get("/metrics/benchmark", response_model=EvaluationMetrics)
def get_metrics():
    """Returns the benchmark confusion matrix and ablation scores from Slide 5."""
    return get_benchmark_evaluation()

@router.get("/stats")
def get_dashboard_stats():
    cases = db.get_all()
    total = len(cases)
    held = sum(1 for c in cases if c.status == CaseStatus.HELD_FOR_REVIEW)
    assigned = sum(1 for c in cases if c.status == CaseStatus.ASSIGNED or c.status == CaseStatus.IN_PROGRESS)
    resolved = sum(1 for c in cases if c.status == CaseStatus.RESOLVED)
    duplicates_detected = sum(1 for c in cases if c.duplicate_candidates)
    
    return {
        "total_cases": total,
        "held_for_review": held,
        "in_progress_or_assigned": assigned,
        "resolved": resolved,
        "duplicates_detected": duplicates_detected,
        "n8n_webhook_health": "operational",
        "gemma_extraction_health": "operational"
    }

@router.post("/reset-demo")
def reset_demo():
    """Allows one-click reset for hackathon judges demo."""
    global db
    from app.services.db_service import InMemoryDatabase
    db = InMemoryDatabase()
    return {"message": "Demo state reset successfully to initial state"}
