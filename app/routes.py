"""
Provided routes. Each route calls ScheduleService and renders a template.

Two helper ideas make the app usable before everything is implemented:

* `call` runs a ScheduleService method and, if it still raises
  NotImplementedError, returns a sentinel so the page can show a friendly
  "not built yet" panel instead of crashing.

You do not need to edit this file.
"""

from __future__ import annotations

from flask import Blueprint, current_app, render_template, request, redirect, url_for, flash

bp = Blueprint("main", __name__)

_NOT_IMPLEMENTED = object()


def service():
    return current_app.config["SERVICE"]


def call(method_name, *args):
    """Call a ScheduleService method; return _NOT_IMPLEMENTED if it is a stub."""
    method = getattr(service(), method_name)
    try:
        return method(*args)
    except NotImplementedError:
        return _NOT_IMPLEMENTED


@bp.route("/")
def index():
    sessions = call("list_sessions")
    return render_template(
        "index.html",
        sessions=sessions if sessions is not _NOT_IMPLEMENTED else None,
        not_implemented=sessions is _NOT_IMPLEMENTED,
        data_loaded=current_app.config.get("DATA_LOADED", False),
        load_error=current_app.config.get("LOAD_ERROR"),
    )


@bp.route("/session/<path:session_name>")
def session_detail(session_name):
    papers = call("list_papers", session_name)
    return render_template(
        "session.html",
        session_name=session_name,
        papers=papers if papers is not _NOT_IMPLEMENTED else None,
        not_implemented=papers is _NOT_IMPLEMENTED,
    )


@bp.route("/add", methods=["POST"])
def add_paper():
    schedule_name = request.form.get("schedule_name", "").strip()
    paper_title = request.form.get("paper_title", "").strip()
    if not schedule_name:
        flash("Enter a schedule name first.")
        return redirect(request.referrer or url_for("main.index"))
    result = call("add_to_schedule", schedule_name, paper_title)
    if result is _NOT_IMPLEMENTED:
        flash("Building a schedule is not implemented yet (UC2).")
    else:
        flash(f'Added to "{schedule_name}".')
    return redirect(request.referrer or url_for("main.index"))


@bp.route("/schedules")
def schedules():
    names = call("list_schedules")
    return render_template(
        "schedules.html",
        names=names if names is not _NOT_IMPLEMENTED else None,
        not_implemented=names is _NOT_IMPLEMENTED,
    )


@bp.route("/schedule/<path:schedule_name>")
def schedule_detail(schedule_name):
    papers = call("list_schedule_papers", schedule_name)
    summary = call("summarise", schedule_name)
    return render_template(
        "schedule.html",
        schedule_name=schedule_name,
        papers=papers if papers is not _NOT_IMPLEMENTED else None,
        papers_missing=papers is _NOT_IMPLEMENTED,
        summary=summary if summary is not _NOT_IMPLEMENTED else None,
        summary_missing=summary is _NOT_IMPLEMENTED,
    )


@bp.route("/compare", methods=["GET", "POST"])
def compare():
    names = call("list_schedules")
    names = names if names is not _NOT_IMPLEMENTED else None
    result = None
    result_missing = False
    if request.method == "POST":
        a = request.form.get("schedule_a", "")
        b = request.form.get("schedule_b", "")
        result = call("compare", a, b)
        if result is _NOT_IMPLEMENTED:
            result = None
            result_missing = True
    return render_template(
        "compare.html",
        names=names,
        names_missing=names is None,
        result=result,
        result_missing=result_missing,
    )
