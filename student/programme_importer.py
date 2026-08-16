"""CSV import for the conference programme."""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from datetime import date, datetime, time
from typing import Protocol

from student.domain import Paper, Session


class IProgrammeImporter(Protocol):
    """Produces validated session domain objects from an external programme."""

    def read(self, csv_path: str) -> list[Session]:
        """Read and validate the programme at ``csv_path``."""
        ...


@dataclass
class _SessionBuilder:
    day: date
    track: str
    room: str
    start_time: time
    duration_min: int
    papers: list[Paper] = field(default_factory=list)


class CsvProgrammeImporter:
    """Read, validate, and group programme rows from a CSV file."""

    _REQUIRED_COLUMNS = (
        "day",
        "session",
        "title",
        "authors",
        "track",
        "room",
        "start_time",
        "duration_min",
    )
    _SESSION_METADATA = (
        "day",
        "track",
        "room",
        "start_time",
        "duration_min",
    )

    def read(self, csv_path: str) -> list[Session]:
        # Dictionary order preserves the first appearance of each session
        builders: dict[str, _SessionBuilder] = {}
        paper_titles: set[str] = set()

        try:
            with open(csv_path, "r", encoding="utf-8-sig", newline="") as csv_file:
                reader = csv.DictReader(csv_file, strict=True)
                self._validate_header(reader.fieldnames)

                for row in reader:
                    row_number = reader.line_num
                    values = self._required_values(row, row_number)
                    paper_title = values["title"]

                    if paper_title in paper_titles:
                        raise ValueError(
                            f"row {row_number}: duplicate paper title "
                            f"{paper_title!r}"
                        )

                    day = self._parse_day(values["day"], row_number)
                    start_time = self._parse_start_time(
                        values["start_time"], row_number
                    )
                    duration_min = self._parse_duration(
                        values["duration_min"], row_number
                    )
                    session_name = values["session"]
                    builder = builders.get(session_name)

                    if builder is None:
                        builder = _SessionBuilder(
                            day=day,
                            track=values["track"],
                            room=values["room"],
                            start_time=start_time,
                            duration_min=duration_min,
                        )
                        builders[session_name] = builder
                    else:
                        # Papers in one session must share the same details
                        self._validate_session_metadata(
                            session_name=session_name,
                            builder=builder,
                            day=day,
                            track=values["track"],
                            room=values["room"],
                            start_time=start_time,
                            duration_min=duration_min,
                            row_number=row_number,
                        )

                    builder.papers.append(
                        Paper(title=paper_title, authors=values["authors"])
                    )
                    paper_titles.add(paper_title)
        except csv.Error as exc:
            raise ValueError(f"malformed CSV content: {exc}") from exc
        except UnicodeDecodeError as exc:
            raise ValueError("malformed CSV content: file is not valid UTF-8") from exc

        return [
            Session(
                name=name,
                day=builder.day,
                track=builder.track,
                room=builder.room,
                start_time=builder.start_time,
                duration_min=builder.duration_min,
                papers=tuple(builder.papers),
            )
            for name, builder in builders.items()
        ]

    def _validate_header(self, fieldnames: list[str] | None) -> None:
        if fieldnames is None:
            raise ValueError("missing required CSV header")

        duplicate_columns = {
            column for column in fieldnames if fieldnames.count(column) > 1
        }
        if duplicate_columns:
            names = ", ".join(sorted(duplicate_columns))
            raise ValueError(f"CSV header contains duplicate columns: {names}")

        missing = [
            column for column in self._REQUIRED_COLUMNS if column not in fieldnames
        ]
        if missing:
            raise ValueError(
                "missing required CSV columns: " + ", ".join(missing)
            )

    def _required_values(
        self, row: dict[str | None, str | list[str] | None], row_number: int
    ) -> dict[str, str]:
        if None in row or any(value is None for value in row.values()):
            raise ValueError(
                f"row {row_number}: malformed row does not match the CSV header"
            )

        values: dict[str, str] = {}
        for column in self._REQUIRED_COLUMNS:
            raw_value = row[column]
            if not isinstance(raw_value, str) or not raw_value.strip():
                raise ValueError(
                    f"row {row_number}: required field {column!r} is blank"
                )
            values[column] = raw_value.strip()
        return values

    def _parse_day(self, value: str, row_number: int) -> date:
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError(
                f"row {row_number}: invalid day {value!r}; expected YYYY-MM-DD"
            ) from exc

    def _parse_start_time(self, value: str, row_number: int) -> time:
        try:
            return datetime.strptime(value, "%H:%M").time()
        except ValueError as exc:
            raise ValueError(
                f"row {row_number}: invalid start_time {value!r}; expected HH:MM"
            ) from exc

    def _parse_duration(self, value: str, row_number: int) -> int:
        message = (
            f"row {row_number}: invalid duration_min {value!r}; "
            "expected a positive integer"
        )
        try:
            duration_min = int(value)
        except ValueError as exc:
            raise ValueError(message) from exc

        if duration_min <= 0:
            raise ValueError(message)
        return duration_min

    def _validate_session_metadata(
        self,
        *,
        session_name: str,
        builder: _SessionBuilder,
        day: date,
        track: str,
        room: str,
        start_time: time,
        duration_min: int,
        row_number: int,
    ) -> None:
        existing = (
            builder.day,
            builder.track,
            builder.room,
            builder.start_time,
            builder.duration_min,
        )
        incoming = (day, track, room, start_time, duration_min)

        for field_name, old_value, new_value in zip(
            self._SESSION_METADATA, existing, incoming
        ):
            if old_value != new_value:
                raise ValueError(
                    f"row {row_number}: session {session_name!r} has "
                    f"conflicting {field_name}: {old_value!s} != {new_value!s}"
                )
