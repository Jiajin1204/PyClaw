# tools/exec_tool.py
import os
import subprocess
import tempfile
from typing import Dict, Any
from .base import Tool, ToolResult


class ExecTool(Tool):
    """Tool for executing Python code and shell commands."""

    UNIX_TO_WINDOWS = {
        "ls": "dir",
        "ls -la": "dir /a",
        "ll": "dir /a",
        "pwd": "cd",
        "cat": "type",
        "rm": "del",
        "cp": "copy",
        "mv": "move",
        "mkdir": "mkdir",
        "touch": "echo. >",
        "clear": "cls",
        "which": "where",
    }

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)
        self.working_dir = self.config.get("working_dir", "workspace")
        self.is_windows = os.name == "nt"

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute Python code or shell commands. Returns stdout/stderr."

    @property
    def parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Shell command or Python code to execute"
                },
                "language": {
                    "type": "string",
                    "enum": ["python", "shell"],
                    "description": "Language to execute in",
                    "default": "python"
                }
            },
            "required": ["command"]
        }

    def _translate_command(self, cmd: str) -> str:
        """Translate Unix command to Windows equivalent."""
        if not self.is_windows:
            return cmd
        cmd_stripped = cmd.strip()
        for unix_cmd, win_cmd in self.UNIX_TO_WINDOWS.items():
            if cmd_stripped == unix_cmd:
                return win_cmd
            if cmd_stripped.startswith(unix_cmd + " "):
                return win_cmd + cmd_stripped[len(unix_cmd):]
        return cmd

    def execute(self, command: str, language: str = "python") -> ToolResult:
        """Execute a command."""
        try:
            work_dir = os.path.expanduser(self.working_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir, exist_ok=True)

            if language == "python":
                result = self._run_python(command, work_dir)
            else:
                cmd = self._translate_command(command)
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=work_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                return ToolResult(
                    result.returncode == 0,
                    result.stdout if result.stdout else result.stderr,
                    None if result.returncode == 0 else result.stderr
                )
            return result
        except subprocess.TimeoutExpired:
            return ToolResult(False, "", f"Execution timed out after {self.timeout} seconds")
        except Exception as e:
            return ToolResult(False, "", str(e))

    def _run_python(self, code: str, work_dir: str) -> ToolResult:
        """Run Python code in a subprocess."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            temp_file = f.name

        try:
            python_cmd = "python" if not self.is_windows else "python"
            result = subprocess.run(
                [python_cmd, temp_file],
                capture_output=True,
                text=True,
                cwd=work_dir,
                timeout=self.timeout
            )
            output = result.stdout
            if result.stderr:
                output += "\n[STDERR]\n" + result.stderr
            return ToolResult(result.returncode == 0, output, None if result.returncode == 0 else result.stderr)
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
