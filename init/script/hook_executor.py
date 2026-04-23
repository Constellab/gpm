"""Post-install hook execution with security validation."""

import os
import subprocess

from .logger import Logger


class HookExecutor:
    """Executes post-install hooks with security validation.

    This class manages:
    - Hook discovery in brick directories
    - Security validation of hook file paths
    - Execution of Python and Bash hooks
    - Timeout and error handling
    """

    HOOK_TIMEOUT_SECONDS: int = 300  # 5 minutes
    HOOKS_DIR_NAME: str = ".hooks"
    PYTHON_HOOK_NAME: str = "post-install.py"
    BASH_HOOK_NAME: str = "post-install.sh"

    def __init__(self, logger: Logger):
        """Initialize the hook executor.

        Args:
            logger: Logger instance for logging operations
        """
        self.logger = logger

    def execute_hooks_for_bricks(
        self, user_bricks_folder: str, sys_bricks_folder: str
    ) -> None:
        """Execute post-install hooks for all bricks in user and sys folders.

        User bricks are executed first. If a brick exists in both folders,
        hooks are only executed once from the user folder.

        Args:
            user_bricks_folder: Path to the user bricks folder
            sys_bricks_folder: Path to the system bricks folder
        """
        executed_bricks: set[str] = set()

        # Call hooks for user bricks first
        self.logger.info(f"Calling brick hooks in {user_bricks_folder} ...")
        self._call_hooks_in_folder(user_bricks_folder, executed_bricks)

        # Call hooks for sys bricks (skip if already executed in user bricks)
        self.logger.info(f"Calling brick hooks in {sys_bricks_folder} ...")
        self._call_hooks_in_folder(sys_bricks_folder, executed_bricks)

        self.logger.info("Brick hooks called.")

    def _call_hooks_in_folder(
        self, bricks_folder: str, executed_bricks: set[str]
    ) -> None:
        """Call post-install hooks for bricks in a specific folder.

        Executes both Python (.py) and Bash (.sh) post-install hooks if they exist
        in the brick's .hooks directory. Skips bricks whose hooks were already executed.

        Args:
            bricks_folder: Path to the folder containing bricks
            executed_bricks: Set of brick names whose hooks have already been executed
        """
        if not os.path.exists(bricks_folder):
            self.logger.info(
                f"Bricks folder {bricks_folder} does not exist, skipping hooks."
            )
            return

        # Check only direct subdirectories of bricks_folder
        for brick_name in os.listdir(bricks_folder):
            brick_path = os.path.join(bricks_folder, brick_name)

            # Skip if not a directory
            if not os.path.isdir(brick_path):
                continue

            # Skip if this brick's hooks were already executed
            if brick_name in executed_bricks:
                self.logger.info(
                    f"Skipping hooks for '{brick_name}' in {bricks_folder}, already executed in user bricks."
                )
                continue

            hooks_dir = os.path.join(brick_path, self.HOOKS_DIR_NAME)

            if os.path.isdir(hooks_dir):
                # Execute Python hook if it exists
                py_hook = os.path.join(hooks_dir, self.PYTHON_HOOK_NAME)
                self._execute_hook_file(py_hook, hooks_dir, brick_path, "python3")

                # Execute Bash hook if it exists
                sh_hook = os.path.join(hooks_dir, self.BASH_HOOK_NAME)
                self._execute_hook_file(sh_hook, hooks_dir, brick_path, "bash")

                # Mark this brick as executed
                executed_bricks.add(brick_name)

    def _execute_hook_file(
        self, hook_path: str, hooks_dir: str, brick_path: str, hook_type: str
    ) -> None:
        """Execute a single hook file with security validation.

        Args:
            hook_path: Path to the hook file to execute
            hooks_dir: Expected parent directory for security validation
            brick_path: Brick directory to use as working directory
            hook_type: Type of hook ('python3' or 'bash') for execution
        """
        if not os.path.isfile(hook_path):
            return

        # Validate that the hook file is within the expected directory
        real_hook_path = os.path.realpath(hook_path)
        real_hooks_dir = os.path.realpath(hooks_dir)
        if not real_hook_path.startswith(real_hooks_dir):
            self.logger.error(
                f"Security: {hook_type} hook {hook_path} is outside expected directory, skipping"
            )
            return

        self.logger.info(f"Executing {hook_type} hook: {hook_path}")
        try:
            subprocess.run(
                [hook_type, hook_path],
                check=True,
                timeout=self.HOOK_TIMEOUT_SECONDS,
                cwd=brick_path,  # Run in brick directory
            )
        except subprocess.CalledProcessError as err:
            self.logger.error(f"Error executing {hook_type} hook {hook_path}: {err}")
        except subprocess.TimeoutExpired:
            self.logger.error(f"Timeout executing {hook_type} hook {hook_path}")
