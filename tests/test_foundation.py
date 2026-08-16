"""
Starter tests for the foundation slice (Assessment 2A).

These tests show the pattern: call ScheduleService methods directly, with no
web browser involved, because all your logic lives behind the facade. Replace
and extend these with your own tests. For 2A you should cover, at least:

  * a normal import (load_sessions returns the right count, sessions/papers
    can be listed),
  * an edge case (for example an empty file, or a session with one paper),
  * an error case (for example a malformed file raising ValueError).

Run the tests with:

    pytest

Note: these tests will FAIL until you implement the foundation slice in
schedule_service.py. That is expected, and is the point of test-driven
development: write the test first, then make it pass.
"""

import os
import textwrap

import pytest

from schedule_service import ScheduleService

DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                    "sessions.csv")


def test_load_sessions_returns_paper_count():
    service = ScheduleService()
    count = service.load_sessions(DATA)
    assert count > 0


def test_list_sessions_after_load():
    service = ScheduleService()
    service.load_sessions(DATA)
    sessions = service.list_sessions()
    assert len(sessions) > 0
    # each session entry should at least name the session and count its papers
    first = sessions[0]
    assert "session" in first
    assert "paper_count" in first


def test_list_papers_for_a_known_session():
    service = ScheduleService()
    service.load_sessions(DATA)
    sessions = service.list_sessions()
    name = sessions[0]["session"]
    papers = service.list_papers(name)
    assert len(papers) >= 1
    assert "title" in papers[0]


def test_unknown_session_returns_empty_list():
    service = ScheduleService()
    service.load_sessions(DATA)
    assert service.list_papers("No Such Session 12345") == []


def test_malformed_file_raises_value_error(tmp_path):
    bad = tmp_path / "bad.csv"
    bad.write_text(textwrap.dedent("""\
        day,session,title
        2025-10-09,Only,Three Columns
    """))
    service = ScheduleService()
    with pytest.raises(ValueError):
        service.load_sessions(str(bad))
