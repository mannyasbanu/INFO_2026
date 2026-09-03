"""Generate summaries for named personal schedules."""

from __future__ import annotations

from typing import Protocol

from student.schedule_access import IScheduleAccess
from student.session_access import ISessionAccess


class ISummaryGenerator(Protocol):
    """Interface for summarising personal schedules."""

    def summarise(self, schedule_name: str) -> dict:
        ...


class SummaryGenerator:
    """Calculate summary statistics from the in-memory schedule data."""

    _schedule_access: IScheduleAccess
    _session_access: ISessionAccess

    def __init__(
        self,
        schedule_access: IScheduleAccess,
        session_access: ISessionAccess,
    ) -> None:
        self._schedule_access = schedule_access
        self._session_access = session_access

    def summarise(self, schedule_name: str) -> dict:
        paper_titles = self._require_schedule(schedule_name)
        tracks: dict[str, int] = {}
        counted_sessions: set[str] = set()
        total_minutes = 0

        for paper_title in paper_titles:
            session = self._session_access.find_session_for_paper(paper_title)
            if session is None:
                raise ValueError(
                    f"stored paper {paper_title!r} is missing from the programme"
                )

            tracks[session.track] = tracks.get(session.track, 0) + 1
            if session.name not in counted_sessions:
                counted_sessions.add(session.name)
                total_minutes += session.duration_min

        return {
            "paper_count": len(paper_titles),
            "tracks": tracks,
            "total_minutes": total_minutes,
        }

    def _require_schedule(self, schedule_name: str) -> tuple[str, ...]:
        paper_titles = self._schedule_access.get_paper_titles(schedule_name)
        if paper_titles is None:
            raise ValueError(f"unknown schedule: {schedule_name!r}")
        return paper_titles
