"""Compatibility entrypoint for the original root backend path."""
from pathlib import Path
import runpy

namespace = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "TaskScheduler" / "backend" / "app.py"),
    run_name=__name__,
)
if "app" in namespace:
    app = namespace["app"]
