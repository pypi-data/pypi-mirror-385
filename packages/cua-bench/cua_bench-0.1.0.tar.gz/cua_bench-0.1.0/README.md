# cua-bench

A framework for computer automation machine learning. Features a HTML-based desktop environment with a semantic design system that can visually emulate `macos`, `win11`, `win10`, `ios`, `android`, and more.

## Installation

```bash
uv pip install -e .
playwright install chromium
```

### Docker Setup (for batch processing)

Build the cua-bench Docker image:

```bash
docker build -t cua-bench:latest .
```

## Quick Start

### Create an environment

```bash
td create-task tasks/my_env
```

Run the environment:

```bash
td interact tasks/my_env
```

### CLI Usage

#### Install an environment
```bash
td install tasks/click_env
```

#### List tasks
```bash
# List all environments
td tasks

# List tasks in specific environment
td tasks tasks/click_env
```

#### Interact with a task

Interact with a task in the browser. This is useful for debugging and testing.

```bash
td interact tasks/click_env --task-id 0 --solve --screenshot output.png
```

#### Run tasks with batch processing

Run a cluster of cua-bench tasks on GCP or locally. For multi-step trajectories, use `td dump-solution`. For single-step trajectories, use `td dump-setup`.

```bash
# Build Docker image first (required for local batch)
docker build -t cua-bench:latest .

# Local (Docker) - Run 4 tasks from click_env (setup + solve + evaluate)
td dump-solution tasks/click_env 4 --local

# Local (Docker) - Run 4 tasks from click_env (setup + evaluate)
td dump-setup tasks/click_env 4 --local --output-dir ./outputs

# GCP Batch - Run 16 tasks from click_env (setup + solve + evaluate)
td dump-solution tasks/click_env 16 --parallelism 8

# GCP Batch - Run 16 tasks from click_env (setup + evaluate)
td dump-setup tasks/click_env 16 --parallelism 8 --output-dir ./outputs
```
 
#### Process snapshots into a training dataset for UI grounding

Given a directory of snapshots, cua-bench offers a simple way to process them into a dataset for UI grounding using action augmentation.

```bash
# Process 5 snapshots using 'aguvis' action augmentation
td process ./outputs 5

# Process all snapshots and push to Hugging Face Hub
td process ./outputs --push-to-hub --repo-id username/repo
```

### Programmatic Interface

```python
import cua_bench as cb

# Create an environment
env = cb.make("tasks/click_env")

# Setup and get initial screenshot
screenshot, task_cfg = env.setup()  # optionally pass task_id

# Execute a step
screenshot = env.step('page.click("#submit")')

# Run the solution
screenshot = env.solve()

# Evaluate the result
rewards = env.evaluate()

# Clean up
env.close()
```