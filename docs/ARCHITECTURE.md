# ResolveAI Architecture & System Flow

ResolveAI is an intelligent campus maintenance resolution platform engineered for the **n8n Workflow Automation Track** at Reforged '26 by team **HackShift_404**.

## High-Level Topology

```
┌───────────────────────────────────────────────────────────────┐
│                    Student & Facility UI                      │
│            (React 19 + TypeScript + Tailwind CSS)             │
└───────────────────────────────┬───────────────────────────────┘
                                │ REST / JSON
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                  FastAPI Application Server                   │
│   • Pydantic Schema Enforcement                               │
│   • Idempotency Token Generation                              │
│   • In-Memory / Relational Case Storage                       │
└───────────────┬───────────────────────────────┬───────────────┘
                │                               │
                ▼                               ▼
┌───────────────────────────────┐ ┌─────────────────────────────┐
│  Gemma Extraction Pipeline    │ │  Hybrid Duplicate Engine    │
│  • Category Classification    │ │  • 50% Semantic Cosine      │
│  • Building / Room Detection  │ │  • 35% Physical Proximity   │
│  • Urgency & Priority Score   │ │  • 15% Temporal Decay       │
└───────────────┬───────────────┘ └─────────────┬───────────────┘
                │                               │
                └───────────────┬───────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────┐
│              n8n Core Orchestration Engine                    │
│   POST /case-events (Header: X-Idempotency-Key)               │
│                                                               │
│   ┌───────────────────────────────────────────────────────┐   │
│   │ IF Check: Duplicate Candidate or Ambiguous?           │   │
│   └───────────────┬───────────────────────┬───────────────┘   │
│                   │ YES                   │ NO                │
│                   ▼                       ▼                   │
│      [HOLD FOR HUMAN REVIEW]     [DIRECT TEAM ASSIGNMENT]     │
│       • Evidence Breakdown        • Plumbing & Water Infra    │
│       • Zero Silent Merge         • High/Low Voltage Elect    │
│       • Facility Admin Triage     • HVAC Systems Team         │
│                                   • Carpentry & Grounds       │
└───────────────────────────────┬───────────────────────────────┘
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                 Audit Trail & Execution Store                 │
│   • Immutable state transition events                         │
│   • n8n execution IDs & webhook delivery receipts             │
└───────────────────────────────────────────────────────────────┘
```

## Architectural Safeguards

1. **Schema Validation**: Every response from the Gemma NLP model is parsed against strict Pydantic models before entering the routing queue.
2. **Idempotent Webhooks**: Outbound events to n8n carry unique idempotency tokens (`idemp_{case_id}_{category}`) to eliminate duplicate alerts during network retries.
3. **Zero Silent Merging**: Suspected duplicates (&ge; 0.58 hybrid score) are held in an administrative review queue with cosine similarity, location match, and time-decay scores. No case is merged without human sign-off.
4. **Redacted Logs**: Telemetry and logs exclude student personal identifying information (PII) and secret credentials.
5. **Evidence Boundary**: The React app only previews files locally. FastAPI validates actual JPEG/PNG/WEBP signatures and decodes them with OpenCV before Cloudinary receives the original evidence. API secrets never enter the browser bundle.
6. **Multimodal, Human-Governed Matching**: OpenCV dHash is compared only alongside category or location evidence and combined with the existing text/location/time score. It can add a hold-for-review signal but cannot silently merge or delete an original report.
7. **Explainable Priority**: `priority_score`, `priority_level`, `priority_reasons`, and `corroborating_report_count` are persisted on each case. Safety terms and critical extraction apply a score-10 floor; corroboration and affected people add transparent boosts.
8. **External Failure Consistency**: Cloudinary uploads roll back objects already written if a later upload fails. A report is not persisted until all evidence is available. Notion synchronization is opt-in, retry-safe, and updates a known page rather than creating a page on every run.

## Image-Evidence Extension

```text
Browser file selection / drop
        │  (client type + 8 MB check, local preview)
        ▼
POST /api/v1/complaints (multipart)
        │
        ├── OpenCV: verify signature → decode → dimension guard → resize analysis copy
        │           → blur variance → 64-bit dHash
        ├── Cloudinary: original evidence → secure URL + transformed thumbnail
        ├── Duplicate engine: text + location + time [+ visual similarity]
        └── Priority service: safety severity + corroboration + people affected
                    │
                    └── n8n direct route OR human-review hold (never auto-merge)
```
