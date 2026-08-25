"""Tests for building and retrieving personal schedules."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from schedule_service import ScheduleService


REQUIRED_COLUMNS = [
    "day",
    "session",
    "title",
    "authors",
    "track",
    "room",
    "start_time",
    "duration_min",
]


def programme_row(
    session: str,
    title: str,
    *,
    authors: str = "A. Author",
    day: str = "2025-10-09",
    track: str = "Displays",
    room: str = "Room 201",
    start_time: str = "10:30",
    duration_min: str = "60",
) -> dict[str, str]:
    return {
        "day": day,
        "session": session,
        "title": title,
        "authors": authors,
        "track": track,
        "room": room,
        "start_time": start_time,
        "duration_min": duration_min,
    }


def write_programme(
    tmp_path: Path,
    rows: list[dict[str, str]],
    *,
    filename: str = "programme.csv",
) -> Path:
    path = tmp_path / filename
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=REQUIRED_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return path


def schedule_titles(service: ScheduleService, schedule_name: str) -> list[str]:
    return [
        paper["title"] for paper in service.list_schedule_papers(schedule_name)
    ]


def test_added_schedule_remains_available_for_later_queries(
    tmp_path: Path,
) -> None:
    path = write_programme(
        tmp_path,
        [programme_row("Display Session", "Paper One")],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    service.add_to_schedule("My Schedule", "Paper One")

    assert service.list_schedules() == ["My Schedule"]
    assert schedule_titles(service, "My Schedule") == ["Paper One"]


def test_list_schedule_papers_returns_complete_paper_details(
    tmp_path: Path,
) -> None:
    path = write_programme(
        tmp_path,
        [
            programme_row(
                "Display Session",
                "Paper One",
                authors="A. Author",
                track="Displays",
                day="2025-10-09",
                room="Room 201",
                start_time="10:30",
                duration_min="60",
            )
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))
    service.add_to_schedule("My Schedule", "Paper One")

    assert service.list_schedule_papers("My Schedule") == [
        {
            "title": "Paper One",
            "authors": "A. Author",
            "track": "Displays",
            "session": "Display Session",
            "day": "2025-10-09",
            "room": "Room 201",
            "start_time": "10:30",
            "duration_min": 60,
        }
    ]


def test_list_schedule_papers_returns_empty_for_unknown_schedule(
    tmp_path: Path,
) -> None:
    path = write_programme(
        tmp_path,
        [programme_row("Display Session", "Paper One")],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_schedule_papers("Unknown Schedule") == []


def test_add_to_schedule_raises_value_error_for_unknown_paper(
    tmp_path: Path,
) -> None:
    path = write_programme(
        tmp_path,
        [programme_row("Display Session", "Paper One")],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    with pytest.raises(ValueError):
        service.add_to_schedule("My Schedule", "Unknown Paper")


def test_multiple_named_schedules_remain_separate(tmp_path: Path) -> None:
    path = write_programme(
        tmp_path,
        [
            programme_row("Session One", "Paper One"),
            programme_row("Session Two", "Paper Two", room="Room 202"),
            programme_row("Session Three", "Paper Three", room="Room 203"),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))
    service.add_to_schedule("First Schedule", "Paper One")
    service.add_to_schedule("Second Schedule", "Paper Two")

    service.add_to_schedule("First Schedule", "Paper Three")

    assert service.list_schedules() == ["First Schedule", "Second Schedule"]
    assert schedule_titles(service, "First Schedule") == [
        "Paper One",
        "Paper Three",
    ]
    assert schedule_titles(service, "Second Schedule") == ["Paper Two"]


def test_overlapping_session_papers_can_share_schedule(tmp_path: Path) -> None:
    path = write_programme(
        tmp_path,
        [
            programme_row(
                "Morning Session",
                "Paper One",
                start_time="09:00",
                duration_min="60",
            ),
            programme_row(
                "Overlapping Session",
                "Paper Two",
                room="Room 202",
                start_time="09:30",
                duration_min="60",
            ),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    # The sessions overlap, but UC2 allows both papers to be selected.
    service.add_to_schedule("My Schedule", "Paper One")
    service.add_to_schedule("My Schedule", "Paper Two")

    assert schedule_titles(service, "My Schedule") == ["Paper One", "Paper Two"]


def test_schedule_operations_do_not_reread_source_csv(tmp_path: Path) -> None:
    path = write_programme(
        tmp_path,
        [programme_row("Display Session", "Paper One")],
    )
    service = ScheduleService()
    service.load_sessions(str(path))
    path.unlink()

    service.add_to_schedule("My Schedule", "Paper One")

    assert service.list_schedule_papers("My Schedule") == [
        {
            "title": "Paper One",
            "authors": "A. Author",
            "track": "Displays",
            "session": "Display Session",
            "day": "2025-10-09",
            "room": "Room 201",
            "start_time": "10:30",
            "duration_min": 60,
        }
    ]
