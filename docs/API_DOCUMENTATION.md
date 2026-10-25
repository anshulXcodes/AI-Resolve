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

---

## Image Evidence & Priority API Extension

Existing JSON clients may keep using `POST /complaints` without images. The same endpoint also accepts `multipart/form-data` with regular complaint fields plus one or more `images` fields.

### Submit a report with images

- **POST** `/complaints`
- **Content-Type**: `multipart/form-data`
- **Fields**: `raw_text`, `student_name`, `student_email`, `reported_block`, `reported_floor`, optional `affected_people`, and one or more `images` files.
- **Limits**: Actual JPEG, PNG, or WEBP files only; four images and 8 MB per image by default. The server validates content signatures and OpenCV decoding instead of trusting the filename or MIME type.
- **Storage**: Cloudinary must be configured. Failure returns `503`; the service does not return made-up image URLs and rolls back any partial upload.

```bash
curl -X POST http://127.0.0.1:8000/api/v1/complaints \
  -F "raw_text=Overflowing dustbin outside Block A Room 204" \
  -F "reported_block=Block A" \
  -F "affected_people=60" \
  -F "images=@evidence-1.jpg" \
  -F "images=@evidence-2.webp"
```

`CaseRecord` responses now include Cloudinary IDs and optimized thumbnail URLs in `images`, plus `priority_score`, `priority_level`, `priority_reasons`, and `corroborating_report_count`.

### Attach evidence

- **POST** `/complaints/{case_id}/images`
- **Content-Type**: `multipart/form-data`
- **Fields**: one or more `images` fields.
- **Behavior**: Adds evidence (within the configured per-case limit), recomputes visual duplicate signals, and writes an audit event.
- **DELETE** `/complaints/{case_id}/images/{image_id}` removes a Cloudinary object before removing its evidence record. When `ADMIN_API_TOKEN` is configured, this requires `X-Admin-Token`.

### Priority and duplicate views

- **GET** `/cases?priority=critical&location=library&sort=priority`
- Supported filters: `priority` (`critical`, `high`, `medium`, `low`), `location`, and `sort` (`priority`, `most_reported`, `recent`). The backend supplies the authoritative priority values.
- **GET** `/cases/{case_id}/duplicates` returns candidate records with optional `visual_similarity`, review status, suspected parent, and confirmed parent.

### Admin mutations and Notion sync

- **PATCH** `/cases/{case_id}/status`
- **POST** `/integrations/notion/sync`
- If `ADMIN_API_TOKEN` is configured, these endpoints and the existing `/cases/{case_id}/decision` endpoint require `X-Admin-Token: <token>`.
- The Notion endpoint requires its configured token plus a shared parent page/database (or known documentation page); it finds/updates **ResolveAI – Project Documentation** rather than creating duplicates.

## Priority Method

1. Start with structured severity (1–10).
2. Critical extraction or explicit safety terms such as spark, exposed wire, fire, flood, or collapse set a score-10 safety floor.
3. Add one, two, or three points at 2+, 5+, or 10+ corroborating reports; add one or two points for impact estimates of 20+ or 100+ people.
4. Clamp to 1–10 and map 1–3/4–6/7–8/9–10 to low/medium/high/critical.

Corroboration is useful evidence but not the only priority factor: one dangerous electrical report remains critical.
