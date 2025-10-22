"""Environment class for programmatic interface."""

import importlib.util
import sys
import mimetypes
from pathlib import Path
from typing import Optional, List, Any
from playwright.sync_api import sync_playwright

class Environment:
    """Environment for running cua-bench tasks programmatically."""
    
    def __init__(self, env_path: str, *, split: str = "train"):
        """Initialize environment.
        
        Args:
            env_path: Path to environment directory (e.g., 'tasks/click_env')
            split: Dataset split to use when selecting decorated functions
        """
        self.env_path = Path(env_path)
        self.split = split
        if not self.env_path.is_absolute():
            # Try relative to current directory
            if not self.env_path.exists():
                # Try relative to project root
                project_root = Path(__file__).parent.parent
                self.env_path = project_root / env_path
        
        if not self.env_path.exists():
            raise FileNotFoundError(f"Environment not found: {env_path}")
        
        self.main_file = self.env_path / "main.py"
        if not self.main_file.exists():
            raise FileNotFoundError(f"main.py not found in {self.env_path}")
        
        # Load the environment module
        self._load_module()
        
        # Playwright context
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.current_window = None
        self.current_task = None
        self.tasks = None
        self.headless = True  # Default to headless mode
        
        # Desktop environment
        self.desktop = None
        
        # Static file serving
        self.static_dirs = []
    
    def _load_module(self):
        """Load the environment's main.py module."""
        spec = importlib.util.spec_from_file_location("env_module", self.main_file)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {self.main_file}")
        
        self.module = importlib.util.module_from_spec(spec)
        
        # Inject cua-bench with custom launch function
        import cua_bench as cb
        self.module.td = td
        
        # Execute the module
        spec.loader.exec_module(self.module)
        
        # Extract decorated functions for the requested split
        self.load_tasks_fn = None
        self.setup_task_fn = None
        self.solve_task_fn = None
        self.evaluate_task_fn = None

        # Only accept functions whose _td_split matches the requested split
        for name in dir(self.module):
            obj = getattr(self.module, name)
            if callable(obj) and hasattr(obj, '_td_type'):
                td_type = getattr(obj, '_td_type', None)
                td_split = getattr(obj, '_td_split', None)
                if td_split != self.split:
                    continue
                if td_type == 'load_tasks':
                    self.load_tasks_fn = obj
                elif td_type == 'setup_task':
                    self.setup_task_fn = obj
                elif td_type == 'solve_task':
                    self.solve_task_fn = obj
                elif td_type == 'evaluate_task':
                    self.evaluate_task_fn = obj
    
    def _init_playwright(self):
        """Initialize Playwright browser."""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-dev-shm-usage"]
            )
            self.context = self.browser.new_context()
            self.page = self.context.new_page()
            self.static_routes = {}  # Track static file routes
            
            # Set up unified static file handler
            def handle_all_static(route):
                url = route.request.url
                
                # Check each registered static route
                for url_path, local_dir in self.static_routes.items():
                    if f"/{url_path}/" in url:
                        file_path = url.split(f"/{url_path}/", 1)[1].split("?")[0]
                        full_path = local_dir / file_path
                        
                        if full_path.exists() and full_path.is_file():
                            # Determine content type using mimetypes
                            content_type, _ = mimetypes.guess_type(str(full_path))
                            if content_type is None:
                                content_type = "application/octet-stream"
                            
                            # Add charset for text-based content types
                            if content_type.startswith("text/"):
                                content_type += "; charset=utf-8"
                                with open(full_path, 'r', encoding='utf-8') as f:
                                    body = f.read()
                            else:
                                # Read and serve the file
                                with open(full_path, 'rb') as f:
                                    body = f.read()
                            route.fulfill(status=200, content_type=content_type, body=body)
                            return
                
                # No matching static route, continue
                route.continue_()
            
            # Register the unified handler once
            self.page.route("*://127.0.0.1/**", handle_all_static)
    
    def serve_static(self, url_path: str, local_path: str):
        """Serve static files from a local directory.
        
        Args:
            url_path: URL path prefix (e.g., "css", "gui")
            local_path: Local directory path relative to environment or cua-bench root
        """
        self._init_playwright()
        
        # Resolve local path
        local_dir = Path(local_path)
        if not local_dir.is_absolute():
            # Try relative to environment directory first
            env_relative = self.env_path / local_path
            if env_relative.exists():
                local_dir = env_relative
            else:
                # Try relative to cua-bench package
                pkg_relative = Path(__file__).parent / local_path
                if pkg_relative.exists():
                    local_dir = pkg_relative
                else:
                    raise FileNotFoundError(f"Static directory not found: {local_path}")
        
        # Store the route mapping (will be used by the unified handler in _init_playwright)
        self.static_routes[url_path] = local_dir
    
    def _init_desktop(self):
        """Initialize the desktop environment."""
        if self.desktop is None:
            from .desktop import Desktop
            self.desktop = Desktop(self)
            # Render initial desktop
            self.desktop._render()
    
    def setup(self, task_id: Optional[int] = None):
        """Setup the environment and return task config and initial screenshot.
        
        Args:
            task_id: Optional task ID to run (defaults to first task)
        
        Returns:
            Tuple of (screenshot_bytes, task_cfg)
        """
        # Load tasks if not already loaded
        if self.tasks is None:
            if self.load_tasks_fn is None:
                raise RuntimeError("No @cb.load_tasks function found in environment")
            self.tasks = self.load_tasks_fn()
        
        # Select task
        if task_id is None:
            task_id = 0
        if task_id >= len(self.tasks):
            raise ValueError(f"Task ID {task_id} out of range (0-{len(self.tasks)-1})")
        
        self.current_task = self.tasks[task_id]
        
        # Initialize Playwright first (sets up route handlers)
        self._init_playwright()
        
        # Initialize desktop environment before setup
        self._init_desktop()
        
        # Run setup - pass task_cfg and env
        if self.setup_task_fn is not None:
            self.setup_task_fn(self.current_task, self)
        
        # Take screenshot
        if self.page is not None:
            return (self.page.screenshot(), self.current_task)
        else:
            raise RuntimeError("No page created during setup")
    
    def step(self, playwright_code: str) -> bytes:
        """Execute a step of Playwright code and return screenshot.
        
        Args:
            playwright_code: Playwright code to execute (e.g., 'page.click("#submit")')
        
        Returns:
            Screenshot bytes
        """
        if self.page is None:
            raise RuntimeError("Environment not initialized. Call setup() first.")
        
        # Create execution context with page available
        exec_globals = {
            'page': self.page,
            'window': self.current_window,
        }
        
        # Execute the code
        exec(playwright_code, exec_globals)
        
        # Return screenshot
        return self.page.screenshot()
    
    def solve(self) -> bytes:
        """Run the solution function and return screenshot.
        
        Returns:
            Screenshot bytes
        """
        if self.solve_task_fn is None:
            raise RuntimeError("No @cb.solve_task function found in environment")
        
        if self.current_task is None:
            raise RuntimeError("No task loaded. Call setup() first.")
        
        # Run solve - pass task_cfg and env
        self.solve_task_fn(self.current_task, self)
        return self.page.screenshot()
    
    def evaluate(self) -> Any:
        """Run the evaluation function and return results."""
        if self.evaluate_task_fn is None:
            raise RuntimeError("No @cb.evaluate_task function found in environment")
        
        if self.current_task is None:
            raise RuntimeError("No task loaded. Call setup() first.")
        
        # Run evaluate - pass task_cfg and env
        return self.evaluate_task_fn(self.current_task, self)
    
    def snapshot(
        self,
        *,
        include_client_rects: bool = True,
        include_form_values: bool = True,
        include_scroll_offset: bool = True,
        include_text_selection: bool = True,
        include_random_text_actions: bool = True,
        include_keyboard_focus: bool = True,
        include_window_management_actions: bool = True,
    ) -> str:
        """Capture a normalized DOM snapshot with all interactive state.
        
        Returns:
            HTML string with normalized DOM including:
            - Input values as 'value' attributes
            - Checkbox/radio states as 'checked' attributes
            - Select options as 'selected' attributes
            - Scroll positions as data-scroll-* attributes
            - Text selections as data-selection-* attributes
            - Focus state as data-focused attribute
            - Bounding boxes as data-bbox-* attributes (x, y, width, height, top, right, bottom, left)
            - Window scroll position as data-window-scroll-x/y on root element
        """
        if self.page is None:
            raise RuntimeError("Environment not initialized. Call setup() first.")
        
        # Load snapshot builder JS and execute it
        js_path = Path(__file__).parent / "www" / "js" / "snapshot.js"
        if not js_path.exists():
            raise FileNotFoundError(f"snapshot.js not found at {js_path}")
        # Inject script (idempotent inside the script)
        self.page.add_script_tag(path=str(js_path))
        # Evaluate builder function exposed by the script with options
        opts = {
            "includeClientRects": include_client_rects,
            "includeKeyboardFocus": include_keyboard_focus,
            "includeFormValues": include_form_values,
            "includeScrollOffset": include_scroll_offset,
            "includeTextSelection": include_text_selection,
            "includeRandomTextActions": include_random_text_actions,
            "includeWindowManagementActions": include_window_management_actions,
        }
        return self.page.evaluate("opts => window.__td_build_snapshot(opts)", opts)
    
    def close(self):
        """Clean up resources."""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
