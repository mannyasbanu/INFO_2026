"""Integration tests for comparing and saving schedules."""

from __future__ import annotations

from pathlib import Path

import pytest

from schedule_service import ScheduleService


def _service_with_source_schedules(
    programme_path: Path,
) -> ScheduleService:
    service = ScheduleService()
    service.load_sessions(str(programme_path))

    for paper_title in (
        "Display Paper One",
        "Tracking Paper",
        "Later Display Paper",
    ):
        service.add_to_schedule("Schedule A", paper_title)

    for paper_title in (
        "Tracking Paper",
        "Display Paper Two",
        "Display Paper One",
    ):
        service.add_to_schedule("Schedule B", paper_title)

    return service


def test_compare_returns_saved_schedule_differences(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)

    assert service.compare("Schedule A", "Schedule B") == {
        "shared": [
            "Display Paper One",
            "Tracking Paper",
        ],
        "only_a": [
            "Later Display Paper",
        ],
        "only_b": [
            "Display Paper Two",
        ],
        "merged": [
            "Display Paper One",
            "Tracking Paper",
            "Later Display Paper",
            "Display Paper Two",
        ],
    }


def test_compare_raises_value_error_for_missing_schedule(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)

    with pytest.raises(ValueError):
        service.compare("Schedule A", "Missing")


def test_save_joint_schedule_creates_retrievable_schedule(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)

    service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert "Joint" in service.list_schedules()
    assert service.list_schedule_papers("Joint") == [
        {
            "title": "Display Paper One",
            "authors": "A. Author",
            "track": "Displays",
            "session": "Display Session",
            "day": "2025-10-09",
            "room": "Room 201",
            "start_time": "10:30",
            "duration_min": 60,
        },
        {
            "title": "Tracking Paper",
            "authors": "C. Author",
            "track": "Tracking",
            "session": "Tracking Session",
            "day": "2025-10-09",
            "room": "Room 202",
            "start_time": "10:30",
            "duration_min": 60,
        },
        {
            "title": "Later Display Paper",
            "authors": "D. Author",
            "track": "Displays",
            "session": "Later Display Session",
            "day": "2025-10-09",
            "room": "Room 203",
            "start_time": "12:00",
            "duration_min": 45,
        },
        {
            "title": "Display Paper Two",
            "authors": "B. Author",
            "track": "Displays",
            "session": "Display Session",
            "day": "2025-10-09",
            "room": "Room 201",
            "start_time": "10:30",
            "duration_min": 60,
        },
    ]


def test_save_joint_schedule_rejects_existing_name_without_overwriting(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)
    service.add_to_schedule("Joint", "Display Paper Two")

    with pytest.raises(ValueError):
        service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert service.list_schedule_papers("Joint") == [
        {
            "title": "Display Paper Two",
            "authors": "B. Author",
            "track": "Displays",
            "session": "Display Session",
            "day": "2025-10-09",
            "room": "Room 201",
            "start_time": "10:30",
            "duration_min": 60,
        }
    ]


def test_save_joint_schedule_rejects_missing_source_without_creating_target(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)

    with pytest.raises(ValueError):
        service.save_joint_schedule("Joint", "Schedule A", "Missing")

    assert "Joint" not in service.list_schedules()


@pytest.mark.parametrize("new_name", ["", "   "])
def test_save_joint_schedule_rejects_blank_name_without_creating_target(
    schedule_programme_path: Path,
    new_name: str,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)
    source_names = service.list_schedules()

    with pytest.raises(ValueError):
        service.save_joint_schedule(new_name, "Schedule A", "Schedule B")

    assert service.list_schedules() == source_names


def test_saved_joint_schedule_can_be_compared_again(
    schedule_programme_path: Path,
) -> None:
    service = _service_with_source_schedules(schedule_programme_path)
    service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert service.compare("Joint", "Schedule A") == {
        "shared": [
            "Display Paper One",
            "Tracking Paper",
            "Later Display Paper",
        ],
        "only_a": [
            "Display Paper Two",
        ],
        "only_b": [],
        "merged": [
            "Display Paper One",
            "Tracking Paper",
            "Later Display Paper",
            "Display Paper Two",
        ],
    }
