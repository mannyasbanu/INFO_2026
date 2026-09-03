"""Tests for summarising saved schedules."""

from __future__ import annotations

from datetime import date, time

import pytest

from student.domain import Paper, Session
from student.summary_generator import SummaryGenerator


class FakeScheduleAccess:
    """Return paper titles from a small collection of saved schedules."""

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


class FakeSessionAccess:
    """Map paper titles to their real session domain objects."""

    def __init__(self, sessions: tuple[Session, ...]) -> None:
        self._sessions_by_paper_title = {
            paper.title: session
            for session in sessions
            for paper in session.papers
        }

    def find_session_for_paper(self, paper_title: str) -> Session | None:
        return self._sessions_by_paper_title.get(paper_title)


@pytest.fixture
def catalogue() -> tuple[Session, ...]:
    return (
        Session(
            name="Display Session",
            day=date(2025, 10, 9),
            track="Displays",
            room="Room 201",
            start_time=time(10, 30),
            duration_min=60,
            papers=(
                Paper("Display Paper One", "A. Author"),
                Paper("Display Paper Two", "B. Author"),
            ),
        ),
        Session(
            name="Tracking Session",
            day=date(2025, 10, 9),
            track="Tracking",
            room="Room 202",
            start_time=time(10, 30),
            duration_min=60,
            papers=(Paper("Tracking Paper", "C. Author"),),
        ),
        Session(
            name="Later Display Session",
            day=date(2025, 10, 9),
            track="Displays",
            room="Room 203",
            start_time=time(12, 0),
            duration_min=45,
            papers=(Paper("Later Display Paper", "D. Author"),),
        ),
    )


def make_summary_generator(
    schedules: dict[str, tuple[str, ...]],
    catalogue: tuple[Session, ...],
) -> SummaryGenerator:
    return SummaryGenerator(
        FakeScheduleAccess(schedules),
        FakeSessionAccess(catalogue),
    )


def test_summarise_returns_paper_track_and_duration_totals(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator(
        {
            "My Schedule": (
                "Display Paper One",
                "Tracking Paper",
                "Later Display Paper",
            )
        },
        catalogue,
    )

    assert generator.summarise("My Schedule") == {
        "paper_count": 3,
        "tracks": {
            "Displays": 2,
            "Tracking": 1,
        },
        "total_minutes": 165,
    }


def test_summarise_counts_same_session_duration_once(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator(
        {
            "My Schedule": (
                "Display Paper One",
                "Display Paper Two",
            )
        },
        catalogue,
    )

    # Both papers belong to the same session block, so its duration is counted once.
    assert generator.summarise("My Schedule") == {
        "paper_count": 2,
        "tracks": {
            "Displays": 2,
        },
        "total_minutes": 60,
    }


def test_summarise_counts_overlapping_sessions_in_full(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator(
        {
            "My Schedule": (
                "Display Paper One",
                "Tracking Paper",
            )
        },
        catalogue,
    )

    # The sessions overlap, but both scheduled durations still contribute.
    assert generator.summarise("My Schedule") == {
        "paper_count": 2,
        "tracks": {
            "Displays": 1,
            "Tracking": 1,
        },
        "total_minutes": 120,
    }


def test_summarise_returns_zero_values_for_empty_schedule(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator({"Empty": ()}, catalogue)

    assert generator.summarise("Empty") == {
        "paper_count": 0,
        "tracks": {},
        "total_minutes": 0,
    }


def test_summarise_raises_value_error_for_missing_schedule(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator({}, catalogue)

    with pytest.raises(ValueError):
        generator.summarise("Missing")


def test_summarise_raises_value_error_when_paper_has_no_session(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator(
        {"Invalid": ("Unknown Paper",)},
        catalogue,
    )

    with pytest.raises(ValueError):
        generator.summarise("Invalid")


def test_summarise_preserves_first_track_encounter_order(
    catalogue: tuple[Session, ...],
) -> None:
    generator = make_summary_generator(
        {
            "My Schedule": (
                "Tracking Paper",
                "Display Paper One",
                "Later Display Paper",
            )
        },
        catalogue,
    )

    result = generator.summarise("My Schedule")

    assert list(result["tracks"]) == [
        "Tracking",
        "Displays",
    ]
