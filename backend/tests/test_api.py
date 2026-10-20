import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_get_initial_cases():
    response = client.get("/api/v1/cases")
    assert response.status_code == 200
    cases = response.json()
    assert len(cases) >= 3
    # Check that seed case RES-2026-101 exists
    numbers = [c["case_number"] for c in cases]
    assert "RES-2026-101" in numbers

def test_case_1_unique_complaint():
    """
    Tests Slide 4 Case 1: Unique complaint routes directly via n8n
    """
    payload = {
        "raw_text": "Severe ceiling fan humming and sparks coming from switchboard in Lab 402, Block C.",
        "student_name": "Test Student",
        "student_email": "test@campus.edu",
        "reported_block": "Block C"
    }
    response = client.post("/api/v1/complaints", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert data["extraction"]["issue_type"] == "electrical"
    assert data["extraction"]["building_block"] == "Block C"
    assert data["is_held_as_duplicate"] is False
    assert data["status"] == "assigned"
    assert "Electrical" in data["assigned_team"]
    assert data["n8n_dispatch"]["workflow_branch"] == "direct_assignment"

def test_case_2_paraphrased_duplicate_complaint():
    """
    Tests Slide 4 Case 2:
    Paraphrased complaint of Case 1: 'Leaking pipe near the stairs in block B'
    Must trigger hybrid duplicate detection and hold for human review.
    """
    payload = {
        "raw_text": "Leaking pipe near the stairs in block B causing water all over the walkway",
        "student_name": "Second Witness",
        "student_email": "witness@campus.edu",
        "reported_block": "Block B"
    }
    response = client.post("/api/v1/complaints", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    # Must flag as duplicate
    assert data["is_held_as_duplicate"] is True
    assert data["status"] == "held_for_review"
    assert len(data["duplicate_candidates"]) > 0
    top_cand = data["duplicate_candidates"][0]
    assert top_cand["overall_hybrid_score"] > 0.60
    assert top_cand["is_duplicate_candidate"] is True
    assert data["n8n_dispatch"]["workflow_branch"] == "duplicate_hold"

def test_benchmark_metrics():
    response = client.get("/api/v1/metrics/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert data["category_macro_f1"] > 0.90
    assert "ResolveAI Hybrid (Embeddings + Rules + Time)" in data["ablation_comparison"]
