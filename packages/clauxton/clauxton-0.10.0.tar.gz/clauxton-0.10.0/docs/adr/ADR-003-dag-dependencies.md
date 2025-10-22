# ADR-003: DAG for Task Dependencies

**Status**: Accepted
**Date**: 2025-01-25
**Deciders**: Clauxton Core Team

## Context

Clauxton tasks often have dependencies (Task B depends on Task A). Users need:
1. **Dependency Tracking**: Know which tasks must be completed first
2. **Cycle Detection**: Prevent circular dependencies (A → B → A)
3. **Execution Order**: Get tasks in safe execution order
4. **Auto-Inference**: Automatically infer dependencies from file overlap

## Decision

Model task dependencies as a **Directed Acyclic Graph (DAG)** with:
- **Nodes**: Tasks
- **Edges**: Dependencies (A → B means "B depends on A")
- **Constraint**: No cycles allowed (enforced by validation)

```python
class TaskManager:
    def add(self, task: Task) -> str:
        # Validate no cycles
        if self._creates_cycle(task):
            raise CycleDetectedError()

        # Add to graph
        self.graph.add_node(task.id)
        for dep in task.depends_on:
            self.graph.add_edge(dep, task.id)
```

## Consequences

### Positive

1. **Cycle Prevention**:
   - Impossible to create circular dependencies
   - Validation at task creation time
   - Clear error messages

2. **Execution Order**:
   - Topological sort provides safe order
   - Multiple valid orders possible (non-deterministic dependencies)
   - `task_next()` returns best next task

3. **Auto-Inference**:
   - Infer dependencies from file overlap
   - If Task A edits `api.py` and Task B edits `api.py`, B depends on A
   - Reduces manual dependency management

4. **Visualization**:
   - DAG can be visualized (future feature)
   - Easy to understand task relationships

5. **Parallel Execution**:
   - Independent tasks can run in parallel
   - DAG makes parallelism explicit

### Negative

1. **Complexity**:
   - More complex than simple list of tasks
   - Requires cycle detection algorithm (DFS)

2. **Over-Inference**:
   - Auto-inferred dependencies may be too strict
   - Manual override sometimes needed
   - **Mitigation**: Users can specify `depends_on=[]` explicitly

3. **Rigidity**:
   - Can't have circular dependencies (even if intentional)
   - Some workflows may be awkward to model

4. **Performance**:
   - Cycle detection is O(V + E) per task add
   - Topological sort is O(V + E) per search
   - **Mitigation**: Acceptable for <1,000 tasks

## Alternatives Considered

### 1. Simple Task List (No Dependencies)

**Pros**:
- Simplest implementation
- No complexity

**Cons**:
- Users must manually track order
- Easy to forget dependencies
- No validation

**Why Rejected**: Too simple, doesn't solve dependency problem.

### 2. Priority-Only Ordering

**Pros**:
- Simple to implement
- Users understand priority

**Cons**:
- Doesn't model dependencies (just ordering hint)
- Can't detect conflicts
- No auto-inference

**Why Rejected**: Priority ≠ dependency.

### 3. Allow Cycles (Warn Only)

**Pros**:
- More flexible
- Handles edge cases

**Cons**:
- Topological sort undefined
- Execution order ambiguous
- Easy to create deadlocks

**Why Rejected**: Cycles are almost always errors.

### 4. Petri Nets / State Machines

**Pros**:
- More expressive (parallel execution, joins, forks)
- Better for complex workflows

**Cons**:
- Significantly more complex
- Overkill for task management
- Users need to learn Petri nets

**Why Rejected**: Too complex for current needs.

### 5. Makefile-style Dependencies

**Pros**:
- Well-known pattern (Make, Bazel)
- File-based dependencies

**Cons**:
- Requires file timestamps
- Doesn't handle non-file tasks
- More complex semantics

**Why Rejected**: Not all tasks produce files.

## Implementation Notes

### Cycle Detection (DFS)

```python
def _creates_cycle(self, new_task: Task) -> bool:
    # Add new task temporarily
    temp_graph = self.graph.copy()
    temp_graph.add_node(new_task.id)
    for dep in new_task.depends_on:
        temp_graph.add_edge(dep, new_task.id)

    # Check for cycles using DFS
    try:
        cycles = list(nx.simple_cycles(temp_graph))
        return len(cycles) > 0
    except nx.NetworkXNoCycle:
        return False
```

### Topological Sort

```python
def get_execution_order(self) -> List[str]:
    try:
        return list(nx.topological_sort(self.graph))
    except nx.NetworkXUnfeasible:
        raise CycleDetectedError("Cycle detected in task graph")
```

### Auto-Inference

```python
def infer_dependencies(self, task: Task) -> List[str]:
    deps = []
    for existing_task in self.list():
        # If file overlap, infer dependency
        overlap = set(task.files_to_edit) & set(existing_task.files_to_edit)
        if overlap and existing_task.status != "completed":
            deps.append(existing_task.id)
    return deps
```

### Task Recommendation

```python
def task_next(self) -> Task:
    # Get pending tasks with no pending dependencies
    ready_tasks = [
        t for t in self.list(status="pending")
        if all(
            self.get(dep).status == "completed"
            for dep in t.depends_on
        )
    ]

    # Sort by priority
    ready_tasks.sort(key=lambda t: priority_order(t.priority))

    return ready_tasks[0] if ready_tasks else None
```

## Future Considerations

1. **DAG Visualization**: Export to Graphviz/Mermaid for visualization
2. **Parallel Execution**: CLI flag to run independent tasks in parallel
3. **Dependency Relaxation**: Allow "soft" dependencies (hints, not hard constraints)
4. **Critical Path**: Highlight critical path (longest dependency chain)
5. **Task Splitting**: Break large tasks into sub-tasks automatically

## Performance Characteristics

| Operation       | Complexity | Notes                        |
|-----------------|------------|------------------------------|
| Add Task        | O(V + E)   | Cycle detection              |
| Get Next        | O(V)       | Filter + sort                |
| Topological Sort| O(V + E)   | Standard algorithm           |
| Infer Deps      | O(V × F)   | V tasks, F files per task    |

**Scalability**: Works well for <1,000 tasks (typical use case: 10-50 tasks).

## References

- [Directed Acyclic Graph (DAG)](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
- [Topological Sorting](https://en.wikipedia.org/wiki/Topological_sorting)
- [NetworkX Library](https://networkx.org/)
- [Task Scheduling Algorithms](https://en.wikipedia.org/wiki/Job-shop_scheduling)
