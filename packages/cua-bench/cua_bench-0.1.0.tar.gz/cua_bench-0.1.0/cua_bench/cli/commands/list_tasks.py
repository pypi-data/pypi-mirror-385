"""List command - List available tasks in environments."""

from pathlib import Path
import json


def execute(args):
    """Execute the list command."""
    
    if args.env_path:
        # List tasks in specific environment
        return list_env_tasks(args, args.env_path)
    else:
        # List all environments
        return list_all_environments(args)


def list_env_tasks(args, env_path_str: str):
    """List tasks in a specific environment."""
    env_path = Path(env_path_str)
    
    if not env_path.exists():
        print(f"Error: Environment not found: {env_path}")
        return 1
    
    try:
        from cua_bench import make
        
        env = make(str(env_path))
        
        if env.load_tasks_fn is None:
            print(f"No tasks found in {env_path}")
            return 1
        
        tasks = env.load_tasks_fn()
        
        if getattr(args, 'json', False):
            payload = {
                "environment": str(env_path),
                "tasks": [
                    {
                        "index": i,
                        "description": getattr(task, 'description', None),
                        "task_id": getattr(task, 'task_id', None),
                        "metadata": getattr(task, 'metadata', None),
                    }
                    for i, task in enumerate(tasks)
                ],
                "task_count": len(tasks),
            }
            print(json.dumps(payload, indent=2))
        else:
            print(f"\nEnvironment: {env_path}")
            print(f"Tasks: {len(tasks)}")
            print()
            for i, task in enumerate(tasks):
                print(f"  [{i}] {task.description}")
                if task.task_id:
                    print(f"      ID: {task.task_id}")
                if task.metadata:
                    print(f"      Metadata: {task.metadata}")
        
        env.close()
        
    except Exception as e:
        print(f"Error listing tasks: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def list_all_environments(args):
    """List all available environments."""
    # Look for environments in common locations
    search_paths = [
        Path("tasks"),
        Path("envs"),
        Path("."),
    ]
    
    found_envs = []
    
    for search_path in search_paths:
        if not search_path.exists():
            continue
        
        # Look for directories with main.py
        for item in search_path.iterdir():
            if item.is_dir():
                main_file = item / "main.py"
                if main_file.exists():
                    found_envs.append(item)
    
    results = []
    for env_path in found_envs:
        entry = {"path": str(env_path), "task_count": None, "error": None}
        try:
            from cua_bench import make
            env = make(str(env_path))
            if env.load_tasks_fn:
                tasks = env.load_tasks_fn()
                entry["task_count"] = len(tasks)
            else:
                entry["task_count"] = 0
            env.close()
        except Exception as e:
            entry["error"] = str(e)
        results.append(entry)

    if getattr(args, 'json', False):
        print(json.dumps({
            "environments": results,
            "count": len(results)
        }, indent=2))
    else:
        if not results:
            print("No environments found.")
            print("\nSearched in:")
            for path in search_paths:
                print(f"  - {path}")
            return 0
        print(f"\nFound {len(results)} environment(s):\n")
        for r in results:
            print(f"  {r['path']}")
            if r["error"]:
                print(f"    Error: {r['error']}")
            else:
                print(f"    Tasks: {r['task_count']}")
        print()
    return 0
