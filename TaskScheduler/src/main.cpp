#include <bits/stdc++.h>
using namespace std;

struct Task {
    int id;
    string name;
    int priority;
    int deadline;
    int duration;
};

struct Cmp {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority)
            return a.priority < b.priority;

        if (a.deadline != b.deadline)
            return a.deadline > b.deadline;

        return a.id > b.id;
    }
};

class Scheduler {
    unordered_map<int, Task> tasks;
    unordered_map<int, vector<int>> adj;
    unordered_map<int, int> indeg;

    int nextId = 1;

    bool dfs(
        int u,
        unordered_map<int, int>& state,
        vector<int>& path,
        const unordered_set<int>& stuck,
        vector<int>& cycle
    ) {
        state[u] = 1;
        path.push_back(u);

        for (int v : adj[u]) {

            if (!stuck.count(v))
                continue;

            if (state[v] == 1) {

                auto it = find(
                    path.begin(),
                    path.end(),
                    v
                );

                cycle.assign(it, path.end());
                cycle.push_back(v);

                return true;
            }

            if (
                state[v] == 0 &&
                dfs(v, state, path, stuck, cycle)
            )
                return true;
        }

        path.pop_back();
        state[u] = 2;

        return false;
    }

public:

    int addTask(
        const string& name,
        int priority,
        int deadline,
        int duration = 1
    ) {
        int id = nextId++;

        tasks[id] = {
            id,
            name,
            priority,
            deadline,
            duration
        };

        indeg[id] = 0;

        return id;
    }

    bool addDependency(int a, int b) {

        if (!tasks.count(a) || !tasks.count(b))
            return false;

        if (a == b)
            return false;

        if (
            find(
                adj[a].begin(),
                adj[a].end(),
                b
            ) != adj[a].end()
        )
            return false;

        adj[a].push_back(b);

        indeg[b]++;

        return true;
    }

    bool schedule(
        vector<int>& order,
        vector<int>& cycle
    ) {

        order.clear();
        cycle.clear();

        auto deg = indeg;

        priority_queue<
            Task,
            vector<Task>,
            Cmp
        > pq;

        for (auto& [id, task] : tasks) {

            if (deg[id] == 0)
                pq.push(task);
        }

        while (!pq.empty()) {

            Task current = pq.top();
            pq.pop();

            order.push_back(current.id);

            for (int v : adj[current.id]) {

                deg[v]--;

                if (deg[v] == 0)
                    pq.push(tasks[v]);
            }
        }

        if (order.size() == tasks.size())
            return true;

        unordered_set<int> stuck;

        for (auto& [id, d] : deg) {

            if (d > 0)
                stuck.insert(id);
        }

        unordered_map<int, int> state;
        vector<int> path;

        for (int s : stuck) {

            if (
                state[s] == 0 &&
                dfs(
                    s,
                    state,
                    path,
                    stuck,
                    cycle
                )
            )
                break;
        }

        return false;
    }

    Task getTask(int id) {
        return tasks[id];
    }

    bool getCriticalPath(vector<int>& path, int& totalDuration) {
    vector<int> order, cycle;

    if (!schedule(order, cycle))
        return false;

    if (order.empty()) {
        totalDuration = 0;
        return true;
    }

    unordered_map<int, int> best;
    unordered_map<int, int> finish;
    unordered_map<int, int> pred;

    for (int u : order) {

        finish[u] =
            best[u] + tasks[u].duration;

        for (int v : adj[u]) {

            if (finish[u] > best[v]) {

                best[v] = finish[u];
                pred[v] = u;
            }
        }
    }

    int end = order[0];

    for (int u : order) {

        if (finish[u] > finish[end])
            end = u;
    }

    totalDuration = finish[end];

    path.clear();

    int current = end;

    while (true) {

        path.push_back(current);

        if (!pred.count(current))
            break;

        current = pred[current];
    }

    reverse(path.begin(), path.end());

    return true;
}

    void printOrder(
        const vector<int>& order
    ) {

        cout << "\nValid execution order:\n";

        for (
            size_t i = 0;
            i < order.size();
            i++
        ) {

            Task t = tasks[order[i]];

            cout
                << i + 1
                << ". "
                << t.name
                << " (priority="
                << t.priority
                << ", deadline="
                << t.deadline
                << ", duration="
                << t.duration
                << ")\n";
        }
    }
};


