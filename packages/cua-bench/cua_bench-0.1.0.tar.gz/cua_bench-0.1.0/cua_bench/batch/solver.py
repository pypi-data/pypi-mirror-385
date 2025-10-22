"""Batch task solver - runs individual tasks in batch jobs."""

import os
import sys
from pathlib import Path


def main():
    """Main entry point for batch task solver.
    
    This script is run inside each batch task container.
    It uses BATCH_TASK_INDEX to determine which task to run.
    """
    if len(sys.argv) < 2:
        print("Usage: python -m cua-bench.batch.solver <env_path> [--dump]")
        sys.exit(1)
    
    env_path = Path(sys.argv[1])
    
    # Check for dump mode (skip solver)
    dump_mode = "--dump" in sys.argv
    
    # Get task index from environment variable
    task_index = int(os.environ.get("BATCH_TASK_INDEX", "0"))
    task_count = int(os.environ.get("BATCH_TASK_COUNT", "1"))
    
    print(f"Starting task {task_index} of {task_count}")
    print(f"Environment: {env_path}")
    
    try:
        from cua_bench import make
        
        # Load environment
        env = make(str(env_path))
        
        # Load all tasks
        if env.load_tasks_fn is None:
            print("Error: No @cb.load_tasks function found")
            sys.exit(1)
        
        tasks = env.load_tasks_fn()
        
        # Determine which task to run
        # If we have more batch tasks than actual tasks, distribute them
        if task_index >= len(tasks):
            print(f"Task index {task_index} >= number of tasks {len(tasks)}, skipping")
            sys.exit(0)
        
        print(f"Running task {task_index}: {tasks[task_index].description}")
        
        # Setup the task
        screenshot, task_cfg = env.setup(task_id=task_index)
        print(f"✓ Setup complete (screenshot: {len(screenshot)} bytes)")
        
        # Run the solution if available and not in dump mode
        if not dump_mode:
            if env.solve_task_fn:
                screenshot = env.solve()
                print(f"✓ Solution complete (screenshot: {len(screenshot)} bytes)")
            else:
                print("Warning: No @cb.solve_task function found")
        else:
            print("ℹ Dump mode: skipping solver")
        
        # Evaluate if available
        if env.evaluate_task_fn:
            result = env.evaluate()
            print(f"✓ Evaluation result: {result}")
        
        # Save screenshot and snapshot to output
        output_dir = Path("/tmp/td_output")
        output_dir.mkdir(exist_ok=True)
        
        screenshot_path = output_dir / f"task_{task_index}_screenshot.png"
        screenshot_path.write_bytes(screenshot)
        print(f"✓ Screenshot saved to {screenshot_path}")
        
        # Save DOM snapshot
        snapshot_html = env.snapshot()
        snapshot_path = output_dir / f"task_{task_index}_snapshot.html"
        snapshot_path.write_text(snapshot_html, encoding='utf-8')
        print(f"✓ DOM snapshot saved to {snapshot_path}")
        
        env.close()
        
        print(f"\n✓ Task {task_index} completed successfully!")
        
    except Exception as e:
        print(f"Error running task {task_index}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
