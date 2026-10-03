#include <bits/stdc++.h>
using namespace std;

struct Task {
    int id;
    string name;
    int priority;  // bada number = zyada important
    int deadline;  // chhota number = jaldi deadline
    int duration;  // task ko kitna time lagega (critical path ke liye)
};

// priority_queue me "top" wo hoga jo comparator ke hisaab se sabse bada ho
struct Cmp {
    bool operator()(const Task& a, const Task& b) const {
        if (a.priority != b.priority) return a.priority < b.priority;  // high priority pehle
        if (a.deadline != b.deadline) return a.deadline > b.deadline;  // tie: jaldi deadline pehle
        return a.id > b.id;                                            // tie: chhota id pehle
    }
};

class Scheduler {
    unordered_map<int, Task> tasks;
    unordered_map<int, vector<int>> adj;  // a -> b  matlab b, a pe depend karta hai
    unordered_map<int, int> indeg;
    int nextId = 1;

    // DFS se exact cycle path nikalna (sirf stuck nodes pe)
    bool dfs(int u, unordered_map<int, int>& state, vector<int>& path,
             const unordered_set<int>& stuck, vector<int>& cycle) {
        state[u] = 1;  // visiting
        path.push_back(u);
        for (int v : adj[u]) {
            if (!stuck.count(v)) continue;
            if (state[v] == 1) {  // back edge => cycle mili
                auto it = find(path.begin(), path.end(), v);
                cycle.assign(it, path.end());
                cycle.push_back(v);
                return true;
            }
            if (state[v] == 0 && dfs(v, state, path, stuck, cycle)) return true;
        }
        path.pop_back();
        state[u] = 2;  // done
        return false;
    }

public:
    int addTask(const string& name, int priority, int deadline, int duration = 1) {
        int id = nextId++;
        tasks[id] = {id, name, priority, deadline, duration};
        indeg[id] = 0;
        return id;
    }

    // b, a pe depend karta hai (a pehle complete hona chahiye)
    bool addDependency(int a, int b) {
        if (!tasks.count(a) || !tasks.count(b)) { cout << "Invalid task id\n"; return false; }
        if (a == b) { cout << "Task khud pe depend nahi kar sakta\n"; return false; }
        if (find(adj[a].begin(), adj[a].end(), b) != adj[a].end()) { cout << "Dependency already exists\n"; return false; }
        adj[a].push_back(b);
        indeg[b]++;
        return true;
    }

    // Kahn's algorithm + priority queue
    // true => valid order mila; false => cycle, 'cycle' me path hai
    bool schedule(vector<int>& order, vector<int>& cycle) {
        order.clear();
        cycle.clear();
        auto deg = indeg;  // copy, taaki original safe rahe
        priority_queue<Task, vector<Task>, Cmp> pq;
        for (auto& [id, t] : tasks)
            if (deg[id] == 0) pq.push(t);

        while (!pq.empty()) {
            Task cur = pq.top();
            pq.pop();
            order.push_back(cur.id);
            for (int v : adj[cur.id])
                if (--deg[v] == 0) pq.push(tasks[v]);
        }

        if (order.size() == tasks.size()) return true;

        // cycle hai: bache hue nodes (deg > 0) me se exact path nikalo
        unordered_set<int> stuck;
        for (auto& [id, d] : deg)
            if (d > 0) stuck.insert(id);
        unordered_map<int, int> state;
        vector<int> path;
        for (int s : stuck)
            if (state[s] == 0 && dfs(s, state, path, stuck, cycle)) break;
        return false;
    }


    // BONUS: Critical path = DAG me sabse lamba (duration ke hisaab se) path
    void criticalPath() {
        vector<int> order, cycle;
        if (!schedule(order, cycle)) { printCycle(cycle); return; }
        if (order.empty()) { cout << "Koi task nahi hai\n"; return; }

        unordered_map<int, int> best, finish, pred;  // best[v] = preds ka max finish time
        for (int u : order) {
            finish[u] = best[u] + tasks[u].duration;
            for (int v : adj[u])
                if (finish[u] > best[v]) { best[v] = finish[u]; pred[v] = u; }
        }
        int end = order[0];
        for (int u : order)
            if (finish[u] > finish[end]) end = u;

        vector<int> path;
        for (int u = end;; u = pred[u]) {
            path.push_back(u);
            if (!pred.count(u)) break;
        }
        reverse(path.begin(), path.end());

        cout << "\nCritical path (total duration = " << finish[end] << "):\n";
        for (size_t i = 0; i < path.size(); i++) {
            cout << tasks[path[i]].name << "(" << tasks[path[i]].duration << ")";
            if (i + 1 < path.size()) cout << " -> ";
        }
        cout << "\n";
    }

    void printOrder(const vector<int>& order) {
        cout << "\nValid execution order:\n";
        for (size_t i = 0; i < order.size(); i++) {
            const Task& t = tasks[order[i]];
            cout << i + 1 << ". " << t.name << " (id=" << t.id << ", priority=" << t.priority
                 << ", deadline=" << t.deadline << ", duration=" << t.duration << ")\n";
        }
    }

    void printCycle(const vector<int>& cycle) {
        cout << "\nCircular dependency detected! Schedule nahi ban sakta.\nCycle: ";
        for (size_t i = 0; i < cycle.size(); i++) {
            cout << tasks[cycle[i]].name;
            if (i + 1 < cycle.size()) cout << " -> ";
        }
        cout << "\n";
    }
};

int main() {
    Scheduler s;
    while (true) {
        cout << "\n1. Add task\n2. Add dependency\n3. Show schedule\n4. Critical path\n5. Exit\nChoice: ";
        int ch;
        if (!(cin >> ch) || ch == 5) break;

        if (ch == 1) {
            string name; int p, d;
            int dur;
            cout << "Name priority deadline duration: ";
            cin >> name >> p >> d >> dur;
            cout << "Task added with id " << s.addTask(name, p, d, dur) << "\n";
        } else if (ch == 2) {
            int a, b;
            cout << "Pehle kaun (a) , phir kaun (b depends on a): ";
            cin >> a >> b;
            if (s.addDependency(a, b)) cout << "Dependency added\n";
        } else if (ch == 3) {
            vector<int> order, cycle;
            if (s.schedule(order, cycle)) s.printOrder(order);
            else s.printCycle(cycle);
        } else if (ch == 4) {
            s.criticalPath();
        }
    }
    return 0;
}
