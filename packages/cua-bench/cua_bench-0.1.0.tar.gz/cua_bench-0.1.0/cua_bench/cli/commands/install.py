"""Install command - Install an environment."""

import shutil
from pathlib import Path


def execute(args):
    """Execute the install command.
    
    This command validates and prepares an environment for use.
    """
    env_path = Path(args.env_path)
    
    # Check if environment exists
    if not env_path.exists():
        print(f"Error: Environment not found: {env_path}")
        return 1
    
    # Check for main.py
    main_file = env_path / "main.py"
    if not main_file.exists():
        print(f"Error: main.py not found in {env_path}")
        return 1
    
    # Validate the environment by trying to load it
    try:
        from cua_bench import make
        env = make(str(env_path))
        
        # Check for required decorators
        if env.load_tasks_fn is None:
            print(f"Warning: No @cb.load_tasks function found in {main_file}")
        if env.setup_task_fn is None:
            print(f"Warning: No @cb.setup_task function found in {main_file}")
        
        # Try to load tasks
        if env.load_tasks_fn:
            tasks = env.load_tasks_fn()
            print(f"✓ Environment validated: {env_path}")
            print(f"  Found {len(tasks)} task(s)")
            for i, task in enumerate(tasks):
                print(f"    Task {i}: {task.description}")
        else:
            print(f"✓ Environment found: {env_path}")
        
        env.close()
        
    except Exception as e:
        print(f"Error validating environment: {e}")
        return 1
    
    print(f"\nEnvironment '{env_path.name}' is ready to use!")
    print(f"  Run a task:  td run {env_path}")
    print(f"  Batch solve: td batch solve {env_path}")
    
    return 0
