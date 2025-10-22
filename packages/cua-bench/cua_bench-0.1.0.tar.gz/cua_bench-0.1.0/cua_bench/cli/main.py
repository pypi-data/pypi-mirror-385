"""Main CLI entry point for cua-bench."""

import argparse
import sys
from pathlib import Path

from .commands import (
    install, 
    batch, 
    list_tasks, 
    interact, 
    process,
    create_task
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="cua-bench - Desktop automation framework with batch processing"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # install (top-level)
    install_parser = subparsers.add_parser(
        'install',
        help='Install an environment'
    )
    install_parser.add_argument(
        'env_path',
        help='Path to environment directory (e.g., tasks/click_env)'
    )

    # tasks list (top-level, alias: ls)
    list_parser = subparsers.add_parser(
        'tasks',
        help='List available tasks in an environment',
        aliases=['ls']
    )
    list_parser.add_argument(
        'env_path',
        nargs='?',
        help='Path to environment directory (optional, lists all if not provided)'
    )
    list_parser.add_argument(
        '--json',
        action='store_true',
        help='Output results in JSON format'
    )

    # interact (top-level)
    interact_parser = subparsers.add_parser(
        'interact',
        help='Interactively run a task with browser visible'
    )
    interact_parser.add_argument(
        'env_path',
        help='Path to environment directory'
    )
    interact_parser.add_argument(
        '--task-id',
        type=int,
        default=0,
        help='Task ID to run (default: 0)'
    )
    interact_parser.add_argument(
        '--solve',
        action='store_true',
        help='Run the solution after setup'
    )
    interact_parser.add_argument(
        '--screenshot',
        help='Save screenshot to file'
    )

    # dump-solution (top-level)
    dump_solution_parser = subparsers.add_parser(
        'dump-solution',
        help='Run multi-step dump (setup + solve + evaluate)'
    )
    dump_solution_parser.add_argument(
        'env_path',
        help='Path to environment directory'
    )
    dump_solution_parser.add_argument(
        'tasks',
        nargs='?',
        type=int,
        help='Number of tasks to run (default: all tasks in environment)'
    )
    dump_solution_parser.add_argument(
        '--job-name',
        help='Custom job name (default: auto-generated)'
    )
    dump_solution_parser.add_argument(
        '--parallelism',
        type=int,
        default=8,
        help='Max concurrent tasks (default: 8)'
    )
    dump_solution_parser.add_argument(
        '--local',
        action='store_true',
        help='Run locally using Docker instead of GCP'
    )
    dump_solution_parser.add_argument(
        '--image',
        help='Custom container image URI'
    )
    dump_solution_parser.add_argument(
        '--output-dir',
        help='Output directory to save results (works in both Local and GCP modes)'
    )
    dump_solution_parser.set_defaults(dump_mode=False)

    # dump-setup (top-level)
    dump_setup_parser = subparsers.add_parser(
        'dump-setup',
        help='Run setup + evaluate (no solver)'
    )
    dump_setup_parser.add_argument(
        'env_path',
        help='Path to environment directory'
    )
    dump_setup_parser.add_argument(
        'tasks',
        nargs='?',
        type=int,
        help='Number of tasks to run (default: all tasks in environment)'
    )
    dump_setup_parser.add_argument(
        '--job-name',
        help='Custom job name (default: auto-generated)'
    )
    dump_setup_parser.add_argument(
        '--parallelism',
        type=int,
        default=8,
        help='Max concurrent tasks (default: 8)'
    )
    dump_setup_parser.add_argument(
        '--local',
        action='store_true',
        help='Run locally using Docker instead of GCP'
    )
    dump_setup_parser.add_argument(
        '--image',
        help='Custom container image URI'
    )
    dump_setup_parser.add_argument(
        '--output-dir',
        help='Output directory to save results (works in both Local and GCP modes)'
    )
    dump_setup_parser.set_defaults(dump_mode=True)

    # process command (top-level)
    process_parser = subparsers.add_parser(
        'process',
        help='Process batch dump outputs into datasets'
    )
    process_parser.add_argument(
        'outputs_path',
        help='Path to outputs folder from batch dump (e.g., ./outputs or /tmp/td_output)'
    )
    process_parser.add_argument(
        'max_samples',
        nargs='?',
        type=int,
        help='Limit number of samples processed (useful for testing)'
    )
    process_parser.add_argument(
        '--mode',
        default='aguvis',
        help="Processing mode (default: 'aguvis')"
    )
    process_parser.add_argument(
        '--dataset-name',
        help='Dataset name when saving to disk (default: td_<mode>_dataset)'
    )
    process_parser.add_argument(
        '--save-dir',
        help='Directory to save a JSONL dataset (default: <outputs>/processed if not pushing)'
    )
    process_parser.add_argument(
        '--push-to-hub',
        action='store_true',
        help='Push the dataset to the Hugging Face Hub'
    )
    process_parser.add_argument(
        '--repo-id',
        help='HF Hub repository ID (e.g., username/repo). Required with --push-to-hub.'
    )
    process_parser.add_argument(
        '--private',
        action='store_true',
        help='When pushing to hub, create/update the repo as private'
    )

    # create-task (top-level)
    create_task_parser = subparsers.add_parser(
        'create-task',
        help='Interactively scaffold a new task environment'
    )
    create_task_parser.add_argument(
        'path',
        nargs='?',
        default='.',
        help='Target directory to create the task in (default: current directory)'
    )
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(1)
    
    # Execute command
    if args.command == 'install':
        install.execute(args)
    elif args.command == 'tasks':  # 'ls' alias resolves to 'tasks'
        list_tasks.execute(args)
    elif args.command == 'interact':
        interact.execute(args)
    elif args.command in ('dump-solution', 'dump-setup'):
        batch.execute(args)
    elif args.command == 'process':
        process.execute(args)
    elif args.command == 'create-task':
        create_task.execute(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
