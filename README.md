# Conference Session Planner — starter code

This is the provided starter code for Assessment 2A and 2B. It is a working web
application whose **logic is not yet implemented**. Your job is to implement the
logic, by writing your own classes and connecting them to the application
through one file: `schedule_service.py`.

You do **not** write any web or user-interface code. You never edit the `app/`
package.

## Setup

```bash
pip install -r requirements.txt
python run.py
```

Then open <http://127.0.0.1:5000>. The app runs immediately, but most pages will
show a **"Not implemented yet"** panel, because the methods they depend on have
not been written. As you implement those methods, the panels are replaced by
real content. Watching them disappear is how you track your progress.

## What is in here

```
conference_planner/
  app/                  PROVIDED web application. Do not edit.
  schedule_service.py   The seam. Fill in the methods marked # TODO(student).
  student/              Write YOUR OWN component classes in here.
  tests/                Starter pytest tests. Extend them with your own.
  data/sessions.csv     The conference programme (real IEEE ISMAR 2025 data).
  run.py                Starts the app.
```

## How to work

1. Open `data/sessions.csv` and understand the data. Each row is one paper;
   rows sharing a `session` value are the papers in that session block.
2. Run the app and see what does not work yet.
3. Open `schedule_service.py`. Read the method docstrings: these are the
   contracts the application relies on. Find the `# TODO(student)` markers.
4. Design your components and write them as classes in the `student/` package.
5. Wire each `ScheduleService` method to use your components.
6. Write `pytest` tests as you go. Run them with `pytest`.

For **Assessment 2A** you implement only the foundation slice: the three methods
under "UC1" in `schedule_service.py` (load the data, list sessions, list papers).
When those work, the programme will display in the app. You design the rest now
and implement it in **Assessment 2B**.

## Testing

```bash
pytest
```

The starter tests in `tests/test_foundation.py` will fail until you implement
the foundation slice. That is expected: write the test first, then make it pass.

## Rules

- Use only the Python standard library plus anything in `requirements.txt`.
- Keep your logic in your own components. `ScheduleService` should delegate to
  them, not contain all the logic itself.
- Do not change the names or parameters of the `ScheduleService` methods; the
  provided app depends on them.
