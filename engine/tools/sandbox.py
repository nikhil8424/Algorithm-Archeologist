"""
Secure Sandbox Executor for Algorithm Archaeologist.
Executes candidate algorithm code inside an isolated Python subprocess with:
- AST Static Security Inspection (bans os, subprocess, socket, file I/O, dangerous dunders)
- Wall-clock timeout enforcement (kill runaway processes)
- Memory peak tracking using tracemalloc
- Clean capture of return values, stdout, stderr, and failure classifications.
"""
import ast
import json
import os
import subprocess
import sys
import tempfile
import time
from typing import Any, Dict, List, Optional, Tuple
from engine.models import ExecutionStatus

BANNED_MODULES = {
    "os", "subprocess", "socket", "sys", "shutil", "urllib", "requests",
    "http", "ftplib", "telnetlib", "posix", "nt", "pty", "commands",
    "asyncio", "multiprocessing", "threading", "ctypes", "builtins"
}

BANNED_BUILTINS = {
    "eval", "exec", "compile", "__import__", "open", "input", "globals",
    "locals", "vars", "exit", "quit", "breakpoint"
}

BANNED_ATTRS = {
    "__subclasses__", "__bases__", "__class__", "__globals__", "__code__"
}

class SecurityViolationError(Exception):
    pass

def inspect_code_ast(code: str) -> Tuple[bool, Optional[str]]:
    """Statically checks AST for forbidden imports, calls, or dunder exploits."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"Syntax Error during AST parse: {e.msg} at line {e.lineno}"

    has_solve_func = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "solve":
            has_solve_func = True

        # Check imports
        if isinstance(node, ast.Import):
            for alias in node.names:
                root_pkg = alias.name.split(".")[0]
                if root_pkg in BANNED_MODULES:
                    return False, f"Security Violation: Import of forbidden module '{alias.name}'"
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                root_pkg = node.module.split(".")[0]
                if root_pkg in BANNED_MODULES:
                    return False, f"Security Violation: Import from forbidden module '{node.module}'"

        # Check banned builtin calls
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in BANNED_BUILTINS:
                return False, f"Security Violation: Call to banned builtin '{node.func.id}()'"

        # Check banned attribute accesses
        elif isinstance(node, ast.Attribute):
            if node.attr in BANNED_ATTRS:
                return False, f"Security Violation: Access to restricted dunder attribute '{node.attr}'"

    if not has_solve_func:
        return False, "Validation Error: Candidate code must define a top-level 'def solve(...)' function"

    return True, None


RUNNER_TEMPLATE = """
import sys
import json
import time
import tracemalloc
import io

{code}

def __run_execution():
    raw_input_data = {input_json_str}
    
    # Redirect stdout
    stdout_buf = io.StringIO()
    sys_stdout_backup = sys.stdout
    sys.stdout = stdout_buf
    
    tracemalloc.start()
    t_start = time.perf_counter()
    res = None
    err = None
    err_type = None
    
    try:
        if isinstance(raw_input_data, dict) and "__kwargs__" in raw_input_data:
            res = solve(**raw_input_data["__kwargs__"])
        elif isinstance(raw_input_data, list) and len(raw_input_data) == 1 and isinstance(raw_input_data[0], dict) and "__args__" in raw_input_data[0]:
            res = solve(*raw_input_data[0]["__args__"])
        elif isinstance(raw_input_data, dict):
            # Try passing as kwargs or single dict
            try:
                res = solve(**raw_input_data)
            except TypeError:
                res = solve(raw_input_data)
        elif isinstance(raw_input_data, (list, tuple)):
            try:
                res = solve(*raw_input_data)
            except TypeError:
                res = solve(raw_input_data)
        else:
            res = solve(raw_input_data)
    except Exception as e:
        err = str(e)
        err_type = type(e).__name__
    finally:
        t_end = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        sys.stdout = sys_stdout_backup

    runtime_ms = (t_end - t_start) * 1000.0
    memory_mb = peak / (1024.0 * 1024.0)
    
    output_payload = {{
        "result": res,
        "runtime_ms": runtime_ms,
        "memory_mb": memory_mb,
        "stdout": stdout_buf.getvalue()[:2000],
        "error": err,
        "error_type": err_type
    }}
    
    # Write to stdout as a single JSON line
    print("__ALGO_ARCH_OUTPUT_START__" + json.dumps(output_payload, default=str) + "__ALGO_ARCH_OUTPUT_END__")

if __name__ == "__main__":
    __run_execution()
