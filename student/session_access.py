"""In-memory access to imported conference sessions and papers."""

from __future__ import annotations

from typing import Protocol

from student.domain import Paper, Session
from student.programme_importer import IProgrammeImporter


class ISessionAccess(Protocol):
    """Read interface for the currently loaded conference programme."""

    def load_sessions(self, csv_path: str) -> int:
        ...

    def list_sessions(self) -> tuple[Session, ...]:
        ...

    def list_papers(self, session_name: str) -> tuple[Paper, ...]:
        ...

    def find_paper(self, paper_title: str) -> Paper | None:
        ...

    def find_session_for_paper(self, paper_title: str) -> Session | None:
        ...


class SessionAccess:
    """Store and index a validated, ordered session catalogue in memory."""

    def __init__(self, importer: IProgrammeImporter) -> None:
        self._importer = importer
        self._sessions_by_name: dict[str, Session] = {}
        self._session_by_paper_title: dict[str, Session] = {}

    def load_sessions(self, csv_path: str) -> int:
        sessions = self._importer.read(csv_path)

        # Build replacement indexes before changing the current catalogue
        sessions_by_name: dict[str, Session] = {}
        session_by_paper_title: dict[str, Session] = {}
        for session in sessions:
            sessions_by_name[session.name] = session
            # Titles are unique, so they provide a direct owner lookup
            for paper in session.papers:
                session_by_paper_title[paper.title] = session

        self._sessions_by_name = sessions_by_name
        self._session_by_paper_title = session_by_paper_title
        return sum(session.paper_count() for session in sessions)

    def list_sessions(self) -> tuple[Session, ...]:
        return tuple(self._sessions_by_name.values())

    def list_papers(self, session_name: str) -> tuple[Paper, ...]:
        session = self._sessions_by_name.get(session_name)
        return session.papers if session is not None else ()

    def find_paper(self, paper_title: str) -> Paper | None:
        session = self.find_session_for_paper(paper_title)
        return session.find_paper(paper_title) if session is not None else None

    def find_session_for_paper(self, paper_title: str) -> Session | None:
        return self._session_by_paper_title.get(paper_title)
