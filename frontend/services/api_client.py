"""API Client for ResolveAI FastAPI Backend.

Connects the Streamlit UI to the existing backend endpoints with session handling,
robust timeouts, and structured error reporting.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple
import requests


def get_backend_url() -> str:
    url = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")
    if not url.endswith("/api/v1"):
        url = f"{url}/api/v1"
    return url


class ResolveAIClient:
    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or get_backend_url()).rstrip("/")
        self.session = requests.Session()
        self.timeout = 15

    def _headers(self, token: Optional[str] = None) -> Dict[str, str]:
        headers: Dict[str, str] = {}
        if token:
            headers["X-Session-Token"] = token
            headers["Cookie"] = f"resolveai_session={token}"
        return headers

    def _handle_response(self, response: requests.Response) -> Tuple[bool, Any]:
        try:
            data = response.json()
        except Exception:
            data = {"detail": response.text or f"HTTP {response.status_code}"}

        if response.status_code in {200, 201}:
            return True, data
        err_msg = data.get("detail", f"Request failed with status {response.status_code}")
        if isinstance(err_msg, list):
            err_msg = "; ".join(item.get("msg", str(item)) for item in err_msg)
        return False, str(err_msg)

    # -------------------------------------------------------------------------
    # Public & Health Endpoints
    # -------------------------------------------------------------------------
    def get_stats(self) -> Tuple[bool, Any]:
        try:
            res = self.session.get(f"{self.base_url}/stats", timeout=self.timeout)
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Could not connect to backend at {self.base_url}: {exc}"

    def track_case(self, identifier: str) -> Tuple[bool, Any]:
        try:
            res = self.session.get(f"{self.base_url}/cases/track/{identifier.strip()}", timeout=self.timeout)
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Tracking failed: {exc}"

    def get_case(self, case_id: str) -> Tuple[bool, Any]:
        try:
            res = self.session.get(f"{self.base_url}/cases/{case_id.strip()}", timeout=self.timeout)
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Lookup failed: {exc}"

    def _parse_affected_people(self, val: Any) -> Optional[int]:
        if val is None or val == "":
            return None
        if isinstance(val, int):
            return val
        s = str(val).lower()
        if "1-5" in s or "few" in s:
            return 3
        if "5-20" in s or "moderate" in s:
            return 12
        if "20-100" in s or "high" in s:
            return 50
        if ">100" in s or "entire" in s:
            return 150
        import re
        match = re.search(r"\d+", s)
        return int(match.group()) if match else None

    def submit_complaint(
        self,
        raw_text: str,
        student_name: Optional[str] = None,
        student_email: Optional[str] = None,
        reported_block: Optional[str] = None,
        reported_floor: Optional[str] = None,
        affected_people: Optional[Any] = None,
        files: Optional[List[Tuple[str, bytes, str]]] = None,
    ) -> Tuple[bool, Any]:
        """Submit a complaint with optional multi-file image evidence via OpenCV & Cloudinary."""
        try:
            affected_int = self._parse_affected_people(affected_people)
            if files:
                form_data = {
                    "raw_text": raw_text,
                    "student_name": student_name or "",
                    "student_email": student_email or "",
                    "reported_block": reported_block or "",
                    "reported_floor": reported_floor or "",
                }
                if affected_int is not None:
                    form_data["affected_people"] = str(affected_int)
                upload_files = []
                for fname, fbytes, ctype in files:
                    upload_files.append(("images", (fname, fbytes, ctype)))
                res = self.session.post(
                    f"{self.base_url}/complaints",
                    data=form_data,
                    files=upload_files,
                    timeout=30,
                )
            else:
                json_payload: Dict[str, Any] = {
                    "raw_text": raw_text,
                    "student_name": student_name or "Anonymous Student",
                    "student_email": student_email or "student@campus.edu",
                    "reported_block": reported_block or "Unspecified Block",
                    "reported_floor": reported_floor or "",
                }
                if affected_int is not None:
                    json_payload["affected_people"] = affected_int
                res = self.session.post(
                    f"{self.base_url}/complaints",
                    json=json_payload,
                    timeout=25,
                )
            return self._handle_response(res)
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Submission request failed: {exc}"

    # -------------------------------------------------------------------------
    # Authentication Endpoints
    # -------------------------------------------------------------------------
    def login(self, username: str, password: str) -> Tuple[bool, Any]:
        try:
            res = self.session.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password},
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Login request failed: {exc}"

    def logout(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.post(
                f"{self.base_url}/auth/logout",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Logout request failed: {exc}"

    def get_me(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/auth/me",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Session check failed: {exc}"

    # -------------------------------------------------------------------------
    # Admin Portal Endpoints
    # -------------------------------------------------------------------------
    def list_cases(
        self,
        token: Optional[str] = None,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        location: Optional[str] = None,
        search: Optional[str] = None,
        sort: str = "priority",
    ) -> Tuple[bool, Any]:
        params: Dict[str, str] = {"sort": sort}
        if status and status != "all":
            params["status"] = status
        if category and category != "all":
            params["category"] = category
        if priority and priority != "all":
            params["priority"] = priority
        if location:
            params["location"] = location
        if search:
            params["search"] = search
        try:
            res = self.session.get(
                f"{self.base_url}/cases",
                headers=self._headers(token),
                params=params,
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to fetch cases: {exc}"

    def get_case_duplicates(self, case_id: str, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/cases/{case_id}/duplicates",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to fetch duplicates: {exc}"

    def make_case_decision(
        self,
        case_id: str,
        decision: str,
        reviewer_notes: str,
        token: Optional[str] = None,
        target_team: Optional[str] = None,
        parent_case_id: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        payload: Dict[str, Any] = {
            "decision": decision,
            "reviewer_notes": reviewer_notes,
        }
        if target_team:
            payload["target_team"] = target_team
        if parent_case_id:
            payload["parent_case_id"] = parent_case_id
        try:
            res = self.session.post(
                f"{self.base_url}/cases/{case_id}/decision",
                headers=self._headers(token),
                json=payload,
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to record decision: {exc}"

    def update_case_status(
        self,
        case_id: str,
        status: str,
        note: Optional[str] = None,
        token: Optional[str] = None,
    ) -> Tuple[bool, Any]:
        payload = {"status": status, "note": note or ""}
        try:
            res = self.session.patch(
                f"{self.base_url}/cases/{case_id}/status",
                headers=self._headers(token),
                json=payload,
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to update status: {exc}"

    def delete_case_image(self, case_id: str, image_id: str, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.delete(
                f"{self.base_url}/complaints/{case_id}/images/{image_id}",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to delete image: {exc}"

    # -------------------------------------------------------------------------
    # Testing Portal Endpoints
    # -------------------------------------------------------------------------
    def get_testing_cases(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/testing/cases",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to fetch testing cases: {exc}"

    def get_benchmark_metrics(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/metrics/benchmark",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to fetch benchmark metrics: {exc}"

    def get_cloudinary_status(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/integrations/cloudinary/status",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to get Cloudinary status: {exc}"

    def get_notion_status(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/integrations/notion/status",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to get Notion status: {exc}"

    def verify_integrations(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.get(
                f"{self.base_url}/integrations/verify",
                headers=self._headers(token),
                timeout=25,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to verify integrations: {exc}"

    def sync_notion(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.post(
                f"{self.base_url}/integrations/notion/sync",
                headers=self._headers(token),
                timeout=30,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Notion synchronization request failed: {exc}"

    def reset_demo(self, token: Optional[str] = None) -> Tuple[bool, Any]:
        try:
            res = self.session.post(
                f"{self.base_url}/reset-demo",
                headers=self._headers(token),
                timeout=self.timeout,
            )
            return self._handle_response(res)
        except Exception as exc:
            return False, f"Failed to reset demo: {exc}"
