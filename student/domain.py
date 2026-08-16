"""Domain objects for the conference programme."""

from __future__ import annotations

from datetime import date, time


class Paper:
    """A paper presented as part of a conference session."""

    def __init__(self, title: str, authors: str) -> None:
        self._title = title
        self._authors = authors

    @property
    def title(self) -> str:
        return self._title

    @property
    def authors(self) -> str:
        return self._authors


class Session:
    """A scheduled block with an ordered collection of papers."""

    def __init__(
        self,
        name: str,
        day: date,
        track: str,
        room: str,
        start_time: time,
        duration_min: int,
        papers: tuple[Paper, ...],
    ) -> None:
        self._name = name
        self._day = day
        self._track = track
        self._room = room
        self._start_time = start_time
        self._duration_min = duration_min
        self._papers = tuple(papers)

    @property
    def name(self) -> str:
        return self._name

    @property
    def day(self) -> date:
        return self._day

    @property
    def track(self) -> str:
        return self._track

    @property
    def room(self) -> str:
        return self._room

    @property
    def start_time(self) -> time:
        return self._start_time

    @property
    def duration_min(self) -> int:
        return self._duration_min

    @property
    def papers(self) -> tuple[Paper, ...]:
        return self._papers

    def paper_count(self) -> int:
        return len(self._papers)

    def find_paper(self, title: str) -> Paper | None:
        for paper in self._papers:
            if paper.title == title:
                return paper
        return None
