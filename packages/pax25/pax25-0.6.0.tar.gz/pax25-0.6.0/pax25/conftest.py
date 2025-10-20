"""
This file runs before tests are collected in order to set up the repository for tests.
"""

import re
from os import sep
from pathlib import Path

import pytest

# Delete all test output files before beginning so we don't pass a test based on a
# previous run's output.
for path in Path(".").rglob(f"**{sep}tests{sep}output{sep}*.txt"):
    path.unlink()
for path in Path(".").rglob(f"**{sep}tests{sep}output{sep}*.tmp"):
    path.unlink()
for path in Path(".").rglob(f"**{sep}tests{sep}output{sep}*.json"):
    path.unlink()


@pytest.fixture(scope="session")
def process_id(worker_id: str) -> int:  # pragma: no cover
    """
    Derive a process ID from a worker ID.
    """
    if worker_id == "master":
        return 0
    return int(re.sub("[^0-9]", "", worker_id))
