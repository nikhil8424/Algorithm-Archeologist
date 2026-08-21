from typing import List
from app.models.candidate import AlgorithmCandidate
from app.models.testcase import TestCase, TestResult, TestStatus
from app.tools.executor import code_executor

class TesterAgent:
    """Archaeological Adversarial Tester: Executes candidates against multi-category fuzz suites."""

    def test_candidates(self, candidates: List[AlgorithmCandidate], test_cases: List[TestCase]) -> List[TestResult]:
        all_results: List[TestResult] = []

        for candidate in candidates:
            for test in test_cases:
                exec_res = code_executor.execute(candidate.code, test.input_payload)
                
                passed = False
                status = exec_res.get("status", TestStatus.CRASH)
                actual_out = exec_res.get("actual_output")
                
                if exec_res.get("passed"):
                    if test.expected_output is not None:
                        if actual_out == test.expected_output:
                            passed = True
                            status = TestStatus.PASSED
                        else:
                            passed = False
                            status = TestStatus.FAILED
                    else:
                        passed = True
                        status = TestStatus.PASSED

                all_results.append(TestResult(
                    test_id=test.id,
                    candidate_id=candidate.id,
                    status=status,
                    passed=passed,
                    runtime_ms=exec_res.get("runtime_ms", 0.0),
                    memory_mb=exec_res.get("memory_mb", 0.0),
                    actual_output=actual_out,
                    expected_output=test.expected_output,
                    error_message=exec_res.get("error_message"),
                ))

        return all_results

tester_agent = TesterAgent()
