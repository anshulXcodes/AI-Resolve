# ResolveAI — Backend API Server

High-performance asynchronous backend engine for **ResolveAI**, powered by **FastAPI**, **Pydantic v2**, and **Scikit-Learn**.

---

## Architectural Highlights

- **Gemma Structured Extraction**: Parses unstructured student complaints into schema-validated JSON containing category, building block, floor/room, location hints, and priority scores (1-10).
- **Hybrid Duplicate Detection**: Evaluates candidates against active tickets using a weighted formula:
  $$\text{Score} = 0.50 \times \text{Semantic} + 0.35 \times \text{Location} + 0.15 \times \text{Temporal Decay}$$
  Cases exceeding threshold (&ge; 0.58) are flagged as duplicates and held for human review.
- **n8n Webhook Integration**: Emits idempotent events (`X-Idempotency-Key: idemp_{case_id}_{category}`) with automated retry logic and execution tracking.
- **Immutable Audit Trail**: Logs every classification, dispatch, and administrative review action with microsecond timestamps.

---

## Quick Start

```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run unit & integration tests
python -m pytest tests

# 3. Start the API server
python -m uvicorn app.main:app --port 8000 --host 127.0.0.1 --reload
```

Interactive API documentation available at `http://127.0.0.1:8000/docs`.
