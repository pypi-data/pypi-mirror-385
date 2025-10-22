"""Run command - Manually run a task."""

from pathlib import Path


def execute(args):
    """Execute the run command."""
    env_path = Path(args.env_path)
    
    if not env_path.exists():
        print(f"Error: Environment not found: {env_path}")
        return 1
    
    try:
        from cua_bench import make
        
        print(f"Loading environment: {env_path}")
        env = make(str(env_path))
        
        print(f"Running task {args.task_id}...")
        screenshot, task_cfg = env.setup(task_id=args.task_id)
        print(f"✓ Setup complete (screenshot: {len(screenshot)} bytes)")
        
        if args.solve:
            print("Running solution...")
            screenshot = env.solve()
            print(f"✓ Solution complete (screenshot: {len(screenshot)} bytes)")
        
        # Save screenshot if requested
        if args.screenshot:
            screenshot_path = Path(args.screenshot)
            screenshot_path.write_bytes(screenshot)
            print(f"✓ Screenshot saved to: {screenshot_path}")
        
        # Evaluate if function exists
        if env.evaluate_task_fn:
            print("Running evaluation...")
            result = env.evaluate()
            print(f"✓ Evaluation result: {result}")
        
        env.close()
        print("\n✓ Task completed successfully!")
        
    except Exception as e:
        print(f"Error running task: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0