// =============================
// API MODE
// =============================

void apiMode() {

    Scheduler scheduler;

    int n;

    cin >> n;
    cin.ignore();

    /*
       Input format:

       number of tasks

       taskName
       priority deadline duration

       Example:

       3
       Study
       3 5 2
       Project
       5 2 4
       Gym
       1 10 1
    */

    for (int i = 0; i < n; i++) {

        string name;

        getline(cin, name);

        int priority;
        int deadline;
        int duration;

        cin
            >> priority
            >> deadline
            >> duration;

        cin.ignore();

        scheduler.addTask(
            name,
            priority,
            deadline,
            duration
        );
    }

    // Dependencies

    int dependencyCount;

    cin >> dependencyCount;

    for (
        int i = 0;
        i < dependencyCount;
        i++
    ) {

        int a, b;

        cin >> a >> b;

        scheduler.addDependency(a, b);
    }

    vector<int> order;
    vector<int> cycle;

    bool valid =
        scheduler.schedule(
            order,
            cycle
        );

    if (!valid) {

        cout << "ERROR|CYCLE\n";

        return;
    }

    // Output machine-readable format

    for (int id : order) {

        Task t =
            scheduler.getTask(id);

        cout
            << t.id << "|"
            << t.name << "|"
            << t.priority << "|"
            << t.deadline << "|"
            << t.duration
            << "\n";
    }
}

void criticalApiMode() {

    Scheduler scheduler;

    int n;
    cin >> n;
    cin.ignore();

    for (int i = 0; i < n; i++) {

        string name;

        getline(cin, name);

        int priority;
        int deadline;
        int duration;

        cin >> priority >> deadline >> duration;
        cin.ignore();

        scheduler.addTask(
            name,
            priority,
            deadline,
            duration
        );
    }

    int dependencyCount;

    cin >> dependencyCount;

    for (int i = 0; i < dependencyCount; i++) {

        int a, b;

        cin >> a >> b;

        scheduler.addDependency(a, b);
    }

    vector<int> path;
    int totalDuration = 0;

    if (!scheduler.getCriticalPath(
            path,
            totalDuration
        )) {

        cout << "ERROR|CYCLE\n";
        return;
    }

    cout
        << "TOTAL|"
        << totalDuration
        << "\n";

    for (int id : path) {

        Task t =
            scheduler.getTask(id);

        cout
            << t.id << "|"
            << t.name << "|"
            << t.duration
            << "\n";
    }
}

// =============================
// NORMAL TERMINAL MODE
// =============================

void normalMode() {

    Scheduler scheduler;

    while (true) {

        cout
            << "\n1. Add task"
            << "\n2. Add dependency"
            << "\n3. Show schedule"
            << "\n4. Exit"
            << "\nChoice: ";

        int choice;

        cin >> choice;

        if (choice == 4)
            break;

        if (choice == 1) {

            string name;

            int priority;
            int deadline;
            int duration;

            cout
                << "Name priority deadline duration: ";

            cin
                >> name
                >> priority
                >> deadline
                >> duration;

            int id =
                scheduler.addTask(
                    name,
                    priority,
                    deadline,
                    duration
                );

            cout
                << "Task added with id "
                << id
                << "\n";
        }

        else if (choice == 2) {

            int a, b;

            cout
                << "a b (b depends on a): ";

            cin >> a >> b;

            if (
                scheduler.addDependency(
                    a,
                    b
                )
            )
                cout
                    << "Dependency added\n";

            else
                cout
                    << "Invalid dependency\n";
        }

        else if (choice == 3) {

            vector<int> order;
            vector<int> cycle;

            if (
                scheduler.schedule(
                    order,
                    cycle
                )
            ) {

                scheduler.printOrder(order);

            } else {

                cout
                    << "Circular dependency detected!\n";
            }
        }
    }
}


// =============================
// MAIN
// =============================

int main(int argc, char* argv[]) {

    if (argc > 1) {

        string mode = argv[1];

        if (mode == "--api") {

            apiMode();
            return 0;
        }

        if (mode == "--critical") {

            criticalApiMode();
            return 0;
        }
    }

    normalMode();

    return 0;
}