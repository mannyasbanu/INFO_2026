"""Tests for importing and reading the conference programme."""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

from schedule_service import ScheduleService
from student.programme_importer import CsvProgrammeImporter
from student.session_access import SessionAccess


REQUIRED_COLUMNS = [
    "day",
    "session",
    "title",
    "authors",
    "track",
    "room",
    "start_time",
    "duration_min",
]
DATA = Path(__file__).parent.parent / "data" / "sessions.csv"


def programme_row(
    session: str,
    title: str,
    *,
    authors: str = "Ada Author",
    day: str = "2025-10-09",
    track: str = "Research",
    room: str = "Room 1",
    start_time: str = "09:30",
    duration_min: str = "60",
) -> dict[str, str]:
    return {
        "day": day,
        "session": session,
        "title": title,
        "authors": authors,
        "track": track,
        "room": room,
        "start_time": start_time,
        "duration_min": duration_min,
    }


def write_programme(
    tmp_path: Path,
    rows: list[dict[str, str]],
    *,
    columns: list[str] | None = None,
    filename: str = "programme.csv",
) -> Path:
    path = tmp_path / filename
    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=columns or REQUIRED_COLUMNS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)
    return path


def test_valid_csv_loads_the_number_of_papers(tmp_path: Path) -> None:
    # Paper count is based on rows, even when rows share a session
    path = write_programme(
        tmp_path,
        [
            programme_row("Session A", "Paper 1"),
            programme_row("Session A", "Paper 2"),
            programme_row("Session B", "Paper 3"),
        ],
    )

    assert ScheduleService().load_sessions(str(path)) == 3


def test_rows_with_the_same_name_become_one_session(tmp_path: Path) -> None:
    # Rows with the same session name should be grouped
    path = write_programme(
        tmp_path,
        [
            programme_row("One Session", "Paper 1"),
            programme_row("One Session", "Paper 2"),
        ],
    )
    access = SessionAccess(CsvProgrammeImporter())

    access.load_sessions(str(path))

    sessions = access.list_sessions()
    assert len(sessions) == 1
    assert sessions[0].name == "One Session"
    assert sessions[0].paper_count() == 2


