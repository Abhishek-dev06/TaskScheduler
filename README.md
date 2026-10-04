# Task Scheduler

A dependency-aware task scheduler powered by **C++17**, with a Streamlit web app
and an optional Flask API. Uses Kahn's topological sort and a priority queue;
higher priority comes first, then earlier deadline, then smaller task ID.

**Live app:** https://taskscheduler-yxgboyfh4g72fzvkqecr3t.streamlit.app/

## Features

- Add tasks with priority, deadline and duration.
- Connect prerequisites and dependent tasks.
- Generate a valid execution order and detect circular dependencies.
- Calculate the critical path and its total duration.
- Load a working diamond-graph example.

## Run locally

Requires Python 3.11+ and `g++` on PATH.

```sh
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

The original C++ source is compiled on first use. The binary is cached in
`TaskScheduler/.build/`, with a new build whenever the source changes. There is
no Windows-specific executable path and no external API server to deploy for
the Streamlit version. Tasks are kept in each browser session, not a database.

## Streamlit Community Cloud

- Repository: `Abhishek-dev06/TaskScheduler`
- Branch: `main`
- Main file: `streamlit_app.py` for new deployments.
- The existing `TaskScheduler/backend/app.py` entrypoint remains supported, so
  the current app can redeploy without changing its URL or settings.
- `requirements.txt` declares the Python dependencies; `packages.txt` installs
  the Linux C++ compiler. No secrets are required.

The earlier deployment ran a Flask-only script under Streamlit, omitted Python
dependencies and referenced a local Windows executable. The cloud entrypoint
now renders a Streamlit interface and invokes the portable C++ adapter directly.

## Optional Flask frontend/API

```sh
python TaskScheduler/backend/app.py
```

Open `http://127.0.0.1:5000`. Flask serves the existing HTML/CSS/JavaScript frontend
and exposes `POST /schedule` and `POST /critical-path`. Open the frontend through
Flask rather than directly as a file; requests now use the same origin.
The legacy `python backend/app.py` command works too.

## Tests

```sh
python -m unittest discover -s tests -v
```

Tests invoke the real C++ engine, exercise Flask error handling and use
Streamlit AppTest to cover all supported entrypoints and the example workflow.

See [the C++ project](TaskScheduler/README.md) for algorithm details.
