"""Store and retrieve named personal schedules."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from student.domain import Schedule
from student.session_access import ISessionAccess


class IScheduleAccess(Protocol):
    """Interface for managing personal schedules."""

    def add_paper(self, schedule_name: str, paper_title: str) -> None:
        ...

    def list_names(self) -> list[str]:
        ...

    def get_paper_titles(
        self, schedule_name: str
    ) -> tuple[str, ...] | None:
        ...

    def save_new(
        self, schedule_name: str, paper_titles: Iterable[str]
    ) -> None:
        ...


class ScheduleAccess:
    """Manage validated personal schedules in memory."""

    def __init__(self, session_access: ISessionAccess) -> None:
        self._session_access: ISessionAccess = session_access
        self._schedules_by_name: dict[str, Schedule] = {}

    def add_paper(self, schedule_name: str, paper_title: str) -> None:
        self._validate_name(schedule_name)
        if self._session_access.find_paper(paper_title) is None:
            raise ValueError(f"unknown paper title: {paper_title!r}")

        schedule = self._schedules_by_name.get(schedule_name)
        if schedule is None:
            schedule = Schedule(schedule_name)
            self._schedules_by_name[schedule_name] = schedule

        schedule.add_paper(paper_title)

    def list_names(self) -> list[str]:
        return list(self._schedules_by_name)

    def get_paper_titles(
        self, schedule_name: str
    ) -> tuple[str, ...] | None:
        schedule = self._schedules_by_name.get(schedule_name)
        return schedule.paper_titles() if schedule is not None else None

    def save_new(
        self, schedule_name: str, paper_titles: Iterable[str]
    ) -> None:
        raise NotImplementedError("save_new is not implemented yet")

    def _validate_name(self, schedule_name: str) -> None:
        if not schedule_name.strip():
            raise ValueError("schedule name must not be blank")
