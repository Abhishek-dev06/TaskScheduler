from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "Task Scheduler API is running"

@app.route("/critical-path", methods=["POST"])
@app.route("/schedule", methods=["POST"])
def schedule():
    data = request.get_json()
    tasks = data.get("tasks", [])

    if not tasks:
        return jsonify({"error": "No tasks received"}), 400

    tasks = sorted(
        tasks,
        key=lambda x: x["priority"],
        reverse=True
    )

    return jsonify({"schedule": tasks})

if __name__ == "__main__":
    app.run(debug=True, port=5000)