from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "TaskScheduler" / "backend"
sys.path.insert(0, str(BACKEND))
from scheduler_service import run_scheduler

TASKS = [
    dict(name="Design", priority=5, deadline=3, duration=2),
    dict(name="Code", priority=4, deadline=8, duration=4),
    dict(name="Test", priority=3, deadline=8, duration=3),
    dict(name="Deploy", priority=2, deadline=10, duration=1),
]
EDGES = [(1, 2), (1, 3), (2, 4), (3, 4)]


class EngineTests(unittest.TestCase):
    def test_diamond_schedule_and_critical_path(self):
        order = run_scheduler(TASKS, EDGES)["schedule"]
        self.assertEqual([task["name"] for task in order], ["Design", "Code", "Test", "Deploy"])
        result = run_scheduler(TASKS, EDGES, "critical")
        self.assertEqual(result["totalDuration"], 7)
        self.assertEqual([task["name"] for task in result["path"]], ["Design", "Code", "Deploy"])

    def test_cycle_rejected_in_both_modes(self):
        for mode in ("schedule", "critical"):
            with self.subTest(mode=mode), self.assertRaisesRegex(ValueError, "Circular dependency"):
                run_scheduler(TASKS, EDGES + [(4, 2)], mode)

    def test_priority_deadline_and_id_tiebreakers(self):
        tasks = [dict(name=str(i), priority=p, deadline=d, duration=1)
                 for i, p, d in [(1, 1, 1), (2, 3, 5), (3, 3, 2), (4, 3, 2)]]
        self.assertEqual([t["id"] for t in run_scheduler(tasks, [])["schedule"]], [3, 4, 2, 1])

    def test_invalid_input(self):
        for tasks, edges in [([], []), (TASKS, [(1, 9)]), (TASKS, [(1, 1)]),
                             ([dict(name="Bad|name")], []), ([dict(name="Bad\nname")], []),
                             ([dict(name="Bad", duration=-1)], []), (TASKS, "invalid")]:
            with self.subTest(tasks=tasks, edges=edges), self.assertRaises(ValueError):
                run_scheduler(tasks, edges)

    def test_duplicate_dependencies_and_unicode(self):
        result = run_scheduler(TASKS, EDGES + EDGES)
        self.assertEqual(len(result["schedule"]), 4)
        self.assertEqual(run_scheduler([dict(name="कार्य / café")], [])["schedule"][0]["name"], "कार्य / café")


class FlaskTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("flask_entry", BACKEND / "app.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.client = module.app.test_client()

    def test_frontend_and_assets(self):
        for route in ("/", "/static/style.css", "/static/script.js"):
            with self.subTest(route=route), self.client.get(route) as response:
                self.assertEqual(response.status_code, 200)

    def test_api(self):
        payload = dict(tasks=TASKS, dependencies=EDGES)
        self.assertEqual(len(self.client.post("/schedule", json=payload).json["schedule"]), 4)
        self.assertEqual(self.client.post("/critical-path", json=payload).json["totalDuration"], 7)
        for payload in (None, [], {}, dict(tasks=TASKS, dependencies=EDGES + [(4, 2)])):
            with self.subTest(payload=payload):
                self.assertEqual(self.client.post("/schedule", json=payload).status_code, 400)


class StreamlitTests(unittest.TestCase):
    def test_add_tasks_dependencies_and_clear(self):
        from streamlit.testing.v1 import AppTest
        app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
        for name in ("First", "Second"):
            app.text_input[0].set_value(name)
            next(b for b in app.button if b.label == "Add Task").click().run()
        next(b for b in app.button if b.label == "Add Dependency").click().run()
        next(b for b in app.button if b.label == "Generate Schedule").click().run()
        self.assertFalse(app.exception)
        self.assertEqual([t["name"] for t in app.session_state.result["schedule"]], ["First", "Second"])
        next(b for b in app.button if b.label == "Remove").click().run()
        self.assertFalse(app.session_state.dependencies)
        self.assertNotIn("result", app.session_state)
        next(b for b in app.button if b.label == "Clear all").click().run()
        self.assertFalse(app.session_state.tasks)

    def test_all_entrypoints(self):
        from streamlit.testing.v1 import AppTest
        for path in (ROOT / "streamlit_app.py", BACKEND / "app.py", ROOT / "backend" / "app.py"):
            with self.subTest(path=path):
                app = AppTest.from_file(str(path), default_timeout=30).run()
                self.assertFalse(app.exception)
                self.assertEqual(app.title[0].value, "Task Scheduler")
                next(b for b in app.button if b.label == "Load example").click().run()
                next(b for b in app.button if b.label == "Generate Schedule").click().run()
                self.assertFalse(app.exception)
                self.assertFalse(app.error)
                self.assertEqual(len(app.session_state.result["schedule"]), 4)
                next(b for b in app.button if b.label == "Find Critical Path").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(app.metric[0].value, "7")
                app.session_state.dependencies.append((4, 2))
                next(b for b in app.button if b.label == "Generate Schedule").click().run()
                self.assertIn("Circular dependency", app.error[0].value)
                self.assertNotIn("result", app.session_state)


if __name__ == "__main__":
    unittest.main()
