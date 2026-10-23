"""Rate limiting configuration for MathQuest Georgia API using slowapi."""

from __future__ import annotations

import os
from slowapi import Limiter
from slowapi.util import get_remote_address

# Allow disabling or raising rate limits in testing or CI environments
_is_test_env = (
    os.getenv("TESTING", "").lower() in ("true", "1")
    or "pytest" in os.getenv("_", "")
    or "PYTEST_CURRENT_TEST" in os.environ
)

# In test environments, slowapi is disabled by default to avoid test interference,
# unless explicitly enabled via ENABLE_TEST_RATE_LIMIT=true.
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["120/minute"],
    storage_uri="memory://",
    enabled=not _is_test_env or os.getenv("ENABLE_TEST_RATE_LIMIT", "").lower() == "true",
)
