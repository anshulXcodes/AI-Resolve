# ResolveAI — Frontend Web Application

Modern, responsive SaaS-style web application for **ResolveAI: Intelligent Campus Maintenance Resolution**, built with **React 19**, **Vite**, **TypeScript**, and **Tailwind CSS**.

---

## Features

- **Interactive Presentation Landing Page**: Showcases problem statements, structured solution benefits, 4-step workflow lifecycle, and technical USPs.
- **Smart Issue Submission Portal**: Free-form natural language input with one-click benchmark preloads (Unique Case 1, Paraphrased Duplicate Case 2, Urgent Electrical Hazard, Broken Furniture).
- **Admin Triage & Audit Console**: Complete ticket queue with category/status filters, real-time search, and detailed audit modals.
- **Human-in-the-Loop Review**: Allows administrators to Approve & Dispatch, Merge as Verified Duplicate, or Reject with full reason tracking.
- **n8n Workflow Execution Monitor**: Visual topological graph of n8n routing rules, idempotency checks, and live execution history table.
- **Empirical Benchmark & Ablation Dashboard**: Side-by-side performance comparison of Keyword matching vs Pure Embeddings vs ResolveAI Hybrid strategy.

---

## Quick Start

```powershell
# 1. Install dependencies
npm install

# 2. Build for production
npm run build

# 3. Run preview server
npm run preview -- --port 3000 --host 127.0.0.1
```

Access the UI at `http://127.0.0.1:3000`.
