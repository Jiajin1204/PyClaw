# tools/exec_tool.py
import os
import subprocess
import tempfile
import uuid
from typing import Dict, Any
from .base import Tool, ToolResult


class ExecTool(Tool):
    """Tool for executing Python code and shell commands."""

    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.timeout = self.config.get("timeout", 60)
        self.working_dir = self.config.get("working_dir", "workspace")

    @property
    def name(self) -> str:
        return "exec"

    @property
    def description(self) -> str:
        return "Execute Python code or shell commands. For Python, wraps code in subprocess. Returns stdout/stderr."

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

    def execute(self, command: str, language: str = "python") -> ToolResult:
        """Execute a command."""
        try:
            work_dir = os.path.expanduser(self.working_dir)
            if not os.path.exists(work_dir):
                os.makedirs(work_dir, exist_ok=True)

            if language == "python":
                result = self._run_python(command, work_dir)
            else:
                result = subprocess.run(
                    command,
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
            result = subprocess.run(
                ["python", temp_file],
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
