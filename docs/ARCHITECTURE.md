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
