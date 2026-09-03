"""Tests for complete conference-planning workflows."""

from __future__ import annotations

from pathlib import Path

from schedule_service import ScheduleService


EXPECTED_COMPARISON: dict[str, list[str]] = {
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

EXPECTED_JOINT_SUMMARY: dict[str, object] = {
    "paper_count": 4,
    "tracks": {
        "Displays": 3,
        "Tracking": 1,
    },
    "total_minutes": 165,
}


def build_source_schedules(service: ScheduleService) -> None:
    service.add_to_schedule("Schedule A", "Display Paper One")
    service.add_to_schedule("Schedule A", "Tracking Paper")
    service.add_to_schedule("Schedule A", "Later Display Paper")
    service.add_to_schedule("Schedule B", "Tracking Paper")
    service.add_to_schedule("Schedule B", "Display Paper Two")
    service.add_to_schedule("Schedule B", "Display Paper One")


def schedule_titles(
    service: ScheduleService,
    schedule_name: str,
) -> list[str]:
    return [
        paper["title"]
        for paper in service.list_schedule_papers(schedule_name)
    ]


def test_complete_flow_builds_compares_saves_and_summarises_joint_schedule(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    assert service.load_sessions(str(schedule_programme_path)) == 4
    build_source_schedules(service)

    assert service.compare("Schedule A", "Schedule B") == EXPECTED_COMPARISON

    service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert schedule_titles(service, "Joint") == EXPECTED_COMPARISON["merged"]
    assert service.summarise("Joint") == EXPECTED_JOINT_SUMMARY


def test_compare_save_and_summary_use_internal_storage_after_csv_removal(
    schedule_programme_path: Path,
) -> None:
    service = ScheduleService()
    service.load_sessions(str(schedule_programme_path))
    build_source_schedules(service)

    # Removing the source proves later operations use the imported catalogue.
    schedule_programme_path.unlink()

    assert service.compare("Schedule A", "Schedule B") == EXPECTED_COMPARISON

    service.save_joint_schedule("Joint", "Schedule A", "Schedule B")

    assert schedule_titles(service, "Joint") == EXPECTED_COMPARISON["merged"]
    assert service.summarise("Joint") == EXPECTED_JOINT_SUMMARY
