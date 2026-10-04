let tasks = [];
let dependencies = [];

function addTask() {
    const name = document.getElementById("taskName").value.trim();
    const priority = document.getElementById("priority").value;
    const deadline = document.getElementById("deadline").value;
    const duration = document.getElementById("duration").value;

    if (
        name === "" ||
        priority === "" ||
        deadline === "" ||
        duration === ""
    ) {
        alert("Please fill all task fields.");
        return;
    }

    const task = {
        id: tasks.length + 1,
        name: name,
        priority: Number(priority),
        deadline: Number(deadline),
        duration: Number(duration)
    };

    tasks.push(task);

    displayTasks();

    document.getElementById("taskName").value = "";
    document.getElementById("priority").value = "";
    document.getElementById("deadline").value = "";
    document.getElementById("duration").value = "";
}


function displayTasks() {
    const taskList = document.getElementById("taskList");

    taskList.innerHTML = "";

    tasks.forEach((task) => {
        const li = document.createElement("li");

        li.innerText =
            `ID ${task.id} | ${task.name} | Priority: ${task.priority} | Deadline: ${task.deadline} | Duration: ${task.duration}`;

        taskList.appendChild(li);
    });
}


function addDependency() {
    const from = Number(
        document.getElementById("fromTask").value
    );

    const to = Number(
        document.getElementById("toTask").value
    );

    if (!from || !to) {
        alert("Enter valid task IDs.");
        return;
    }

    if (from === to) {
        alert("Task cannot depend on itself.");
        return;
    }

    if (
        from > tasks.length ||
        to > tasks.length
    ) {
        alert("Task ID does not exist.");
        return;
    }

    dependencies.push([from, to]);

    displayDependencies();

    document.getElementById("fromTask").value = "";
    document.getElementById("toTask").value = "";
}


function displayDependencies() {
    const list =
        document.getElementById("dependencyList");

    list.innerHTML = "";

    dependencies.forEach((dep) => {
        const li = document.createElement("li");

        li.innerText =
            `Task ${dep[1]} depends on Task ${dep[0]}`;

        list.appendChild(li);
    });
}


async function scheduleTasks() {
    const result =
        document.getElementById("result");

    if (tasks.length === 0) {
        result.innerText =
            "Please add some tasks first.";
        return;
    }

    result.innerText =
        "Generating schedule...";

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/schedule",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    tasks: tasks,
                    dependencies: dependencies
                })
            }
        );

        const data =
            await response.json();

        if (!response.ok) {
            result.innerText =
                data.error || "Server error.";
            return;
        }

        let output = "";

        data.schedule.forEach(
            (task, index) => {

                output +=
                    `${index + 1}. ${task.name}` +
                    ` | Priority: ${task.priority}` +
                    ` | Deadline: ${task.deadline}` +
                    ` | Duration: ${task.duration}\n`;
            }
        );

        result.innerText = output;

    } catch (error) {

        console.error(error);

        result.innerText =
            "Backend connection failed.";
    }
}
async function findCriticalPath() {
    const result = document.getElementById("result");

    if (tasks.length === 0) {
        result.innerText = "Please add some tasks first.";
        return;
    }

    result.innerText = "Calculating critical path...";

    try {
        const response = await fetch(
            "http://127.0.0.1:5000/critical-path",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    tasks: tasks,
                    dependencies: dependencies
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            result.innerText =
                data.error || "Server error.";
            return;
        }

        let output =
            `Critical Path\nTotal Duration: ${data.totalDuration}\n\n`;

        data.path.forEach((task, index) => {
            output +=
                `${index + 1}. ${task.name} (Duration: ${task.duration})\n`;
        });

        result.innerText = output;

    } catch (error) {
        console.error(error);

        result.innerText =
            "Backend connection failed.";
    }
}