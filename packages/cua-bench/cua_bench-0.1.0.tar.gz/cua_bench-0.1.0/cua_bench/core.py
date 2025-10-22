"""Core classes and functions for cua-bench."""

from dataclasses import dataclass
from typing import Any, Optional
from pathlib import Path


@dataclass
class Task:
    """Represents a single task to be executed."""
    description: str
    task_id: Optional[str] = None
    metadata: Optional[dict] = None

def make(env_name: str, *, split: str = "train") -> "Environment":
    """Create an environment instance.
    
    Args:
        env_name: Name or path to the environment (e.g., 'click_env' or 'tasks/click_env')
        split: Dataset split to use for decorated functions (e.g., 'train', 'test')
    
    Returns:
        Environment instance
    """
    from .environment import Environment
    return Environment(env_name, split=split)
