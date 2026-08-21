import subprocess
import json
import time
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from app.config import config
from app.tools.sandbox import validate_code_safety
from app.models.testcase import TestStatus

DRIVER_WRAPPER_TEMPLATE = """
import sys
import json
import time
import tracemalloc

# Inject Algorithm Code
{ALGO_CODE}

def _run_driver():
    input_kwargs = {INPUT_JSON}
    
    tracemalloc.start()
    start_time = time.perf_counter()
    
    try:
        if isinstance(input_kwargs, dict):
            res = solve(**input_kwargs)
        else:
            res = solve(input_kwargs)
            
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        peak_mb = peak / (1024.0 * 1024.0)
        
        output_payload = {
            "status": "PASSED",
            "result": res,
            "runtime_ms": elapsed_ms,
            "memory_mb": peak_mb
        }
        print("___OUTPUT_DELIMITER___")
        print(json.dumps(output_payload))
    except Exception as e:
        tracemalloc.stop()
        output_payload = {
            "status": "CRASH",
            "error": str(e),
            "error_type": type(e).__name__
        }
        print("___OUTPUT_DELIMITER___")
        print(json.dumps(output_payload))

if __name__ == "__main__":
    _run_driver()
"""

class CodeExecutor:
    def __init__(self, timeout_sec: float = None, max_memory_mb: float = None):
        self.timeout = timeout_sec or config.sandbox_timeout_seconds
        self.max_memory_mb = max_memory_mb or config.sandbox_max_memory_mb

    def execute(self, code: str, input_payload: Any) -> Dict[str, Any]:
        """Execute algorithm code inside an isolated sandbox subprocess."""
        # 1. AST Static Security Gatekeeper
        is_safe, violations = validate_code_safety(code)
        if not is_safe:
            return {
                "passed": False,
                "status": TestStatus.SECURITY_VIOLATION,
                "runtime_ms": 0.0,
                "memory_mb": 0.0,
                "actual_output": None,
                "error_message": f"Security violation: {'; '.join(violations)}",
            }

        # 2. Prepare isolated driver script
        input_json_str = json.dumps(input_payload)
        script_content = DRIVER_WRAPPER_TEMPLATE.replace("{ALGO_CODE}", code).replace("{INPUT_JSON}", input_json_str)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(script_content)
            temp_path = f.name

        try:
            start_proc = time.perf_counter()
            proc = subprocess.run(
                ["python3", temp_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            total_wall_ms = (time.perf_counter() - start_proc) * 1000.0

            if proc.returncode != 0 and not proc.stdout:
                return {
                    "passed": False,
                    "status": TestStatus.CRASH,
                    "runtime_ms": total_wall_ms,
                    "memory_mb": 0.0,
                    "actual_output": None,
                    "error_message": f"Process exited with code {proc.returncode}: {proc.stderr.strip()}",
                }

            if "___OUTPUT_DELIMITER___" in proc.stdout:
                raw_out = proc.stdout.split("___OUTPUT_DELIMITER___")[-1].strip()
                parsed = json.loads(raw_out)
                if parsed.get("status") == "PASSED":
                    return {
                        "passed": True,
                        "status": TestStatus.PASSED,
                        "runtime_ms": parsed.get("runtime_ms", total_wall_ms),
                        "memory_mb": parsed.get("memory_mb", 0.1),
                        "actual_output": parsed.get("result"),
                        "error_message": None,
                    }
                else:
                    return {
                        "passed": False,
                        "status": TestStatus.CRASH,
                        "runtime_ms": total_wall_ms,
                        "memory_mb": 0.0,
                        "actual_output": None,
                        "error_message": f"{parsed.get('error_type')}: {parsed.get('error')}",
                    }
            else:
                return {
                    "passed": False,
                    "status": TestStatus.CRASH,
                    "runtime_ms": total_wall_ms,
                    "memory_mb": 0.0,
                    "actual_output": None,
                    "error_message": proc.stderr or proc.stdout,
                }

        except subprocess.TimeoutExpired:
            return {
                "passed": False,
                "status": TestStatus.TLE,
                "runtime_ms": self.timeout * 1000.0,
                "memory_mb": 0.0,
                "actual_output": None,
                "error_message": f"Execution timed out after {self.timeout}s limit.",
            }
        except Exception as e:
            return {
                "passed": False,
                "status": TestStatus.CRASH,
                "runtime_ms": 0.0,
                "memory_mb": 0.0,
                "actual_output": None,
                "error_message": str(e),
            }
        finally:
            try:
                Path(temp_path).unlink(missing_ok=True)
            except Exception:
                pass

code_executor = CodeExecutor()