"""

class SandboxExecutor:
    def __init__(self, timeout_seconds: float = 3.0, memory_limit_mb: float = 512.0):
        self.timeout_seconds = timeout_seconds
        self.memory_limit_mb = memory_limit_mb

    def run(self, code: str, input_data: Any) -> Dict[str, Any]:
        """
        Executes code safely in a separate python3 process.
        """
        # Step 1: AST check
        is_safe, error_msg = inspect_code_ast(code)
        if not is_safe:
            return {
                "passed": False,
                "status": ExecutionStatus.SECURITY_VIOLATION if "Security" in (error_msg or "") else ExecutionStatus.SYNTAX_ERROR,
                "actual_output": None,
                "runtime_ms": 0.0,
                "memory_mb": 0.0,
                "stdout": "",
                "stderr": error_msg or "AST Inspection failed",
                "error_type": "SecurityViolationError" if "Security" in (error_msg or "") else "SyntaxError",
                "error_message": error_msg
            }

        # Step 2: Format runner script
        input_json_str = json.dumps(input_data, default=str)
        script_content = RUNNER_TEMPLATE.format(
            code=code,
            input_json_str=input_json_str
        )

        with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False) as tmp_file:
            tmp_file.write(script_content)
            tmp_path = tmp_file.name

        try:
            # Execute subprocess
            proc = subprocess.Popen(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env={"PYTHONPATH": "."}
            )
            
            try:
                stdout, stderr = proc.communicate(timeout=self.timeout_seconds)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.communicate()
                return {
                    "passed": False,
                    "status": ExecutionStatus.TIMEOUT,
                    "actual_output": None,
                    "runtime_ms": self.timeout_seconds * 1000.0,
                    "memory_mb": None,
                    "stdout": "",
                    "stderr": f"Process exceeded time limit of {self.timeout_seconds}s",
                    "error_type": "TimeoutError",
                    "error_message": f"Execution timed out after {self.timeout_seconds}s"
                }

            # Parse payload
            if "__ALGO_ARCH_OUTPUT_START__" in stdout:
                start_idx = stdout.index("__ALGO_ARCH_OUTPUT_START__") + len("__ALGO_ARCH_OUTPUT_START__")
                end_idx = stdout.index("__ALGO_ARCH_OUTPUT_END__")
                raw_payload = stdout[start_idx:end_idx]
                try:
                    payload = json.loads(raw_payload)
                except Exception as e:
                    return {
                        "passed": False,
                        "status": ExecutionStatus.RUNTIME_ERROR,
                        "actual_output": None,
                        "runtime_ms": 0.0,
                        "memory_mb": None,
                        "stdout": stdout[:2000],
                        "stderr": f"Failed to parse runner output: {e}\n{stderr[:2000]}",
                        "error_type": "RunnerSerializationError",
                        "error_message": str(e)
                    }

                if payload.get("error"):
                    return {
                        "passed": False,
                        "status": ExecutionStatus.RUNTIME_ERROR,
                        "actual_output": None,
                        "runtime_ms": payload.get("runtime_ms", 0.0),
                        "memory_mb": payload.get("memory_mb", 0.0),
                        "stdout": payload.get("stdout", ""),
                        "stderr": payload.get("error", "") + "\n" + stderr[:1000],
                        "error_type": payload.get("error_type", "RuntimeError"),
                        "error_message": payload.get("error")
                    }

                # Check memory limit
                if payload.get("memory_mb", 0) > self.memory_limit_mb:
                    return {
                        "passed": False,
                        "status": ExecutionStatus.MEMORY_LIMIT,
                        "actual_output": payload.get("result"),
                        "runtime_ms": payload.get("runtime_ms", 0.0),
                        "memory_mb": payload.get("memory_mb", 0.0),
                        "stdout": payload.get("stdout", ""),
                        "stderr": f"Memory limit exceeded: {payload.get('memory_mb'):.2f}MB > {self.memory_limit_mb}MB",
                        "error_type": "MemoryLimitExceeded",
                        "error_message": f"Peak memory {payload.get('memory_mb'):.2f}MB exceeded limit {self.memory_limit_mb}MB"
                    }

                return {
                    "passed": True,
                    "status": ExecutionStatus.PASSED,
                    "actual_output": payload.get("result"),
                    "runtime_ms": payload.get("runtime_ms", 0.0),
                    "memory_mb": payload.get("memory_mb", 0.0),
                    "stdout": payload.get("stdout", ""),
                    "stderr": stderr[:1000],
                    "error_type": None,
                    "error_message": None
                }
            else:
                return {
                    "passed": False,
                    "status": ExecutionStatus.RUNTIME_ERROR if proc.returncode != 0 else ExecutionStatus.SYNTAX_ERROR,
                    "actual_output": None,
                    "runtime_ms": 0.0,
                    "memory_mb": None,
                    "stdout": stdout[:2000],
                    "stderr": stderr[:2000] or f"Process exited with code {proc.returncode}",
                    "error_type": "SubprocessCrash",
                    "error_message": stderr[:500] or f"Exit code {proc.returncode}"
                }

        finally:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
