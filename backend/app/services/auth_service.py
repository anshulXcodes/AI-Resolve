"""Role-Based Demo Authentication & Session Management Service.

Provides server-validated session cookies with HMAC signatures, role isolation
between 'admin' and 'tester', and constant-time credential verification.
Labeled as demo authentication for hackathon evaluation.
"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from fastapi import HTTPException, Request, status

from app.core.config import settings


SESSION_COOKIE_NAME = "resolveai_session"
SESSION_DURATION_SECONDS = 24 * 60 * 60  # 24 hours


@dataclass
class SessionData:
    session_id: str
    username: str
    role: str
    display_name: str
    created_at: float
    expires_at: float


class AuthService:
    _active_sessions: Dict[str, SessionData] = {}

    @classmethod
    def _sign_token(cls, raw_token: str) -> str:
        secret = settings.SESSION_SECRET.encode("utf-8")
        sig = hmac.new(secret, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()
        return f"{raw_token}.{sig}"

    @classmethod
    def _verify_token_signature(cls, signed_token: str) -> Optional[str]:
        if not signed_token or "." not in signed_token:
            return None
        raw_token, provided_sig = signed_token.split(".", 1)
        secret = settings.SESSION_SECRET.encode("utf-8")
        expected_sig = hmac.new(secret, raw_token.encode("utf-8"), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(provided_sig, expected_sig):
            return None
        return raw_token

    @classmethod
    def authenticate(cls, username: str, password: str) -> Optional[Tuple[str, str, str]]:
        """Verify demo credentials against environment variables using constant-time comparison."""
        admin_user_ok = hmac.compare_digest(username.strip(), settings.ADMIN_USERNAME)
        admin_pass_ok = hmac.compare_digest(password, settings.ADMIN_PASSWORD)
        if admin_user_ok and admin_pass_ok:
            return settings.ADMIN_USERNAME, "admin", "Campus Facility Administrator"

        tester_user_ok = hmac.compare_digest(username.strip(), settings.TESTER_USERNAME)
        tester_pass_ok = hmac.compare_digest(password, settings.TESTER_PASSWORD)
        if tester_user_ok and tester_pass_ok:
            return settings.TESTER_USERNAME, "tester", "QA & Reliability Tester"

        return None

    @classmethod
    def create_session(cls, username: str, role: str, display_name: str) -> str:
        raw_token = secrets.token_urlsafe(32)
        signed_token = cls._sign_token(raw_token)
        now = time.time()
        cls._active_sessions[raw_token] = SessionData(
            session_id=raw_token,
            username=username,
            role=role,
            display_name=display_name,
            created_at=now,
            expires_at=now + SESSION_DURATION_SECONDS,
        )
        return signed_token

    @classmethod
    def get_session(cls, signed_token: Optional[str]) -> Optional[SessionData]:
        if not signed_token:
            return None
        raw_token = cls._verify_token_signature(signed_token)
        if not raw_token:
            return None
        session = cls._active_sessions.get(raw_token)
        if not session:
            return None
        if time.time() > session.expires_at:
            cls._active_sessions.pop(raw_token, None)
            return None
        return session

    @classmethod
    def destroy_session(cls, signed_token: Optional[str]) -> bool:
        if not signed_token:
            return False
        raw_token = cls._verify_token_signature(signed_token)
        if not raw_token:
            return False
        return cls._active_sessions.pop(raw_token, None) is not None

    @classmethod
    def extract_token_from_request(cls, request: Request) -> Optional[str]:
        # 1. Check HTTP-only cookie
        cookie_val = request.cookies.get(SESSION_COOKIE_NAME)
        if cookie_val:
            return cookie_val

        # 2. Check X-Session-Token header (useful for API clients & tests)
        header_val = request.headers.get("X-Session-Token")
        if header_val:
            return header_val

        # 3. Check Authorization header (Bearer token)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:].strip()

        return None


def get_current_session(request: Request) -> SessionData:
    token = AuthService.extract_token_from_request(request)
    session = AuthService.get_session(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in with valid demo credentials.",
        )
    return session


def require_admin(request: Request) -> SessionData:
    session = get_current_session(request)
    if session.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Campus Administrator privileges required for this operation.",
        )
    return session


def require_tester(request: Request) -> SessionData:
    session = get_current_session(request)
    if session.role != "tester":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Testing & QA role required for this operation.",
        )
    return session
