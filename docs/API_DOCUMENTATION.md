# ResolveAI API Documentation

Base URL: `http://127.0.0.1:8000/api/v1`

## Endpoints Summary

### 1. Submit Maintenance Complaint
- **POST** `/complaints`
- **Description**: Ingests student complaint, performs Gemma structured extraction, computes hybrid duplicate scores, and triggers the n8n dispatch event.
- **Request Body**:
```json
{
  "raw_text": "Water across B-block stairway, puddles forming near the second landing",
  "student_name": "Aarav Sharma",
  "student_email": "aarav.s@campus.edu",
  "reported_block": "Block B",
  "reported_floor": "2nd Floor"
}
```
- **Response**: Full `CaseRecord` object containing extraction, duplicate candidates, status, and n8n dispatch details.

---

### 2. List Cases
- **GET** `/cases`
- **Query Parameters**:
  - `status`: Filter by status (`all`, `held_for_review`, `assigned`, `in_progress`, `resolved`, `rejected`)
  - `category`: Filter by category (`water_leak`, `electrical`, `furniture`, `hvac`, etc.)
  - `search`: Keyword search across complaint text, room hints, and ticket IDs.

---

### 3. Get Single Case Detail
- **GET** `/cases/{case_id}`
- **Response**: Complete case details including audit trail history and n8n execution IDs.

---

### 4. Admin Human Review Decision
- **POST** `/cases/{case_id}/decision`
- **Description**: Human-in-the-loop approval or merge for cases held under review.
- **Request Body**:
```json
{
  "decision": "approve" | "merge_duplicate" | "reject",
  "reviewer_notes": "Verified by Facility Head",
  "target_team": "Campus Plumbing & Water Infrastructure Team",
  "parent_case_id": "case_b_leak_001"
}
```

---

### 5. Benchmark & Ablation Metrics
- **GET** `/metrics/benchmark`
- **Description**: Returns empirical evaluation metrics: Category Macro-F1 (94.2%), Duplicate Precision (91.6%), Recall (93.8%), n8n Success Rate (99.4%), and ablation comparisons.

---

### 6. Dashboard Stats
- **GET** `/stats`
- **Response**: Counts of total, held, assigned, and resolved tickets, plus service health statuses.

---

### 7. Reset Demo
- **POST** `/reset-demo`
- **Description**: Reinitializes the case store back to the pristine benchmark state for hackathon presentations.
