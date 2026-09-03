"""Shared fixtures for schedule-service integration tests."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest


_PROGRAMME_COLUMNS = [
    "day",
    "session",
    "title",
    "authors",
    "track",
    "room",
    "start_time",
    "duration_min",
]

_PROGRAMME_ROWS = [
    {
        "day": "2025-10-09",
        "session": "Display Session",
        "title": "Display Paper One",
        "authors": "A. Author",
        "track": "Displays",
        "room": "Room 201",
        "start_time": "10:30",
        "duration_min": "60",
    },
    {
        "day": "2025-10-09",
        "session": "Display Session",
        "title": "Display Paper Two",
        "authors": "B. Author",
        "track": "Displays",
        "room": "Room 201",
        "start_time": "10:30",
        "duration_min": "60",
    },
    {
        "day": "2025-10-09",
        "session": "Tracking Session",
        "title": "Tracking Paper",
        "authors": "C. Author",
        "track": "Tracking",
        "room": "Room 202",
        "start_time": "10:30",
        "duration_min": "60",
    },
    {
        "day": "2025-10-09",
        "session": "Later Display Session",
        "title": "Later Display Paper",
        "authors": "D. Author",
        "track": "Displays",
        "room": "Room 203",
        "start_time": "12:00",
        "duration_min": "45",
    },
]


@pytest.fixture
def schedule_programme_path(tmp_path: Path) -> Path:
    """Write the compact programme shared by schedule integration tests."""
    path = tmp_path / "programme.csv"
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=_PROGRAMME_COLUMNS)
        writer.writeheader()
        writer.writerows(_PROGRAMME_ROWS)
    return path
