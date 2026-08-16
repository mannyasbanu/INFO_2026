"""
ScheduleService: the single connection point between the provided web
application and the logic you write.

HOW THIS FILE WORKS
-------------------
The provided Flask application (in the `app/` package) calls the methods of
this class, and ONLY these methods. It never calls your own classes directly.
Your job is to make each method below do what its docstring promises.

You do this by writing your OWN classes in the `student/` package (for example
a SessionAccess class, a ScheduleAccess class, and so on), and then wiring the
methods here to use them. This file is the starting point for your code, not
the place where all of your code lives. Keep the real logic in your components
and let this class delegate to them.

WHAT TO DO
----------
Each method you must implement is marked with:

    # TODO(student): implement this

and currently raises NotImplementedError. While a method still raises
NotImplementedError, the web page that uses it will show a friendly
"not implemented yet" message instead of crashing, so you can build one use
case at a time and watch each part of the application come to life.

For Assessment 2A you implement ONLY the foundation slice (the three methods
under "UC1"). Design the rest now; implement them in Assessment 2B.

You may add a constructor, helper methods, and any imports you need. Do not
change the NAME or PARAMETERS of the methods below, because the provided web
application relies on them.
"""

from __future__ import annotations

from student.programme_importer import CsvProgrammeImporter
from student.session_access import ISessionAccess, SessionAccess


class ScheduleService:
    """Facade the web application calls. Delegate to your own components."""

    def __init__(self) -> None:
        """Set up the service.

        This is a good place to create the components you designed (for
        example your session store and schedule store) and keep references
        to them. The web application creates ONE ScheduleService when it
        starts and reuses it for every request, so anything you store on
        `self` here persists for the life of the running application.
        """
        importer = CsvProgrammeImporter()
        self._session_access: ISessionAccess = SessionAccess(importer)

    # ------------------------------------------------------------------ #
    # UC1: Import and view the programme  (IMPLEMENT THESE FOR 2A)         #
    # ------------------------------------------------------------------ #

    def load_sessions(self, csv_path: str) -> int:
        """Import the session catalogue from a CSV file into internal storage.

        The file at `csv_path` has the columns:
            day, session, title, authors, track, room, start_time, duration_min
        Several rows share the same `session` value: those are the papers in
        that session block. Store everything in your own internal storage so
        that the other methods never need to read the file again.

        Returns:
            The number of papers (rows) loaded.

        Raises:
            ValueError: if the file is missing required columns or is malformed.
        """
        return self._session_access.load_sessions(csv_path)

    def list_sessions(self) -> list[dict]:
        """Return the session blocks for the interface to display.

        Returns:
            A list with one entry per session block, each a dict with keys:
                "session"     the session block name
                "day"         the date, as YYYY-MM-DD
                "track"       the session's track
                "room"        the room
                "start_time"  the start, as HH:MM
                "duration_min"the length in minutes
                "paper_count" how many papers are in the session
            The web application uses these to show the list of sessions.
        """
        return [
            {
                "session": session.name,
                "day": session.day.isoformat(),
                "track": session.track,
                "room": session.room,
                "start_time": session.start_time.strftime("%H:%M"),
                "duration_min": session.duration_min,
                "paper_count": session.paper_count(),
            }
            for session in self._session_access.list_sessions()
        ]

    def list_papers(self, session_name: str) -> list[dict]:
        """Return the papers inside one session block.

        Args:
            session_name: the `session` value to look up.

        Returns:
            A list with one entry per paper, each a dict with keys:
                "title"    the paper title
                "authors"  the authors
                "track"    the track
            If no session matches, return an empty list.
        """
        papers = self._session_access.list_papers(session_name)
        if not papers:
            return []

        owner = self._session_access.find_session_for_paper(papers[0].title)
        # Every loaded paper is indexed with its owning session
        assert owner is not None
        return [
            {
                "title": paper.title,
                "authors": paper.authors,
                "track": owner.track,
            }
            for paper in papers
        ]

    # ------------------------------------------------------------------ #
    # UC2: Build a schedule  (DESIGN FOR 2A, IMPLEMENT FOR 2B)             #
    # ------------------------------------------------------------------ #

    def add_to_schedule(self, schedule_name: str, paper_title: str) -> None:
        """Add a paper to a named schedule, creating the schedule if needed.

        Args:
            schedule_name: the schedule to add to (created if it does not exist).
            paper_title:   the unique title of the paper to add.

        Raises:
            ValueError: if no paper with that title exists.
        """
        # TODO(student): implement this
        raise NotImplementedError("add_to_schedule is not implemented yet")

    def list_schedules(self) -> list[str]:
        """Return the names of all saved schedules (for the interface to list)."""
        # TODO(student): implement this
        raise NotImplementedError("list_schedules is not implemented yet")

    def list_schedule_papers(self, schedule_name: str) -> list[dict]:
        """Return the papers in one saved schedule.

        Each entry is a dict with the same keys as `list_papers`, plus
        "session", "day", "room", "start_time" and "duration_min" so the
        interface can show when each paper is on. Return an empty list if the
        schedule does not exist.
        """
        # TODO(student): implement this
        raise NotImplementedError("list_schedule_papers is not implemented yet")

    # ------------------------------------------------------------------ #
    # UC3: Compare schedules  (DESIGN FOR 2A, IMPLEMENT FOR 2B)            #
    # ------------------------------------------------------------------ #

    def compare(self, schedule_a: str, schedule_b: str) -> dict:
        """Compare two saved schedules.

        Returns:
            A dict with keys:
                "shared"  list of paper titles in BOTH schedules
                "only_a"  list of paper titles only in schedule_a
                "only_b"  list of paper titles only in schedule_b
                "merged"  list of paper titles in EITHER schedule (no repeats)
        """
        # TODO(student): implement this
        raise NotImplementedError("compare is not implemented yet")

    def save_joint_schedule(self, new_name: str, schedule_a: str,
                            schedule_b: str) -> None:
        """Save the merged result of comparing two schedules as a new schedule.

        The new schedule contains every paper from either schedule, with no
        repeats.
        """
        # TODO(student): implement this
        raise NotImplementedError("save_joint_schedule is not implemented yet")

    # ------------------------------------------------------------------ #
    # UC4: Summarise a schedule  (DESIGN FOR 2A, IMPLEMENT FOR 2B)         #
    # ------------------------------------------------------------------ #

    def summarise(self, schedule_name: str) -> dict:
        """Summarise a saved schedule.

        Returns:
            A dict with keys:
                "paper_count"   total number of papers
                "tracks"        a dict of track name -> count
                "total_minutes" sum of the durations of the papers' sessions
        """
        # TODO(student): implement this
        raise NotImplementedError("summarise is not implemented yet")
