"""cua-bench SDK - A framework for desktop automation tasks with batch processing."""

from .core import Task, make
from .decorators import load_tasks, setup_task, solve_task, evaluate_task
from .environment import Environment
from .desktop import Desktop

__all__ = [
    "Task",
    "make",
    "load_tasks",
    "setup_task",
    "solve_task",
    "evaluate_task",
    "Environment",
    "Desktop",
]
