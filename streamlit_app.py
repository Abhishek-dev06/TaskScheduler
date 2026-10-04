"""Canonical Streamlit Cloud entrypoint."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent / "TaskScheduler" / "backend"))
from streamlit_ui import render

render()
