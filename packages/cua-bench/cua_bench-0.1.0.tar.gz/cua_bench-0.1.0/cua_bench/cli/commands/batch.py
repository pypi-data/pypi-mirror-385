"""Batch command - Run batch processing on GCP."""

import asyncio
import time
from pathlib import Path


def execute(args):
    """Execute the batch command."""
    env_path = Path(args.env_path)
    
    if not env_path.exists():
        print(f"Error: Environment not found: {env_path}")
        return 1
    
    # Validate environment first
    try:
        from cua_bench import make
        env = make(str(env_path))
        
        # Load tasks to get count
        if env.load_tasks_fn is None:
            print("Error: No @cb.load_tasks function found")
            return 1
        
        tasks = env.load_tasks_fn()
        task_count = len(tasks)
        print(f"Found {task_count} task(s) in environment")
        
        env.close()
        
    except Exception as e:
        print(f"Error validating environment: {e}")
        return 1
    
    # Run batch processing (always solve mode now)
    return asyncio.run(run_batch_solve(args, env_path, task_count))


async def run_batch_solve(args, env_path: Path, task_count: int):
    """Run batch solve on GCP."""
    from cua_bench.batch import execute_batch
    
    # Generate job name if not provided
    job_name = args.job_name
    if job_name is None:
        job_name = f"td-{env_path.name}-{int(time.time())}"
    
    # Check if dump mode
    dump_mode = getattr(args, 'dump_mode', False)
    
    # Use specified task count or default to all tasks
    num_tasks = args.tasks if args.tasks is not None else task_count
    
    print(f"\nStarting batch job: {job_name}")
    print(f"  Environment: {env_path}")
    print(f"  Tasks: {num_tasks}")
    print(f"  Parallelism: {args.parallelism}")
    print(f"  Mode: {'Local (Docker)' if args.local else 'GCP Batch'}")
    print(f"  Type: {'Dump (no solver)' if dump_mode else 'Solve'}")
    
    try:
        # Execute batch job
        logs = await execute_batch(
            job_name=job_name,
            env_path=env_path,
            container_script=f"python3 -m cua-bench.batch.solver {{env_path}}{' --dump' if dump_mode else ''}",
            task_count=num_tasks,
            task_parallelism=args.parallelism,
            run_local=args.local,
            image_uri=args.image,
            output_dir=getattr(args, 'output_dir', None),
            auto_cleanup=False,
        )
        
        print("\n✓ Batch job completed successfully!")
        
        if logs:
            print("\nJob output:")
            for line in logs:
                print(f"  {line}")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ Batch job failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
