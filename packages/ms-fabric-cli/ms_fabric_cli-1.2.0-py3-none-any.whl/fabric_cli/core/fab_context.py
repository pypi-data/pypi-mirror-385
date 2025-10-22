# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import glob
import json
import os
import platform

import psutil

from fabric_cli.core import fab_constant, fab_logger, fab_state_config
from fabric_cli.core.fab_exceptions import FabricCLIError
from fabric_cli.core.hiearchy.fab_element import FabricElement
from fabric_cli.core.hiearchy.fab_tenant import Tenant
from fabric_cli.errors import ErrorMessages
from fabric_cli.utils import fab_ui as utils_ui


def singleton(class_):
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]

    return getinstance


@singleton
class Context:
    def __init__(self):
        self._context: FabricElement = None
        self._command: str = None
        session_id = self._get_context_session_id()
        self._context_file = os.path.join(
            fab_state_config.config_location(), f"context-{session_id}.json"
        )
        self._loading_context = False

    @property
    def context(self) -> FabricElement:
        if self._context is None:
            # In command-line mode with persistence enabled, try to load from the persisted context file
            if self._should_use_context_file():
                self._load_context_from_file()

            # If still None, initialize with the tenant
            if self._context is None:
                # Set loading flag to prevent saving the fallback tenant context
                was_loading = self._loading_context
                self._loading_context = True
                try:
                    self._load_context()
                finally:
                    self._loading_context = was_loading
        return self._context

    @context.setter
    def context(self, context: FabricElement) -> None:
        self._context = context

        # If in command-line mode with persistence enabled, save the context to file for persistence
        if self._should_use_context_file():
            self._save_context_to_file()

    @property
    def command(self) -> str:
        return self._command

    @command.setter
    def command(self, command: str) -> None:
        self._command = command

    def reset_context(self) -> None:
        self.cleanup_context_files(cleanup_all_stale=True, cleanup_current=True)
        self.context = self.context.tenant

    def print_context(self) -> None:
        utils_ui.print_grey(str(self.context))

    # Tenant

    def get_tenant(self) -> Tenant:
        assert isinstance(self.context.tenant, Tenant)
        return self.context.tenant

    def get_tenant_id(self) -> str:
        return self.get_tenant().id

    def cleanup_context_files(self, cleanup_all_stale=True, cleanup_current=False):
        """Clean up context files based on specified criteria.

        Args:
            cleanup_all_stale (bool): Remove context files for non-existent parent processes
            cleanup_current (bool): Remove the current session's context file
        """
        try:
            config_dir = fab_state_config.config_location()

            # Clean up current session's context file if requested
            if cleanup_current and os.path.exists(self._context_file):
                os.remove(self._context_file)

            # Clean up stale context files if requested
            if cleanup_all_stale:
                # Find all context files in the config directory
                context_pattern = os.path.join(config_dir, "context-*.json")
                for context_file in glob.glob(context_pattern):
                    try:
                        # Extract PPID from filename
                        filename = os.path.basename(context_file)
                        ppid_str = filename[
                            8:-5
                        ]  # Remove "context-" prefix and ".json" suffix
                        ppid = int(ppid_str)

                        # Check if the parent process still exists
                        if not self._process_exists(ppid):
                            os.remove(context_file)
                    except (ValueError, OSError):
                        # If we can't parse the PPID or check process existence,
                        # leave the file alone to be safe
                        continue
        except Exception:
            # Silently fail on cleanup errors - not critical for operation
            pass

    # Context helpers

    def _load_context(self) -> None:
        from fabric_cli.core.fab_auth import FabAuth

        self.context = FabAuth().get_tenant()

    def _should_use_context_file(self) -> bool:
        """Determine if the context file should be used based on the current mode and persistence settings."""
        mode = fab_state_config.get_config(fab_constant.FAB_MODE)
        persistence_enabled = fab_state_config.get_config(
            fab_constant.FAB_CONTEXT_PERSISTENCE_ENABLED
        )
        return (
            mode == fab_constant.FAB_MODE_COMMANDLINE
            and persistence_enabled == "true"
            and not self._loading_context
        )

    def _save_context_to_file(self) -> None:
        """Save the current context path to a session-specific file for persistence.

        Context persistence is only active when both the mode is command-line
        and the context_persistence_enabled flag is set to true.

        For example, when using 'cd' to navigate to a workspace, subsequent
        commands in the same shell will operate in that workspace context.
        """
        if self._context is not None:
            context_data = {
                "path": self._context.path,
            }

            try:
                with open(self._context_file, "w") as f:
                    json.dump(context_data, f)
            except Exception:
                utils_ui.print_warning(
                    "Warning: Failed to save context file. Context persistence may not work as expected."
                )
                pass

    def _load_context_from_file(self) -> None:
        """Load the context from a session-specific file if available.

        Restores context from a previous command-line invocation within the
        same shell session. Each shell session has its own context file based
        on the shell session.

        Context persistence is only active when both the mode is command-line
        and the context_persistence_enabled flag is set to true.
        """
        # Set flag to prevent re-entrant calls
        self._loading_context = True
        try:
            # Clean up stale context files from closed shells
            self.cleanup_context_files(cleanup_all_stale=True, cleanup_current=False)

            if os.path.exists(self._context_file):
                with open(self._context_file, "r") as f:
                    context_data = json.load(f)

                if "path" in context_data:
                    from fabric_cli.core import fab_handle_context

                    # Load the context using the saved path
                    path = context_data["path"]
                    if path:
                        self._context = fab_handle_context.get_command_context(path)
                        utils_ui.print_warning(
                            f"Command context path: { 'root' if isinstance(self._context, Tenant) else self._context.path }"
                        )
        except Exception:
            # If loading fails, reset the context file and show error
            try:
                if os.path.exists(self._context_file):
                    os.remove(self._context_file)
            except Exception:
                # If we can't even remove the file, just continue silently
                pass

            raise FabricCLIError(
                ErrorMessages.Context.context_load_failed(),
                fab_constant.ERROR_CONTEXT_LOAD_FAILED,
            )
        finally:
            # Always reset the flag
            self._loading_context = False

    def _process_exists(self, pid):
        """Check if a process with the given PID exists.

        Args:
            pid (int): Process ID to check

        Returns:
            bool: True if process exists, False otherwise
        """
        try:
            if platform.system() == "Windows":
                # On Windows, use tasklist command to check if process exists
                import subprocess

                result = subprocess.run(
                    ["tasklist", "/FI", f"PID eq {pid}"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                return str(pid) in result.stdout
            else:
                # On Unix-like systems, check /proc directory or use kill with signal 0
                try:
                    os.kill(pid, 0)
                    return True
                except OSError:
                    return False
        except Exception:
            # If we can't determine process existence, assume it exists to be safe
            return True

    def _get_context_session_id(self):
        """Get the session ID for the current shell session.

        Uses the shell/executing environment process ID to create a unique context session ID
        per shell session. For pip/conda installations, this skips over the python wrapper
        process and anchors to the actual shell session, ensuring multiple shell sessions
        don't interfere with each other.

        Fallback hierarchy:
        1. Try to get grandparent process (session/shell)
        2. If grandparent fails, fall back to parent process
        3. If parent fails, fall back to current process
        """
        try:
            parent_process = psutil.Process().parent()
            if parent_process is None:
                fab_logger.log_debug(
                    "No parent process was found. Falling back to the current process for session ID resolution."
                )
                return os.getpid()
        except Exception as e:
            fab_logger.log_debug(
                f"Failed to get parent process: {e}. Falling back to current process for session ID resolution."
            )
            return os.getpid()

        try:
            session_process = parent_process.parent()
            if session_process is not None:
                return session_process.pid
            else:
                fab_logger.log_debug(
                    "No grandparent process was found. Falling back to parent process for session ID resolution."
                )
                return parent_process.pid
        except Exception as e:
            fab_logger.log_debug(
                f"Failed to get grandparent process: {e}. Falling back to parent process for session ID resolution."
            )
            return parent_process.pid
