"""
Dependency resolution for tasks.

Implements topological sorting and circular dependency detection.
"""

from typing import Dict, List, Set

from taskx.core.task import Task


class CircularDependencyError(Exception):
    """Raised when circular dependency is detected."""

    pass


class DependencyResolver:
    """Resolves task dependencies using topological sort."""

    def __init__(self, tasks: Dict[str, Task]):
        """
        Initialize resolver with tasks.

        Args:
            tasks: Dictionary of task name to Task object
        """
        self.tasks = tasks

    def resolve_dependencies(self, task_name: str) -> List[str]:
        """
        Resolve dependencies for a task in execution order.

        Args:
            task_name: Name of task to resolve

        Returns:
            List of task names in execution order (dependencies first)

        Raises:
            ValueError: If task not found
            CircularDependencyError: If circular dependency detected
        """
        if task_name not in self.tasks:
            raise ValueError(f"Task '{task_name}' not found")

        visited: Set[str] = set()
        visiting: Set[str] = set()
        result: List[str] = []

        def visit(name: str) -> None:
            """Visit a task and its dependencies (DFS)."""
            if name in visited:
                return

            if name in visiting:
                raise CircularDependencyError(
                    f"Circular dependency detected involving task '{name}'"
                )

            if name not in self.tasks:
                raise ValueError(f"Task '{name}' not found (required by dependency chain)")

            visiting.add(name)

            # Visit dependencies first
            task = self.tasks[name]
            for dep in task.depends:
                visit(dep)

            visiting.remove(name)
            visited.add(name)
            result.append(name)

        visit(task_name)
        return result

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """
        Get the complete dependency graph.

        Returns:
            Dictionary mapping task names to their dependencies
        """
        graph = {}
        for name, task in self.tasks.items():
            graph[name] = task.depends.copy()
        return graph

    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find all circular dependencies in the task graph.

        Returns:
            List of circular dependency chains
        """
        circles = []

        for task_name in self.tasks:
            try:
                self.resolve_dependencies(task_name)
            except CircularDependencyError as e:
                # Extract cycle from error message if possible
                circles.append([task_name])

        return circles

    def get_task_depth(self, task_name: str) -> int:
        """
        Get the depth of a task in the dependency tree.

        Args:
            task_name: Task to get depth for

        Returns:
            Depth (0 for tasks with no dependencies)
        """
        if task_name not in self.tasks:
            return 0

        task = self.tasks[task_name]
        if not task.depends:
            return 0

        max_dep_depth = max(self.get_task_depth(dep) for dep in task.depends)
        return max_dep_depth + 1

    def get_independent_tasks(self) -> List[str]:
        """
        Get tasks that have no dependencies.

        Returns:
            List of independent task names
        """
        return [name for name, task in self.tasks.items() if not task.depends]

    def can_run_parallel(self, task1: str, task2: str) -> bool:
        """
        Check if two tasks can run in parallel (no dependency relationship).

        Args:
            task1: First task name
            task2: Second task name

        Returns:
            True if tasks can run in parallel
        """
        try:
            deps1 = self.resolve_dependencies(task1)
            deps2 = self.resolve_dependencies(task2)

            # If either task depends on the other, they can't run in parallel
            return task1 not in deps2 and task2 not in deps1
        except (ValueError, CircularDependencyError):
            return False
