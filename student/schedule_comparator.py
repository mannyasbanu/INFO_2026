"""Compare the paper selections in saved schedules."""

from __future__ import annotations

from typing import Protocol

from student.schedule_access import IScheduleAccess


class IScheduleComparator(Protocol):
    """Interface for comparing saved schedules."""

    def compare(
        self,
        schedule_a: str,
        schedule_b: str,
    ) -> dict[str, list[str]]:
        ...


class ScheduleComparator:
    """Compare saved schedules by their selected paper titles."""

    _schedule_access: IScheduleAccess

    def __init__(self, schedule_access: IScheduleAccess) -> None:
        self._schedule_access = schedule_access

    def compare(
        self,
        schedule_a: str,
        schedule_b: str,
    ) -> dict[str, list[str]]:
        paper_titles_a = self._require_schedule(schedule_a)
        paper_titles_b = self._require_schedule(schedule_b)
        titles_in_a = set(paper_titles_a)
        titles_in_b = set(paper_titles_b)

        shared = [title for title in paper_titles_a if title in titles_in_b]
        only_a = [title for title in paper_titles_a if title not in titles_in_b]
        only_b = [title for title in paper_titles_b if title not in titles_in_a]

        merged: list[str] = []
        merged_titles: set[str] = set()
        for paper_titles in (paper_titles_a, paper_titles_b):
            for title in paper_titles:
                if title not in merged_titles:
                    merged.append(title)
                    merged_titles.add(title)

        return {
            "shared": shared,
            "only_a": only_a,
            "only_b": only_b,
            "merged": merged,
        }

    def _require_schedule(self, schedule_name: str) -> tuple[str, ...]:
        paper_titles = self._schedule_access.get_paper_titles(schedule_name)
        if paper_titles is None:
            raise ValueError(f"schedule does not exist: {schedule_name!r}")
        return paper_titles
