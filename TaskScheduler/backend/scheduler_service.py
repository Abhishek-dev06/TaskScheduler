"""Portable adapter for the original C++ scheduling engine."""

import hashlib
import logging
import os
from pathlib import Path
import shutil
import subprocess
import threading

PROJECT = Path(__file__).resolve().parents[1]
BUILD_LOCK = threading.Lock()
MAX_TASKS = 500
MAX_VALUE = 1_000_000


def validate(tasks, dependencies):
    if not isinstance(tasks, list) or not tasks:
        raise ValueError("Please add at least one task.")
    if len(tasks) > MAX_TASKS:
        raise ValueError(f"Use at most {MAX_TASKS} tasks.")
    clean = []
    for index, task in enumerate(tasks, 1):
        if not isinstance(task, dict):
            raise ValueError("Each task must be an object.")
        name = task.get("name", "")
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            raise ValueError("Task names must contain 1 to 120 characters.")
        if any(char in name for char in "\n\r|\x00"):
            raise ValueError("Task names cannot contain newlines or the | character.")
        row = {"id": index, "name": name.strip()}
        for field, default, minimum in (("priority", 1, 0), ("deadline", 10, 0), ("duration", 1, 1)):
            value = task.get(field, default)
            if type(value) is not int or not minimum <= value <= MAX_VALUE:
                raise ValueError(f"{field.capitalize()} must be an integer between {minimum} and {MAX_VALUE}.")
            row[field] = value
        clean.append(row)
    if not isinstance(dependencies, list) or len(dependencies) > MAX_TASKS * MAX_TASKS:
        raise ValueError("Dependencies must be a list of task ID pairs.")
    edges = []
    seen = set()
    for edge in dependencies:
        if not isinstance(edge, (list, tuple)) or len(edge) != 2:
            raise ValueError("Each dependency must contain two task IDs.")
        a, b = edge
        if any(type(i) is not int or not 1 <= i <= len(clean) for i in edge):
            raise ValueError("Dependency task ID does not exist.")
        if a == b:
            raise ValueError("A task cannot depend on itself.")
        if (a, b) not in seen:
            edges.append((a, b))
            seen.add((a, b))
    return clean, edges


def build_input(tasks, dependencies):
    tasks, dependencies = validate(tasks, dependencies)
    lines = [str(len(tasks))]
    for task in tasks:
        lines.extend([task["name"], f'{task["priority"]} {task["deadline"]} {task["duration"]}'])
    lines.append(str(len(dependencies)))
    lines.extend(f"{a} {b}" for a, b in dependencies)
    return "\n".join(lines) + "\n"


def scheduler_binary():
    source = PROJECT / "src" / "main.cpp"
    digest = hashlib.sha256(source.read_bytes()).hexdigest()[:16]
    build = PROJECT / ".build"
    binary = build / (f"scheduler-{digest}" + (".exe" if os.name == "nt" else ""))
    with BUILD_LOCK:
        if binary.exists():
            return binary
        compiler = shutil.which("g++")
        if compiler is None:
            raise RuntimeError("C++ compiler unavailable. Install g++ (packages.txt on Streamlit Cloud).")
        build.mkdir(exist_ok=True)
        result = subprocess.run(
            [compiler, "-std=c++17", "-O2", str(source), "-o", str(binary)],
            capture_output=True, text=True, encoding="utf-8", timeout=120,
        )
        if result.returncode:
            logging.error("Scheduler build failed: %s", result.stderr)
            raise RuntimeError("Scheduler build failed. Check the server logs.")
    return binary


def run_scheduler(tasks, dependencies, mode="schedule"):
    if mode not in ("schedule", "critical"):
        raise ValueError("Unknown scheduler mode.")
    input_data = build_input(tasks, dependencies)
    try:
        result = subprocess.run(
            [str(scheduler_binary()), "--api" if mode == "schedule" else "--critical"],
            input=input_data, capture_output=True, text=True, encoding="utf-8", timeout=10,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Scheduler timed out. Please try a smaller task list.") from exc
    if result.returncode:
        logging.error("Scheduler execution failed: %s", result.stderr)
        raise RuntimeError("Scheduler execution failed. Check the server logs.")
    lines = result.stdout.strip().splitlines()
    if lines and lines[0] == "ERROR|CYCLE":
        raise ValueError("Circular dependency detected. Remove a dependency to break the cycle.")
    if mode == "critical":
        if not lines or not lines[0].startswith("TOTAL|"):
            raise RuntimeError("Invalid critical path output.")
        path = []
        for line in lines[1:]:
            task_id, name, duration = line.split("|")
            path.append({"id": int(task_id), "name": name, "duration": int(duration)})
        return {"totalDuration": int(lines[0].split("|")[1]), "path": path}
    schedule = []
    for line in lines:
        task_id, name, priority, deadline, duration = line.split("|")
        schedule.append(dict(id=int(task_id), name=name, priority=int(priority), deadline=int(deadline), duration=int(duration)))
    if len(schedule) != len(tasks):
        raise RuntimeError("Invalid schedule output.")
    return {"schedule": schedule}
