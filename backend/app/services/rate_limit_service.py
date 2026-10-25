from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from threading import Lock

from app.core.config import settings


class SubmissionRateLimiter:
    """Small in-process guard for the demo deployment; replace with Redis at scale."""

    def __init__(self) -> None:
        self._attempts: dict[str, deque[datetime]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, identity: str) -> bool:
        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(minutes=1)
        with self._lock:
            bucket = self._attempts[identity]
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= settings.SUBMISSION_RATE_LIMIT_PER_MINUTE:
                return False
            bucket.append(now)
            return True

    def reset(self) -> None:
        with self._lock:
            self._attempts.clear()


submission_rate_limiter = SubmissionRateLimiter()
