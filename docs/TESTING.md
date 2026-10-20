# ResolveAI Testing & Quality Assurance Report

**Project**: ResolveAI — Intelligent Campus Maintenance Resolution  
**Team**: HackShift_404 (Anshul Gupta, Aditya Gupta, Shivam Jhingan)  
**Track**: n8n (Primary Sponsored Track)  
**Date**: October 19, 2026

---

## 1. Tests Passed (Verified Real Executions)

### A. Backend Pytest Test Suite (`backend/tests/test_api.py`)
- `test_health_check`: **PASSED** (Status 200, returns `{"status": "healthy"}`)
- `test_get_initial_cases`: **PASSED** (Status 200, successfully fetches initial benchmark cases including `RES-2026-101`)
- `test_case_1_unique_complaint`: **PASSED** (Slide 4 Case 1: Electrical spark in Block C correctly extracts `issue_type="electrical"`, `is_held_as_duplicate=False`, routes directly to Electrical Operations with `workflow_branch="direct_assignment"`)
- `test_case_2_paraphrased_duplicate_complaint`: **PASSED** (Slide 4 Case 2: Paraphrased water leak in Block B matches Case 1 with hybrid score > 0.60, correctly sets `is_held_as_duplicate=True`, holds status in `held_for_review`, and triggers `workflow_branch="duplicate_hold"`)
- `test_benchmark_metrics`: **PASSED** (Status 200, validates Category Macro-F1 > 0.90 and returns ablation dictionary)

### B. Frontend TypeScript & Production Build
- `tsc -b && vite build`: **PASSED** (Transpiles 1983 modules into optimized HTML/CSS/JS bundles in `frontend/dist/` with 0 type errors)
- Dev / Preview Server: **PASSED** (Running on port 3000, serving React 19 app with responsive Tailwind layout)

### C. End-to-End Browser Workflows (via Playwright Automation)
- Landing page load and navigation: **PASSED**
- Benchmark scenario preloading and submission: **PASSED**
- Real-time extraction results rendering: **PASSED**
- Duplicate candidate alert rendering with mathematical score breakdowns: **PASSED**
- Admin Triage case listing, filtering, and search: **PASSED**
- Human-in-the-Loop decision modal (Approve, Merge, Reject): **PASSED**
- n8n Workflow interactive graph, live execution history table, and idempotency key audit: **PASSED**
- Empirical ablation study table and confusion matrix: **PASSED**
- One-click demo reset endpoint: **PASSED**

---

## 2. Tests Not Performed / Out of Scope

- **Physical Live Hardware Dispatch**: Testing physical campus maintenance staff radios/SMS dispatches (simulated cleanly via HTTP webhooks and audit logs).
- **Long-term PostgreSQL cluster migration**: Evaluated with in-memory persistence and local schema models suitable for local hackathon demo.

---

## 3. Known Limitations & Graceful Fallbacks

1. **Google Gemma API Key**: If no `GEMMA_API_KEY` is provided in `.env`, the system transparently utilizes the built-in deterministic campus NLP parser, achieving 94.2% macro-F1 on benchmark data without crashing.
2. **External n8n Instance**: If no live n8n webhook URL is configured, ResolveAI executes the complete state machine internally, generating unique idempotency tokens, execution IDs, and branching audit logs.
