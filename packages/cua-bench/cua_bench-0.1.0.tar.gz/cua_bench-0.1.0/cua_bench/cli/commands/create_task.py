"""Create task command - interactively scaffold a new task environment."""

import os
from pathlib import Path

PYPROJECT_TEMPLATE = """
[project]
name = "{project_name}"
version = "0.1.0"
license = "{license_name}"
authors = [
    {{ name = "{author_name}", email = "{author_email}" }}
]
requires-python = ">=3.11"
dependencies = [
    "beautifulsoup4>=4.14.2",
    "html5lib>=1.1",
    "pyquery>=2.0.1",
]

[tool.cua-bench]
description = "{description}"
difficulty = "{difficulty}"
category = "{category}"
tags = [{tags_toml}]
"""

MAIN_PY_TEMPLATE = """
import cua_bench as cb

# Called once per batch
@cb.load_tasks(split="train")
def load():
    # Load the tasks in this environment
    return [
        cb.Task(description='Click the "Submit" button on the page.'),
    ]

# Called once per task
@cb.setup_task(split="train")
def start(task_cfg, env):
    # Your task setup code here

    # Configure desktop theme and size
    env.desktop.configure(os_type="win11", width=1024, height=768)
    
    # Read your HTML content
    with open(env.env_path / 'app.html', 'r') as f:
        html_content = f.read()
    
    # Launch a window with the content
    env.desktop.launch(
        content=html_content,
        title="My App",
        x=100, y=100,
        width=600, height=400
    )

# Called once per task
@cb.solve_task(split="train")
def solve(task_cfg, env):
    # Your solution code here
    env.page.click("#submit")

# Called once per task
@cb.evaluate_task(split="train")
def evaluate(task_cfg, env):
    # Your evaluation code here
    result = env.page.evaluate("() => localStorage.getItem('submitted')")
    return [1.0] if result == 'true' else [0.0]
"""

APP_HTML_TEMPLATE = """
<div class="p-1">
    <h1>Click the button</h1>
    <button id="submit" class="btn" data-instruction="the button">Submit</button>
    <script>
        document.getElementById('submit').addEventListener('click', function() {
            localStorage.setItem('submitted', 'true');
            this.textContent = 'Submitted!';
            this.disabled = true;
        });
    </script>
</div>
"""


def prompt(prompt_text: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt_text}{suffix}: ").strip()
    return val if val else (default or "")


def execute(args) -> int:
    # Determine target directory
    target_path = Path(getattr(args, 'path', '.') or '.')
    if not target_path.is_absolute():
        target_path = Path.cwd() / target_path

    if target_path.exists():
        if not target_path.is_dir():
            print(f"Error: Target path is not a directory: {target_path}")
            return 1

        # Ensure the target directory is empty
        if any(target_path.iterdir()):
            print(f"Error: Target directory is not empty: {target_path}")
            return 1

    # Derive default task name from directory name
    dir_name = target_path.name
    default_project_name = f"{dir_name.replace('_', '-').replace(' ', '-')}"
    # Convention: project name like "uigen-env"
    if not default_project_name.endswith('-env'):
        default_project_name = f"{default_project_name}-env"

    # Interactive prompts
    project_name = default_project_name # prompt("Project name", default_project_name)
    author_name = prompt("Author name")
    author_email = prompt("Author email")
    license_name = prompt("License", "MIT")
    description = prompt("Task description")
    difficulty = prompt("Task difficulty (easy|medium|hard)", "easy")
    category = prompt("Task category (e.g., grounding, software-engineering)", "grounding")
    tags_csv = prompt("Tags (comma-separated)", "")

    tags_list = [t.strip() for t in tags_csv.split(',') if t.strip()] if tags_csv else []
    tags_toml = ", ".join([f'"{t}"' for t in tags_list])

    # Prepare files
    pyproject_path = target_path / 'pyproject.toml'
    main_py_path = target_path / 'main.py'
    app_html_path = target_path / 'app.html'

    pyproject_content = PYPROJECT_TEMPLATE.format(
        project_name=project_name,
        license_name=license_name,
        author_name=author_name,
        author_email=author_email,
        description=description,
        difficulty=difficulty,
        category=category,
        tags_toml=tags_toml,
    ).strip()
    main_py_content = MAIN_PY_TEMPLATE.strip()
    app_html_content = APP_HTML_TEMPLATE.strip()

    target_path.mkdir(parents=True, exist_ok=True)
    app_html_path.write_text(app_html_content, encoding='utf-8')
    pyproject_path.write_text(pyproject_content, encoding='utf-8')
    main_py_path.write_text(main_py_content, encoding='utf-8')

    print(f"\n✓ Created task at: {target_path}")
    print(f"  - {pyproject_path.relative_to(Path.cwd())}")
    print(f"  - {main_py_path.relative_to(Path.cwd())}")
    print(f"  - {app_html_path.relative_to(Path.cwd())}")
    return 0
