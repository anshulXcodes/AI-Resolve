# RESOLVEAI — Intelligent Campus Maintenance Resolution

> **Hackathon**: Reforged '26 (BPIT, MLH, Unstop)  
> **Team**: HackShift_404  
> **Members**: Anshul Gupta (Team Leader) • Aditya Gupta • Shivam Jhingan  
> **Primary Track**: n8n Workflow Automation (Sponsored Track)

---

## 1. Project Overview

Free-form maintenance reports filed by campus students frequently generate duplicate tickets, ambiguous categorization, and inconsistent triage, severely slowing down repair velocity and wasting facility resources.

**ResolveAI** transforms unstructured text complaints into organized, schema-validated, auditable work orders. By integrating **Google Gemma** for structured entity extraction, a **Hybrid Duplicate Detection Engine** combining vector semantics with physical building proximity and temporal decay, and **n8n Workflow Automation** for intelligent dispatch, ResolveAI ensures repairs are routed quickly, duplicates are flagged with empirical mathematical evidence, and administrative teams retain full audit oversight.

---

## 2. Key Features

- **Gemma Structured Extraction**: Automatically classifies complaints into 8 categories (Water Leak, Electrical, Furniture, HVAC, IT/Network, Cleanliness, Security, Other) and extracts building blocks, rooms, and urgency priorities (1–10).
- **Hybrid Duplicate Detection**: Uses an empirical formula ($50\%$ Semantic Cosine $+ 35\%$ Location Match $+ 15\%$ Time Proximity) to catch paraphrased complaints (e.g. *"Water on stairs in B-block"* vs *"Leaking pipe near block B walkway"*).
- **Zero Silent Merging**: Suspicious duplicate tickets are automatically held for human review with concrete similarity evidence, eliminating accidental deletion of critical unique issues.
- **n8n Orchestration Core**: Stateful branching via idempotent webhooks (`POST /case-events`) that routes tickets directly to specialized teams or holds them for triage.
- **Human-in-the-Loop Admin Triage**: Facility managers can approve & dispatch, merge duplicates into parent tickets, or reassign with complete audit notes.
- **Empirical Benchmarking Dashboard**: Evaluates models on 120 held-out student complaints, demonstrating a 94.2% Macro-F1 score and a 92.7% duplicate detection F1-score.

---

## 3. Technology Stack

- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons
- **Backend**: FastAPI, Pydantic v2, Scikit-Learn, NumPy, Uvicorn, Python-dotenv
- **Automation / Orchestration**: n8n Webhook Architecture with Idempotency Key protection
- **NLP / ML**: Google Gemma / Gemini API (with deterministic offline campus extraction engine fallback)
- **Testing & Tooling**: Pytest, Playwright Chromium, Python-PPTX

---

## 4. System Architecture

```
[Student / Staff Complaint] ──► [React 19 Frontend]
                                       │
                                       ▼ (REST / JSON)
                                [FastAPI Backend]
                                       │
         ┌─────────────────────────────┴─────────────────────────────┐
         ▼                                                           ▼
[Google Gemma NLP Extraction]                             [Hybrid Duplicate Engine]
(Schema-validated JSON)                                   (Embeddings + Space/Time Rules)
         │                                                           │
         └─────────────────────────────┬─────────────────────────────┘
                                       ▼
                       [n8n Automation Engine / Webhook]
                          (Idempotency Key Guaranteed)
                                       │
                 ┌─────────────────────┴─────────────────────┐
                 │ IF Score >= 0.58                          │ IF Score < 0.58
                 ▼ (Yes)                                     ▼ (No)
        [Hold for Human Review]                     [Direct Team Assignment]
        • Never silently merged                     • Plumbing & Infrastructure
        • Admin Triage Modal                        • Electrical Operations
        • Evidence breakdown                        • HVAC & Carpentry Units
                 │                                           │
                 └─────────────────────┬─────────────────────┘
                                       ▼
                         [Immutable Case Audit Trail]
```

---

## 5. Quick Start Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ (npm installed)

### Backend Startup
```powershell
cd ResolveAI/backend
pip install -r requirements.txt
python -m pytest tests
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1
```
*API docs available at `http://127.0.0.1:8000/docs`.*

### Frontend Startup
```powershell
cd ResolveAI/frontend
npm install
npm run build
npm run preview -- --port 3000 --host 127.0.0.1
```
*Web application available at `http://127.0.0.1:3000`.*

---

## 6. Live Demo Workflow (Hackathon Presentation Guide)

1. **Open Application**: Navigate to `http://127.0.0.1:3000`.
2. **Execute Case 1 (Unique Issue)**: Click **"Test Case 1: Unique Complaint"** &rarr; Submit. Note how Gemma classifies it as `water_leak` at Block B, and n8n assigns it directly to the Plumbing Team.
3. **Execute Case 2 (Paraphrased Duplicate)**: Click **"Test Case 2: Paraphrased Duplicate"** &rarr; Submit. Observe how the Hybrid Duplicate engine identifies a 61.6% match with Case 1, puts the case into `held_for_review`, and displays the exact cosine + location evidence.
4. **Admin Triage & Audit Trail**: Go to **"Admin Triage"** &rarr; Click **"Review"** on the held case &rarr; Select "Merge Duplicate" or "Approve & Dispatch" &rarr; Confirm &rarr; Inspect the audit timeline.
5. **n8n Workflow Graph**: Open **"n8n Workflow"** to see the interactive routing topology, idempotency safeguards, and live execution runs table.
6. **Empirical Benchmarks**: Open **"Benchmark & USP"** to review the ablation comparison (Keyword vs Embeddings vs Hybrid) and confusion matrix.
7. **Reset Demo**: Click the floating **"Reset Demo"** button anytime to reset state for the next judges.

---

## 7. Deliverables & Documentation

- `presentation/Final_Project_Presentation.pptx`: 9-slide presentation deck covering Problem, Solution, 4-Step Pipeline, Architecture, n8n Branching, Empirical Benchmarks, Mentoring Improvements, and Production Readiness.
- `screenshots/`: Real browser captures of all pages (`01_landing_hero.png` through `07_empirical_benchmark.png`).
- `docs/ARCHITECTURE.md`: In-depth architectural blueprint and security safeguards.
- `docs/API_DOCUMENTATION.md`: Complete OpenAPI endpoint schemas and payloads.
- `docs/SETUP_GUIDE.md`: Comprehensive setup and troubleshooting handbook.
- `docs/TESTING.md`: QA test report with passed unit/integration/browser tests.
- `ResolveAI-Complete.zip`: Complete packaged bundle.
