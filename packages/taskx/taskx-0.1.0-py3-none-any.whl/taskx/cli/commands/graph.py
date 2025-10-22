"""
Graph command implementation.

Visualizes task dependencies in ASCII or export formats.
"""

from pathlib import Path
from typing import Dict, List, Set

import click
from rich.console import Console
from rich.tree import Tree

from taskx.core.config import Config
from taskx.core.task import Task


@click.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["tree", "mermaid", "dot"], case_sensitive=False),
    default="tree",
    help="Output format (tree=ASCII tree, mermaid=Mermaid diagram, dot=Graphviz DOT)",
)
@click.option(
    "--task",
    "-t",
    help="Show graph for specific task only (default: show all tasks)",
)
@click.pass_context
def graph(ctx: click.Context, format: str, task: str) -> None:
    """
    Visualize task dependencies.

    Examples:

        # Show all tasks as ASCII tree
        $ taskx graph

        # Show specific task dependencies
        $ taskx graph --task deploy

        # Export as Mermaid diagram
        $ taskx graph --format mermaid > tasks.mmd

        # Export as Graphviz DOT
        $ taskx graph --format dot > tasks.dot
    """
    console: Console = ctx.obj["console"]
    config_path: Path = ctx.obj["config_path"]

    # Load configuration
    try:
        config = Config(config_path)
        config.load()
    except Exception as e:
        console.print(f"[red]✗ Failed to load configuration: {e}[/red]")
        ctx.exit(1)

    if not config.tasks:
        console.print("[yellow]No tasks defined[/yellow]")
        ctx.exit(0)

    # Generate graph
    if format == "tree":
        _print_tree(console, config.tasks, task)
    elif format == "mermaid":
        _print_mermaid(console, config.tasks, task)
    elif format == "dot":
        _print_dot(console, config.tasks, task)


def _print_tree(console: Console, tasks: Dict[str, Task], specific_task: str = None) -> None:
    """Print dependency graph as ASCII tree using Rich."""
    if specific_task:
        if specific_task not in tasks:
            console.print(f"[red]✗ Task '{specific_task}' not found[/red]")
            return

        # Build tree for specific task
        tree = Tree(f"[cyan]{specific_task}[/cyan]")
        _build_tree_node(tree, specific_task, tasks, set())
        console.print(tree)

    else:
        # Show all tasks
        # Find root tasks (tasks with no dependencies or not depended upon)
        all_deps = set()
        for task in tasks.values():
            all_deps.update(task.depends)

        root_tasks = [name for name in tasks.keys() if name not in all_deps or not tasks[name].depends]

        if not root_tasks:
            # If all tasks have dependencies (circular or complex), show all
            root_tasks = list(tasks.keys())

        tree = Tree("[bold]Task Dependencies[/bold]")
        visited = set()
        for root in sorted(root_tasks):
            branch = tree.add(f"[cyan]{root}[/cyan]")
            _build_tree_node(branch, root, tasks, visited)

        console.print(tree)


def _build_tree_node(node: Tree, task_name: str, tasks: Dict[str, Task], visited: Set[str]) -> None:
    """Recursively build tree nodes for dependencies."""
    if task_name in visited:
        node.add("[dim](circular reference)[/dim]")
        return

    visited.add(task_name)

    task = tasks.get(task_name)
    if not task:
        return

    for dep in task.depends:
        dep_task = tasks.get(dep)
        if dep_task:
            desc = f" - {dep_task.description}" if dep_task.description else ""
            branch = node.add(f"[green]{dep}[/green]{desc}")
            _build_tree_node(branch, dep, tasks, visited.copy())
        else:
            node.add(f"[red]{dep}[/red] [dim](not found)[/dim]")


def _print_mermaid(console: Console, tasks: Dict[str, Task], specific_task: str = None) -> None:
    """Print dependency graph as Mermaid diagram."""
    lines = ["graph TD"]

    # Filter tasks if specific task requested
    if specific_task:
        if specific_task not in tasks:
            console.print(f"[red]✗ Task '{specific_task}' not found[/red]")
            return

        # Get all dependencies recursively
        relevant_tasks = _get_task_closure(specific_task, tasks)
    else:
        relevant_tasks = set(tasks.keys())

    # Add nodes with descriptions
    for name in sorted(relevant_tasks):
        task = tasks[name]
        if task.description:
            # Escape special characters for Mermaid
            desc = task.description.replace('"', "'")
            lines.append(f'    {_sanitize_name(name)}["{name}<br/>{desc}"]')
        else:
            lines.append(f'    {_sanitize_name(name)}["{name}"]')

    # Add edges
    for name in sorted(relevant_tasks):
        task = tasks[name]
        for dep in task.depends:
            if dep in relevant_tasks:
                lines.append(f"    {_sanitize_name(dep)} --> {_sanitize_name(name)}")

    # Add styling
    lines.append("")
    lines.append("    classDef default fill:#f9f,stroke:#333,stroke-width:2px")

    output = "\n".join(lines)
    console.print(output)


def _print_dot(console: Console, tasks: Dict[str, Task], specific_task: str = None) -> None:
    """Print dependency graph as Graphviz DOT format."""
    lines = ["digraph Tasks {"]
    lines.append('    rankdir=LR;')
    lines.append('    node [shape=box, style=rounded];')

    # Filter tasks if specific task requested
    if specific_task:
        if specific_task not in tasks:
            console.print(f"[red]✗ Task '{specific_task}' not found[/red]")
            return

        relevant_tasks = _get_task_closure(specific_task, tasks)
    else:
        relevant_tasks = set(tasks.keys())

    # Add nodes
    for name in sorted(relevant_tasks):
        task = tasks[name]
        if task.description:
            label = f"{name}\\n{task.description}"
        else:
            label = name
        lines.append(f'    "{name}" [label="{label}"];')

    # Add edges
    for name in sorted(relevant_tasks):
        task = tasks[name]
        for dep in task.depends:
            if dep in relevant_tasks:
                lines.append(f'    "{dep}" -> "{name}";')

    lines.append("}")

    output = "\n".join(lines)
    console.print(output)


def _get_task_closure(task_name: str, tasks: Dict[str, Task]) -> Set[str]:
    """Get all tasks in the dependency closure of a given task."""
    closure = {task_name}
    queue = [task_name]

    while queue:
        current = queue.pop(0)
        task = tasks.get(current)
        if not task:
            continue

        for dep in task.depends:
            if dep not in closure and dep in tasks:
                closure.add(dep)
                queue.append(dep)

    return closure


def _sanitize_name(name: str) -> str:
    """Sanitize task name for use in Mermaid diagrams."""
    # Replace hyphens and special chars with underscores
    return name.replace("-", "_").replace(".", "_").replace(":", "_")
