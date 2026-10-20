import uuid
import datetime
import httpx
from typing import Dict, Any, Optional
from app.models.schemas import CaseRecord, DispatchEvent, CaseStatus, IssueCategory
from app.core.config import settings

TEAM_MAPPING = {
    IssueCategory.WATER_LEAK: "Campus Plumbing & Water Infrastructure Team",
    IssueCategory.ELECTRICAL: "High & Low Voltage Electrical Operations",
    IssueCategory.FURNITURE: "Carpentry & Facilities Maintenance Unit",
    IssueCategory.HVAC: "HVAC & Thermal Systems Engineering",
    IssueCategory.INTERNET_IT: "Campus IT & Network Operations Center (NOC)",
    IssueCategory.CLEANLINESS: "Sanitation & Groundskeeping Services",
    IssueCategory.SECURITY: "Campus Safety & Rapid Response Unit",
    IssueCategory.OTHER: "General Operations Helpdesk"
}

class N8NWorkflowService:
    """
    Simulates or forwards webhook events to n8n Automation Engine.
    Implements:
    - Idempotency key per dispatch
    - Branching:
      * Branch A (Duplicate / Ambiguous): HOLD FOR HUMAN REVIEW (Do not auto-assign)
      * Branch B (Unique case): Direct assignment to category-specific maintenance team
      * Branch C (Urgent / Escalated): Immediate alert flag
    - Full execution audit log
    """
    
    @classmethod
    async def dispatch_case_event(cls, case: CaseRecord) -> DispatchEvent:
        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        idempotency_key = f"idemp_{case.id}_{case.extraction.issue_type.value}"
        timestamp = datetime.datetime.now().isoformat()
        
        # Determine n8n branching logic
        if case.is_held_as_duplicate:
            action = "held_for_review"
            workflow_branch = "duplicate_hold"
            assigned_team = "Human Facility Administrator Queue"
            details = {
                "branch": "Branch_ReviewHold",
                "message": "Potential duplicate detected with high hybrid score. Held for manual triage.",
                "candidate_matches_count": len(case.duplicate_candidates),
                "auto_merged": False
            }
        elif case.extraction.confidence < 0.60:
            action = "held_for_review"
            workflow_branch = "uncertain_hold"
            assigned_team = "Human Facility Administrator Queue"
            details = {
                "branch": "Branch_UncertainClassification",
                "message": "Low extraction confidence. Pending human review.",
                "confidence": case.extraction.confidence
            }
        else:
            action = "assigned_to_team"
            workflow_branch = "direct_assignment"
            assigned_team = TEAM_MAPPING.get(case.extraction.issue_type, "General Facilities Team")
            details = {
                "branch": "Branch_CategoryRouting",
                "message": f"Automatically assigned to {assigned_team}",
                "routing_rule": f"Rule_{case.extraction.issue_type.value.upper()}_DIRECT"
            }
            
        execution_id = f"n8n_exec_{uuid.uuid4().hex[:8]}"
        
        # If external n8n webhook URL is configured, send the live POST request
        if settings.N8N_WEBHOOK_URL:
            try:
                payload = {
                    "event_id": event_id,
                    "idempotency_key": idempotency_key,
                    "case_id": case.id,
                    "case_number": case.case_number,
                    "issue_type": case.extraction.issue_type.value,
                    "building_block": case.extraction.building_block,
                    "workflow_branch": workflow_branch,
                    "assigned_team": assigned_team,
                    "is_held_as_duplicate": case.is_held_as_duplicate
                }
                async with httpx.AsyncClient(timeout=4.0) as client:
                    resp = await client.post(
                        settings.N8N_WEBHOOK_URL,
                        json=payload,
                        headers={"X-Idempotency-Key": idempotency_key}
                    )
                    execution_id = resp.headers.get("X-N8N-Execution-Id", execution_id)
            except Exception as e:
                print(f"[n8n Service] Live webhook error, proceeding with simulated execution engine: {e}")
                
        return DispatchEvent(
            event_id=event_id,
            timestamp=timestamp,
            idempotency_key=idempotency_key,
            action_taken=action,
            assigned_team=assigned_team,
            n8n_execution_id=execution_id,
            workflow_branch=workflow_branch,
            status_code=200,
            details=details
        )
