"""Tests for the personal schedule domain object."""

from student.domain import Schedule


def test_new_schedule_has_name_and_no_papers() -> None:
    schedule = Schedule("My Schedule")

    assert schedule.name == "My Schedule"
    assert schedule.paper_titles() == ()


def test_schedule_adds_papers_in_order() -> None:
    schedule = Schedule("My Schedule")

    schedule.add_paper("Paper One")
    schedule.add_paper("Paper Two")

    assert schedule.paper_titles() == ("Paper One", "Paper Two")


def test_schedule_ignores_duplicate_paper() -> None:
    schedule = Schedule("My Schedule")

    schedule.add_paper("Paper One")
    schedule.add_paper("Paper Two")
    schedule.add_paper("Paper One")

    assert schedule.paper_titles() == ("Paper One", "Paper Two")


def test_schedule_contains_added_paper() -> None:
    schedule = Schedule("My Schedule")

    assert not schedule.contains("Paper One")

    schedule.add_paper("Paper One")

    assert schedule.contains("Paper One")
