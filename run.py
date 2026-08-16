"""Run the Conference Session Planner.

    python run.py

Then open http://127.0.0.1:5000 in your browser. The app starts even before
you have implemented anything: pages will show a "not implemented yet" panel
where they depend on a method you have not written. As you implement the
ScheduleService methods, those panels are replaced by real content.
"""
from app import create_app

if __name__ == "__main__":
    create_app().run(debug=True)
