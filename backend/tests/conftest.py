"""Pytest configuration and global test environment setup.

Strictly enforces Rule 2 & 3: Environment-variable enforced model names and zero secrets.
Sets up mock environment variables for test suites without hardcoded credentials.
"""

from __future__ import annotations

import os
import pytest


@pytest.fixture(autouse=True)
def configure_test_environment(monkeypatch: pytest.MonkeyPatch):
    """Ensure standard test environment variables are set for all tests."""
    monkeypatch.setenv("TESTING", "true")
    monkeypatch.setenv("GEMINI_MODEL", "mock-gemini-model")
    monkeypatch.setenv("GEMINI_MODEL_ALT", "mock-gemini-alt-model")
    monkeypatch.setenv("GEMINI_EMBED_MODEL", "mock-embed-model")
