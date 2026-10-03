# DECISIONS.md

## Decision: Kahn's Algorithm (BFS) with a Priority Queue instead of DFS-based Topological Sort

**Context:** The scheduler must produce a valid order that respects dependencies, and among tasks that are ready at the same time it must prefer higher priority, then earlier deadline.

**Options considered**
1. DFS-based topological sort (reverse post-order)
2. Kahn's algorithm with a plain queue
3. Kahn's algorithm with a priority queue (chosen)

**Why option 3**
- Kahn's keeps a "ready set" (tasks with in-degree 0). Replacing the plain queue with a max-heap lets us pick the best ready task at every step, so priority and deadline are respected *without* a separate sorting pass.
- DFS-based topo sort gives a valid order but has no natural place to apply priority; the order depends on DFS traversal order.
- Cycle detection comes free: if the output has fewer tasks than the graph, a cycle exists. The leftover nodes (in-degree > 0) are then used to extract the exact cycle path with a DFS.

**Trade-off:** The heap adds a log factor, so time is O((V + E) log V) instead of O(V + E). For a task scheduler this is acceptable.

**Complexity**
- Time: O((V + E) log V). Each task is pushed and popped from the heap once, and each edge is relaxed once.
- Space: O(V + E) for the adjacency list, in-degree map and heap.
