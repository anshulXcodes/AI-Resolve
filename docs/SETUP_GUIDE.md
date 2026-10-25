# ResolveAI Setup & Deployment Guide

This guide provides complete instructions to set up, configure, and execute the ResolveAI application locally or in production.

---

## 1. Prerequisites

- **Python**: Version 3.10+ (Tested on Python 3.13)
- **Node.js**: Version 18+ (Tested on Node.js v24.19 / npm 11.17)
- **Git** (optional)

---

## 2. Repository Structure

```text
ResolveAI/
├── frontend/             # React 19 + TypeScript + Tailwind CSS UI
│   ├── src/
│   │   ├── components/   # Navbar & UI modules
│   │   ├── pages/        # LandingPage, SubmitPage, DashboardPage, WorkflowView, BenchmarkPage
│   │   ├── services/     # Axios API service
│   │   └── types/        # TypeScript interfaces
│   ├── package.json
│   └── vite.config.ts
├── backend/              # FastAPI + Pydantic + Scikit-Learn
│   ├── app/
│   │   ├── api/          # REST route handlers
│   │   ├── core/         # Configuration & thresholds
│   │   ├── models/       # Pydantic schemas
│   │   └── services/     # Gemma extraction, hybrid duplicate, n8n dispatch, DB
│   ├── tests/            # Pytest test suite
│   ├── requirements.txt
│   └── .env.example
├── presentation/         # Final_Project_Presentation.pptx (9 slides)
├── screenshots/          # Real browser captures
└── docs/                 # ARCHITECTURE.md, API_DOCUMENTATION.md, SETUP_GUIDE.md, TESTING.md
```

---

## 3. Backend Setup

1. Open a terminal in `ResolveAI/backend`:
```powershell
cd ResolveAI/backend
```

2. (Optional) Create and activate a Python virtual environment:
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

3. Install dependencies:
```powershell
pip install -r requirements.txt
```

4. Configure environment:
```powershell
Copy-Item .env.example .env
```
*(Optional: Provide a `GEMMA_API_KEY` for live Google Gemini/Gemma models; if left empty, the intelligent local structured extractor runs seamlessly.)*

### Image evidence configuration

Populate these backend-only variables in `.env` to enable image reports:

```env
CLOUDINARY_CLOUD_NAME="your-cloud-name"
CLOUDINARY_API_KEY="your-api-key"
CLOUDINARY_API_SECRET="your-api-secret"
```

Text-only reports remain available without Cloudinary. Image reports return a clear configuration error until all values are present. Never add Cloudinary secrets to `VITE_` variables or frontend files.

### Optional Notion documentation sync

1. Create an internal integration in Notion and set `NOTION_API_KEY`.
2. Share the target parent page or database with the integration.
3. Set `NOTION_PARENT_PAGE_ID` (recommended), `NOTION_DATABASE_ID`, or an existing `NOTION_DOCUMENTATION_PAGE_ID`.
4. In non-demo environments, set `ADMIN_API_TOKEN` and include it in `X-Admin-Token` when calling the sync endpoint.

Missing Notion credentials/permissions result in an error response; the app does not report a false successful synchronization.

5. Run test suite to verify installation:
```powershell
python -m pytest tests
```

6. Start the FastAPI backend server:
```powershell
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1 --reload
```
API Documentation will be live at: `http://127.0.0.1:8000/docs`

---

## 4. Frontend Setup

1. Open a separate terminal in `ResolveAI/frontend`:
```powershell
cd ResolveAI/frontend
```

2. Install npm dependencies:
```powershell
npm install
```

3. Build the frontend for production:
```powershell
npm run build
```

4. Run the frontend preview server:
```powershell
npm run preview -- --port 3000 --host 127.0.0.1
```
Or run dev mode:
```powershell
npm run dev -- --port 3000 --host 127.0.0.1
```

5. Open your browser at:
`http://127.0.0.1:3000`

---

## 5. Live Hackathon Demonstration Steps

1. **Overview**: View the hero problem/solution breakdown and core USPs.
2. **Execute Case 1 (Unique)**: Click **"Test Case 1: Unique Complaint"** &rarr; Submit &rarr; See Gemma parse `water_leak` at Block B, and observe n8n direct assignment to the Plumbing Team.
3. **Execute Case 2 (Paraphrased Duplicate)**: Click **"Test Case 2: Paraphrased Duplicate"** &rarr; Submit &rarr; Observe the **Hybrid Duplicate Engine** detect the correlation (Score > 60%), hold the ticket for human triage, and display the mathematical cosine + location evidence.
4. **Admin Triage & Audit Trail**: Navigate to **"Admin Triage"** &rarr; Click **"Review"** on the held ticket &rarr; Select "Merge Duplicate" or "Approve & Dispatch" &rarr; Confirm &rarr; Inspect the immutable event log.
5. **n8n Workflow Graph**: Navigate to **"n8n Workflow"** &rarr; View the visual execution topology and live execution runs table with idempotency keys.
6. **Empirical Benchmarks**: Navigate to **"Benchmark & USP"** &rarr; Inspect the ablation study table and category confusion matrix.
7. **One-Click Demo Reset**: Click the floating **"Reset Demo"** button anytime to reset tickets to pristine state.

---

## 6. Image Workflow Verification

1. Start the backend with Cloudinary variables configured, then open the Student & Staff Portal.
2. Drag a JPG, PNG, or WEBP image onto **Photo evidence**, confirm its preview, and submit.
3. In **Admin Maintenance Triage**, confirm the thumbnail, priority badge, corroborating count, and (when applicable) visual duplicate signal.
4. Try a text file renamed `.jpg`, an unsupported format, and an oversized file. Each must be rejected by the server.
5. Submit a same-category/location report with similar evidence. It should enter human review; it must never automatically merge.
