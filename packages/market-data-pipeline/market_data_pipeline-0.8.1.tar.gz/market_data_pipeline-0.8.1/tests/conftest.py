# tests/conftest.py
import asyncio
import os
import sys
import pytest

# Ensure src/ is importable when running from repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def event_loop():
    # Windows-safe event loop for asyncio tests
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
