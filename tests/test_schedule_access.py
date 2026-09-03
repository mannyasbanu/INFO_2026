"""Tests for storing and retrieving named personal schedules."""

from __future__ import annotations

import pytest

from student.domain import Paper
from student.schedule_access import ScheduleAccess


class FakeSessionAccess:
    """Provide a small in-memory paper catalogue for schedule access tests."""

    def __init__(self) -> None:
        self._papers_by_title = {
            "Paper One": Paper("Paper One", "A. Author"),
            "Paper Two": Paper("Paper Two", "B. Author"),
            "Paper Three": Paper("Paper Three", "C. Author"),
        }

    def find_paper(self, paper_title: str) -> Paper | None:
        return self._papers_by_title.get(paper_title)


@pytest.fixture
def schedule_access() -> ScheduleAccess:
    return ScheduleAccess(FakeSessionAccess())


def test_add_paper_creates_named_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.add_paper("My Schedule", "Paper One")

    assert schedule_access.get_paper_titles("My Schedule") == ("Paper One",)


def test_add_paper_reuses_existing_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.add_paper("My Schedule", "Paper One")
    schedule_access.add_paper("My Schedule", "Paper Two")

    assert schedule_access.get_paper_titles("My Schedule") == (
        "Paper One",
        "Paper Two",
    )


def test_multiple_schedules_are_independent(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.add_paper("Morning Picks", "Paper One")
    schedule_access.add_paper("Afternoon Picks", "Paper Two")
    schedule_access.add_paper("Morning Picks", "Paper Three")

    assert schedule_access.get_paper_titles("Morning Picks") == (
        "Paper One",
        "Paper Three",
    )
    assert schedule_access.get_paper_titles("Afternoon Picks") == ("Paper Two",)


def test_list_names_returns_saved_schedules(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.add_paper("First Schedule", "Paper One")
    schedule_access.add_paper("Second Schedule", "Paper Two")

    assert schedule_access.list_names() == ["First Schedule", "Second Schedule"]


def test_get_paper_titles_returns_none_for_unknown_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    assert schedule_access.get_paper_titles("Unknown Schedule") is None


def test_unknown_paper_is_rejected_without_creating_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    with pytest.raises(ValueError):
        schedule_access.add_paper("My Schedule", "Unknown Paper")

    assert schedule_access.get_paper_titles("My Schedule") is None


@pytest.mark.parametrize("schedule_name", ["", "   "])
def test_blank_schedule_name_raises_value_error(
    schedule_access: ScheduleAccess,
    schedule_name: str,
) -> None:
    with pytest.raises(ValueError):
        schedule_access.add_paper(schedule_name, "Paper One")


def test_same_paper_can_belong_to_multiple_schedules(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.add_paper("First Schedule", "Paper One")
    schedule_access.add_paper("Second Schedule", "Paper One")

    assert schedule_access.get_paper_titles("First Schedule") == ("Paper One",)
    assert schedule_access.get_paper_titles("Second Schedule") == ("Paper One",)


def test_save_new_stores_papers_in_supplied_order(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.save_new(
        "Joint",
        ["Paper Three", "Paper One", "Paper Two"],
    )

    assert schedule_access.get_paper_titles("Joint") == (
        "Paper Three",
        "Paper One",
        "Paper Two",
    )


def test_save_new_allows_empty_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.save_new("Empty", [])

    assert schedule_access.get_paper_titles("Empty") == ()
    assert "Empty" in schedule_access.list_names()


def test_save_new_removes_duplicate_titles_preserving_first_occurrence(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.save_new(
        "Joint",
        ["Paper One", "Paper Two", "Paper One"],
    )

    assert schedule_access.get_paper_titles("Joint") == (
        "Paper One",
        "Paper Two",
    )


def test_save_new_accepts_a_general_iterable(
    schedule_access: ScheduleAccess,
) -> None:
    titles = (title for title in ["Paper One", "Paper Two"])

    schedule_access.save_new("Joint", titles)

    assert schedule_access.get_paper_titles("Joint") == (
        "Paper One",
        "Paper Two",
    )


@pytest.mark.parametrize("schedule_name", ["", "   "])
def test_save_new_rejects_blank_name(
    schedule_access: ScheduleAccess,
    schedule_name: str,
) -> None:
    with pytest.raises(ValueError):
        schedule_access.save_new(schedule_name, ["Paper One"])

    assert schedule_access.get_paper_titles(schedule_name) is None


def test_save_new_rejects_unknown_paper_without_creating_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    with pytest.raises(ValueError):
        schedule_access.save_new(
            "Invalid",
            ["Paper One", "Unknown Paper"],
        )

    assert schedule_access.get_paper_titles("Invalid") is None


def test_save_new_rejects_existing_name_without_overwriting_schedule(
    schedule_access: ScheduleAccess,
) -> None:
    schedule_access.save_new("Existing", ["Paper One"])

    with pytest.raises(ValueError):
        schedule_access.save_new("Existing", ["Paper Two"])

    assert schedule_access.get_paper_titles("Existing") == ("Paper One",)
