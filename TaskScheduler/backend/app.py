"""Supports the existing Streamlit deployment and the local Flask API."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))


def create_app():
    from flask import Flask, jsonify, request, send_from_directory
    from flask_cors import CORS
    from scheduler_service import run_scheduler

    web = Path(__file__).resolve().parents[1] / "web"
    app = Flask(__name__, static_folder=str(web), static_url_path="/static")
    CORS(app)

    @app.get("/")
    def home():
        return send_from_directory(web, "index.html")

    def calculate(mode):
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify(error="Request must contain a JSON object."), 400
        try:
            return jsonify(run_scheduler(data.get("tasks", []), data.get("dependencies", []), mode))
        except ValueError as exc:
            return jsonify(error=str(exc)), 400
        except RuntimeError as exc:
            return jsonify(error=str(exc)), 500

    @app.post("/schedule")
    def schedule():
        return calculate("schedule")

    @app.post("/critical-path")
    def critical_path():
        return calculate("critical")

    return app


# Keep TaskScheduler/backend/app.py working as the existing cloud entrypoint.
from streamlit.runtime.scriptrunner import get_script_run_ctx

if get_script_run_ctx(suppress_warning=True) is not None:
    from streamlit_ui import render
    render()
else:
    app = create_app()
    if __name__ == "__main__":
        app.run(port=5000)
