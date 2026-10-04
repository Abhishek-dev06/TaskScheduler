from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

SCHEDULER_PATH = r"D:\TaskScheduler\TaskScheduler\scheduler.exe"


def build_input(tasks, dependencies):
    input_data = f"{len(tasks)}\n"

    for task in tasks:
        name = task.get("name", "Task")
        priority = task.get("priority", 1)
        deadline = task.get("deadline", 10)
        duration = task.get("duration", 1)

        input_data += f"{name}\n"
        input_data += f"{priority} {deadline} {duration}\n"

    input_data += f"{len(dependencies)}\n"

    for dep in dependencies:
        input_data += f"{dep[0]} {dep[1]}\n"

    return input_data


@app.route("/")
def home():
    return "Task Scheduler API is running"


@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.get_json()

    tasks = data.get("tasks", [])
    dependencies = data.get("dependencies", [])

    if not tasks:
        return jsonify({"error": "No tasks received"}), 400

    input_data = build_input(tasks, dependencies)

    try:
        result = subprocess.run(
            [SCHEDULER_PATH, "--api"],
            input=input_data,
            text=True,
            capture_output=True
        )

        output = result.stdout.strip()

        if result.returncode != 0:
            return jsonify({
                "error": result.stderr
            }), 500

        if output.startswith("ERROR|CYCLE"):
            return jsonify({
                "error": "Circular dependency detected"
            }), 400

        schedule_result = []

        for line in output.splitlines():
            parts = line.split("|")

            if len(parts) == 5:
                schedule_result.append({
                    "id": int(parts[0]),
                    "name": parts[1],
                    "priority": int(parts[2]),
                    "deadline": int(parts[3]),
                    "duration": int(parts[4])
                })

        return jsonify({
            "schedule": schedule_result
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


@app.route("/critical-path", methods=["POST"])
def critical_path():
    data = request.get_json()

    tasks = data.get("tasks", [])
    dependencies = data.get("dependencies", [])

    if not tasks:
        return jsonify({"error": "No tasks received"}), 400

    input_data = build_input(tasks, dependencies)

    try:
        result = subprocess.run(
            [SCHEDULER_PATH, "--critical"],
            input=input_data,
            text=True,
            capture_output=True
        )

        output = result.stdout.strip()

        if result.returncode != 0:
            return jsonify({
                "error": result.stderr
            }), 500

        if output.startswith("ERROR|CYCLE"):
            return jsonify({
                "error": "Circular dependency detected"
            }), 400

        lines = output.splitlines()

        if not lines or not lines[0].startswith("TOTAL|"):
            return jsonify({
                "error": "Invalid critical path output",
                "cppOutput": output
            }), 500

        total_duration = int(
            lines[0].split("|")[1]
        )

        path = []

        for line in lines[1:]:
            parts = line.split("|")

            if len(parts) == 3:
                path.append({
                    "id": int(parts[0]),
                    "name": parts[1],
                    "duration": int(parts[2])
                })

        return jsonify({
            "totalDuration": total_duration,
            "path": path
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)