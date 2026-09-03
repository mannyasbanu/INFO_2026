"""Integration tests for schedule summaries."""

from __future__ import annotations

from pathlib import Path

import pytest

from schedule_service import ScheduleService


def test_summarise_returns_complete_saved_schedule_summary(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))
    service.add_to_schedule("My Schedule", "Display Paper One")
    service.add_to_schedule("My Schedule", "Tracking Paper")
    service.add_to_schedule("My Schedule", "Later Display Paper")

    assert service.summarise("My Schedule") == {
        "paper_count": 3,
        "tracks": {
            "Displays": 2,
            "Tracking": 1,
        },
        "total_minutes": 165,
    }


def test_summarise_raises_value_error_for_missing_schedule(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))

    with pytest.raises(ValueError):
        service.summarise("Missing Schedule")


def test_summarise_counts_multiple_papers_in_one_session_once_for_time(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))
    service.add_to_schedule("My Schedule", "Display Paper One")
    service.add_to_schedule("My Schedule", "Display Paper Two")

    assert service.summarise("My Schedule") == {
        "paper_count": 2,
        "tracks": {
            "Displays": 2,
        },
        "total_minutes": 60,
    }


def test_summarise_counts_overlapping_sessions_in_full(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))
    service.add_to_schedule("My Schedule", "Display Paper One")
    service.add_to_schedule("My Schedule", "Tracking Paper")

    assert service.summarise("My Schedule") == {
        "paper_count": 2,
        "tracks": {
            "Displays": 1,
            "Tracking": 1,
        },
        "total_minutes": 120,
    }


def test_summarise_returns_summary_for_joint_schedule(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))
    service.add_to_schedule("Schedule A", "Display Paper One")
    service.add_to_schedule("Schedule A", "Tracking Paper")
    service.add_to_schedule("Schedule A", "Later Display Paper")
    service.add_to_schedule("Schedule B", "Tracking Paper")
    service.add_to_schedule("Schedule B", "Display Paper Two")
    service.add_to_schedule("Schedule B", "Display Paper One")
    service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert service.summarise("Joint") == {
        "paper_count": 4,
        "tracks": {
            "Displays": 3,
            "Tracking": 1,
        },
        "total_minutes": 165,
    }
