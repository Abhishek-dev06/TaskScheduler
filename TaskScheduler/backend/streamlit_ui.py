"""Streamlit interface; task data is isolated to each browser session."""

import streamlit as st
from scheduler_service import MAX_TASKS, MAX_VALUE, run_scheduler, validate


def render():
    st.set_page_config(page_title="Task Scheduler", page_icon="📋", layout="wide")
    st.title("Task Scheduler")
    st.caption("Topological sort + priority queue · Powered by the original C++ engine")
    st.session_state.setdefault("tasks", [])
    st.session_state.setdefault("dependencies", [])
    tasks = st.session_state.tasks
    dependencies = st.session_state.dependencies

    with st.sidebar:
        st.header("Get started")
        st.write("Add tasks, connect their dependencies, then generate a schedule or find the critical path.")
        st.caption("Higher priority runs first. Ties use the earliest deadline, then task ID. Use the same time unit for deadlines and durations.")
        if st.button("Load example", width="stretch"):
            st.session_state.tasks = [
                dict(id=1, name="Design", priority=5, deadline=3, duration=2),
                dict(id=2, name="Code", priority=4, deadline=8, duration=4),
                dict(id=3, name="Test", priority=3, deadline=8, duration=3),
                dict(id=4, name="Deploy", priority=2, deadline=10, duration=1),
            ]
            st.session_state.dependencies = [(1, 2), (1, 3), (2, 4), (3, 4)]
            st.session_state.pop("result", None)
            st.rerun()
        if st.button("Clear all", width="stretch"):
            st.session_state.tasks = []
            st.session_state.dependencies = []
            st.session_state.pop("result", None)
            st.rerun()
        st.caption("Tasks stay in this browser session only. Reloading or reconnecting may clear them.")

    st.subheader("Add task")
    with st.form("new_task", clear_on_submit=True):
        name = st.text_input("Task name", max_chars=120)
        c1, c2, c3 = st.columns(3)
        priority = c1.number_input("Priority", min_value=0, max_value=MAX_VALUE, value=1)
        deadline = c2.number_input("Deadline", min_value=0, max_value=MAX_VALUE, value=10)
        duration = c3.number_input("Duration", min_value=1, max_value=MAX_VALUE, value=1)
        if st.form_submit_button("Add Task", disabled=len(tasks) >= MAX_TASKS):
            candidate = dict(id=len(tasks) + 1, name=name, priority=priority, deadline=deadline, duration=duration)
            try:
                validate([candidate], [])
            except ValueError as exc:
                st.error(str(exc))
            else:
                tasks.append(candidate)
                st.session_state.pop("result", None)
                st.rerun()

    left, right = st.columns([3, 2])
    with left:
        st.subheader(f"Tasks ({len(tasks)})")
        if tasks:
            st.dataframe(tasks, hide_index=True, width="stretch")
        else:
            st.info("Add your first task or load the example from the sidebar.")
    with right:
        st.subheader("Dependencies")
        if len(tasks) >= 2:
            ids = [task["id"] for task in tasks]
            labels = {task["id"]: f'{task["id"]}: {task["name"]}' for task in tasks}
            with st.form("new_dependency"):
                first = st.selectbox("Prerequisite (runs first)", ids, format_func=labels.get)
                second = st.selectbox("Dependent task (runs after)", ids, index=1, format_func=labels.get)
                if st.form_submit_button("Add Dependency"):
                    if first == second:
                        st.error("A task cannot depend on itself.")
                    elif (first, second) in dependencies:
                        st.warning("This dependency already exists.")
                    else:
                        dependencies.append((first, second))
                        st.session_state.pop("result", None)
                        st.rerun()
            for index, (first, second) in enumerate(dependencies):
                label, action = st.columns([4, 1])
                label.write(f"{labels[first]} → {labels[second]}")
                if action.button("Remove", key=f"remove_{index}"):
                    dependencies.pop(index)
                    st.session_state.pop("result", None)
                    st.rerun()
        else:
            st.caption("Add at least two tasks to create dependencies.")

    c1, c2 = st.columns(2)
    schedule = c1.button("Generate Schedule", type="primary", disabled=not tasks, width="stretch")
    critical = c2.button("Find Critical Path", disabled=not tasks, width="stretch")
    if schedule or critical:
        st.session_state.pop("result", None)
        try:
            with st.spinner("Running C++ scheduler…"):
                st.session_state.result = run_scheduler(tasks, dependencies, "schedule" if schedule else "critical")
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
    result = st.session_state.get("result")
    if result:
        if "schedule" in result:
            st.subheader("Scheduled order")
            st.dataframe([{"order": index, **task} for index, task in enumerate(result["schedule"], 1)], hide_index=True, width="stretch")
        else:
            st.subheader("Critical path")
            st.metric("Total duration", result["totalDuration"])
            st.write(" → ".join(task["name"] for task in result["path"]))
            st.dataframe(result["path"], hide_index=True, width="stretch")
            st.caption("Longest dependency chain, assuming independent tasks can run in parallel.")
