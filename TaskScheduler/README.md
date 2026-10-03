# Task Scheduler

A console task scheduler that orders tasks while respecting dependencies and priority, and reports circular dependencies clearly.

## Project Structure
```
TaskScheduler/
├── src/main.cpp        # scheduler implementation
├── examples/           # sample inputs (diamond DAG, cycle)
├── DECISIONS.md        # design decision + complexity
├── Makefile
├── .gitignore
└── README.md
```

## Features
- Create tasks with a priority and a deadline
- Declare dependencies between tasks
- Compute a valid completion order
- Detect circular dependencies and print the exact cycle path

## Build & Run
```
g++ -std=c++17 src/main.cpp -o ts     # or: make
./ts
```
Try the sample inputs:
```
./ts < examples/diamond.txt   # valid order + critical path
./ts < examples/cycle.txt     # circular dependency report
```
Menu: 1) Add task (name priority deadline duration)  2) Add dependency  3) Show schedule  4) Critical path  5) Exit

## Graph Representation
Directed graph stored as an adjacency list (`unordered_map<int, vector<int>>`).
An edge `A -> B` means *B depends on A* (A must finish first).
A separate `in-degree` map stores how many unfinished dependencies each task has.

## Algorithm
Kahn's algorithm (BFS topological sort) with a priority queue:
1. Push every task with in-degree 0 into a max-heap.
2. Heap order: higher priority first, then earlier deadline, then smaller id.
3. Pop the top task, add it to the order, decrement the in-degree of its dependents, and push any that reach 0.
4. If the final order has fewer tasks than the graph, a cycle exists. A DFS over the remaining nodes extracts the cycle path.

## Bonus: Critical Path
Each task has a duration. Processing tasks in topological order, `finish[v] = duration[v] + max(finish[u])` over all dependencies `u` of `v`, remembering the predecessor that gave the max. The task with the largest finish time is the end of the critical path; following predecessors back gives the full path. Time O(V + E).

## Complexity
- Time: O((V + E) log V)
- Space: O(V + E)

## Example
Design -> Code, Design -> Test, Code -> Deploy, Test -> Deploy
Output: Design, Code, Test, Deploy (Code runs before Test due to higher priority).
Adding Deploy -> Code gives: `Cycle: Code -> Deploy -> Code`.

## Design decision
See [DECISIONS.md](DECISIONS.md).
