"""Tests for comparing saved schedules."""

from __future__ import annotations

import pytest

from student.schedule_comparator import ScheduleComparator


class FakeScheduleAccess:
    """Provide saved paper titles from a small in-memory mapping."""

    def __init__(
        self,
        schedules: dict[str, tuple[str, ...]],
    ) -> None:
        self._schedules = dict(schedules)

    def get_paper_titles(
        self,
        schedule_name: str,
    ) -> tuple[str, ...] | None:
        return self._schedules.get(schedule_name)


def test_compare_returns_ordered_shared_unique_and_merged_papers() -> None:
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": (
                "Paper One",
                "Paper Two",
                "Paper Three",
            ),
            "Schedule B": (
                "Paper Two",
                "Paper Four",
                "Paper One",
            ),
        }
    )
    comparator = ScheduleComparator(schedule_access)

    assert comparator.compare("Schedule A", "Schedule B") == {
        "shared": [
            "Paper One",
            "Paper Two",
        ],
        "only_a": [
            "Paper Three",
        ],
        "only_b": [
            "Paper Four",
        ],
        "merged": [
            "Paper One",
            "Paper Two",
            "Paper Three",
            "Paper Four",
        ],
    }


def test_compare_handles_schedules_with_no_shared_papers() -> None:
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": ("Paper One", "Paper Two"),
            "Schedule B": ("Paper Three", "Paper Four"),
        }
    )
    comparator = ScheduleComparator(schedule_access)

    assert comparator.compare("Schedule A", "Schedule B") == {
        "shared": [],
        "only_a": ["Paper One", "Paper Two"],
        "only_b": ["Paper Three", "Paper Four"],
        "merged": [
            "Paper One",
            "Paper Two",
            "Paper Three",
            "Paper Four",
        ],
    }


def test_compare_handles_identical_schedules() -> None:
    paper_titles = ("Paper One", "Paper Two", "Paper Three")
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": paper_titles,
        }
    )
    comparator = ScheduleComparator(schedule_access)

    assert comparator.compare("Schedule A", "Schedule A") == {
        "shared": ["Paper One", "Paper Two", "Paper Three"],
        "only_a": [],
        "only_b": [],
        "merged": ["Paper One", "Paper Two", "Paper Three"],
    }


def test_compare_handles_empty_schedules() -> None:
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": (),
            "Schedule B": (),
        }
    )
    comparator = ScheduleComparator(schedule_access)

    assert comparator.compare("Schedule A", "Schedule B") == {
        "shared": [],
        "only_a": [],
        "only_b": [],
        "merged": [],
    }


@pytest.mark.parametrize(
    ("schedule_a", "schedule_b"),
    [
        ("Missing", "Schedule B"),
        ("Schedule A", "Missing"),
    ],
)
def test_compare_raises_value_error_when_either_schedule_is_missing(
    schedule_a: str,
    schedule_b: str,
) -> None:
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": ("Paper One",),
            "Schedule B": ("Paper Two",),
        }
    )
    comparator = ScheduleComparator(schedule_access)

    with pytest.raises(ValueError):
        comparator.compare(schedule_a, schedule_b)


def test_compare_does_not_modify_source_schedules() -> None:
    schedule_access = FakeScheduleAccess(
        {
            "Schedule A": ("Paper One", "Paper Two"),
            "Schedule B": ("Paper Two", "Paper Three"),
        }
    )
    comparator = ScheduleComparator(schedule_access)
    schedule_a_before = schedule_access.get_paper_titles("Schedule A")
    schedule_b_before = schedule_access.get_paper_titles("Schedule B")

    comparator.compare("Schedule A", "Schedule B")

    assert schedule_access.get_paper_titles("Schedule A") == schedule_a_before
    assert schedule_access.get_paper_titles("Schedule B") == schedule_b_before