def test_list_sessions_matches_the_frontend_contract(tmp_path: Path) -> None:
    # Session dictionaries must use the display format expected by the web app
    path = write_programme(
        tmp_path,
        [
            programme_row(
                "Spatial Systems",
                "Paper 1",
                day="2025-11-03",
                track="Displays",
                room="Auditorium",
                start_time="08:05",
                duration_min="75",
            ),
            programme_row(
                "Spatial Systems",
                "Paper 2",
                day="2025-11-03",
                track="Displays",
                room="Auditorium",
                start_time="08:05",
                duration_min="75",
            ),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_sessions() == [
        {
            "session": "Spatial Systems",
            "day": "2025-11-03",
            "track": "Displays",
            "room": "Auditorium",
            "start_time": "08:05",
            "duration_min": 75,
            "paper_count": 2,
        }
    ]


def test_list_papers_returns_papers_and_owning_track(tmp_path: Path) -> None:
    # Paper dictionaries include the track from their owning session
    path = write_programme(
        tmp_path,
        [
            programme_row(
                "Interaction",
                "Paper 1",
                authors="Alice and Bob",
                track="Human Factors",
            ),
            programme_row(
                "Interaction",
                "Paper 2",
                authors="Carol",
                track="Human Factors",
            ),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_papers("Interaction") == [
        {
            "title": "Paper 1",
            "authors": "Alice and Bob",
            "track": "Human Factors",
        },
        {"title": "Paper 2", "authors": "Carol", "track": "Human Factors"},
    ]


def test_sessions_and_papers_retain_csv_order(tmp_path: Path) -> None:
    # Catalogue order follows CSV appearance rather than alphabetical order
    path = write_programme(
        tmp_path,
        [
            programme_row("Second by Name", "Paper B"),
            programme_row("First by Name", "Paper C"),
            programme_row("Second by Name", "Paper A"),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    assert [item["session"] for item in service.list_sessions()] == [
        "Second by Name",
        "First by Name",
    ]
    assert [item["title"] for item in service.list_papers("Second by Name")] == [
        "Paper B",
        "Paper A",
    ]


def test_header_only_csv_loads_an_empty_catalogue(tmp_path: Path) -> None:
    # A valid header with no rows represents an empty programme
    path = write_programme(tmp_path, [])
    service = ScheduleService()

    assert service.load_sessions(str(path)) == 0
    assert service.list_sessions() == []


def test_unknown_session_returns_an_empty_list(tmp_path: Path) -> None:
    # An unknown name should not produce an error
    path = write_programme(tmp_path, [programme_row("Known", "Paper 1")])
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_papers("Unknown") == []


def test_session_with_one_paper(tmp_path: Path) -> None:
    # A one-paper session should display normally
    path = write_programme(tmp_path, [programme_row("Solo", "Only Paper")])
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_sessions()[0]["paper_count"] == 1
    assert [paper["title"] for paper in service.list_papers("Solo")] == [
        "Only Paper"
    ]


def test_sessions_at_the_same_date_and_time_remain_separate(
    tmp_path: Path,
) -> None:
    # Sharing a time slot does not make two sessions the same
    path = write_programme(
        tmp_path,
        [
            programme_row("Session A", "Paper A", room="Room 1"),
            programme_row("Session B", "Paper B", room="Room 2"),
        ],
    )
    service = ScheduleService()
    service.load_sessions(str(path))

    assert [session["session"] for session in service.list_sessions()] == [
        "Session A",
        "Session B",
    ]


def test_larger_session_has_all_papers_and_the_correct_count(
    tmp_path: Path,
) -> None:
    # The summary count should agree with the papers returned
    rows = [programme_row("Large Session", f"Paper {number}") for number in range(6)]
    path = write_programme(tmp_path, rows)
    service = ScheduleService()
    service.load_sessions(str(path))

    assert service.list_sessions()[0]["paper_count"] == 6
    assert [paper["title"] for paper in service.list_papers("Large Session")] == [
        f"Paper {number}" for number in range(6)
    ]


def test_named_extra_columns_are_allowed(tmp_path: Path) -> None:
    # Named columns outside the required schema should be ignored
    row = programme_row("Session A", "Paper 1")
    row["notes"] = "Optional information"
    path = write_programme(
        tmp_path,
        [row],
        columns=REQUIRED_COLUMNS + ["notes"],
    )

    assert ScheduleService().load_sessions(str(path)) == 1


def test_completely_empty_file_raises_value_error(tmp_path: Path) -> None:
    # A file without a header is not a valid programme
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    with pytest.raises(ValueError, match="header"):
        CsvProgrammeImporter().read(str(path))


def test_missing_required_column_raises_value_error(tmp_path: Path) -> None:
    # Every required column must be present in the header
    columns = [column for column in REQUIRED_COLUMNS if column != "authors"]
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1")],
        columns=columns,
    )

    with pytest.raises(ValueError, match="authors"):
        CsvProgrammeImporter().read(str(path))


def test_blank_required_value_raises_value_error(tmp_path: Path) -> None:
    # Whitespace-only values count as missing
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", authors="   ")],
    )

    with pytest.raises(ValueError, match="row 2.*authors.*blank"):
        CsvProgrammeImporter().read(str(path))


def test_malformed_row_raises_value_error(tmp_path: Path) -> None:
    # Extra values without a matching header column make the row malformed
    path = tmp_path / "malformed.csv"
    path.write_text(
        ",".join(REQUIRED_COLUMNS)
        + "\n2025-10-09,Session A,Paper 1,Author,Track,Room 1,09:30,60,extra\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="row 2.*malformed"):
        CsvProgrammeImporter().read(str(path))


def test_invalid_date_raises_value_error(tmp_path: Path) -> None:
    # Calendar dates must be valid
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", day="2025-02-30")],
    )

    with pytest.raises(ValueError, match="row 2.*day"):
        CsvProgrammeImporter().read(str(path))


def test_invalid_time_raises_value_error(tmp_path: Path) -> None:
    # Times outside the 24-hour clock must be rejected
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", start_time="25:00")],
    )

    with pytest.raises(ValueError, match="row 2.*start_time"):
        CsvProgrammeImporter().read(str(path))


def test_non_integer_duration_raises_value_error(tmp_path: Path) -> None:
    # Duration must contain an integer value
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", duration_min="one hour")],
    )

    with pytest.raises(ValueError, match="row 2.*duration_min"):
        CsvProgrammeImporter().read(str(path))


@pytest.mark.parametrize("duration", ["0", "-1"])
def test_non_positive_duration_raises_value_error(
    tmp_path: Path, duration: str
) -> None:
    # Zero and negative durations are invalid
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", duration_min=duration)],
    )

    with pytest.raises(ValueError, match="row 2.*duration_min"):
        CsvProgrammeImporter().read(str(path))


def test_duplicate_paper_title_raises_value_error(tmp_path: Path) -> None:
    # Duplicate titles are not allowed anywhere in the programme
    path = write_programme(
        tmp_path,
        [
            programme_row("Session A", "Repeated Paper"),
            programme_row("Session B", "Repeated Paper", room="Room 2"),
        ],
    )

    with pytest.raises(ValueError, match="row 3.*duplicate paper title"):
        CsvProgrammeImporter().read(str(path))


def test_conflicting_metadata_for_one_session_raises_value_error(
    tmp_path: Path,
) -> None:
    # Repeated session rows must describe the same room and time block
    path = write_programme(
        tmp_path,
        [
            programme_row("Session A", "Paper 1", room="Room 1"),
            programme_row("Session A", "Paper 2", room="Room 2"),
        ],
    )

    with pytest.raises(ValueError, match="row 3.*conflicting room"):
        CsvProgrammeImporter().read(str(path))


def test_failed_import_preserves_the_previous_catalogue(tmp_path: Path) -> None:
    # Failed import should keep the previously loaded data
    valid_path = write_programme(
        tmp_path,
        [programme_row("Valid Session", "Valid Paper")],
        filename="valid.csv",
    )
    invalid_path = write_programme(
        tmp_path,
        [programme_row("Invalid Session", "Broken Paper", duration_min="0")],
        filename="invalid.csv",
    )
    service = ScheduleService()
    service.load_sessions(str(valid_path))
    sessions_before = service.list_sessions()
    papers_before = service.list_papers("Valid Session")

    with pytest.raises(ValueError):
        service.load_sessions(str(invalid_path))

    assert service.list_sessions() == sessions_before
    assert service.list_papers("Valid Session") == papers_before


def test_session_access_finds_paper_and_its_owner(tmp_path: Path) -> None:
    # Both title indexes should resolve known papers and reject unknown ones
    path = write_programme(
        tmp_path,
        [programme_row("Session A", "Paper 1", authors="Named Author")],
    )
    access = SessionAccess(CsvProgrammeImporter())
    access.load_sessions(str(path))

    paper = access.find_paper("Paper 1")
    owner = access.find_session_for_paper("Paper 1")
    assert paper is not None and paper.authors == "Named Author"
    assert owner is not None and owner.name == "Session A"
    assert access.find_paper("Unknown Paper") is None
    assert access.find_session_for_paper("Unknown Paper") is None


def test_supplied_programme_loads_and_can_be_read() -> None:
    # The supplied dataset should work through the complete read path
    service = ScheduleService()

    paper_count = service.load_sessions(str(DATA))
    sessions = service.list_sessions()

    assert paper_count > 0
    assert sessions
    assert service.list_papers(sessions[0]["session"])


@pytest.mark.parametrize(
    ("method_name", "arguments"),
    [
        ("compare", ("A", "B")),
        ("save_joint_schedule", ("Joint", "A", "B")),
        ("summarise", ("My Schedule",)),
    ],
)
def test_later_use_cases_remain_unimplemented(
    method_name: str, arguments: tuple[str, ...]
) -> None:
    # Later features should remain unavailable until their own implementation
    service = ScheduleService()

    with pytest.raises(NotImplementedError):
        getattr(service, method_name)(*arguments)
