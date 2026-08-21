"""
Master Agentic State Machine Orchestrator for Algorithm Archaeologist.
Drives the explicit state lifecycle:
ANALYZE -> PLAN -> GENERATE -> VALIDATE -> TEST -> BENCHMARK -> CRITIQUE -> REPAIR -> EVOLVE -> SELECT -> REPORT -> DONE
Logs all transitions, persists state to SQLite, and coordinates agents and tools.
"""
import uuid
import time
from typing import Optional, Dict, Any, List
from engine.models import (
    Experiment, ProblemSpec, CandidateAlgorithm, TestCase,
    TestResult, BenchmarkResult, CriticReview, TimelineEvent,
    AgentState, ExecutionStatus, CriticAction, TestCategory
)
from engine.database import ExperimentRepository
from engine.tools.problem_analyzer import analyze_problem_statement
from engine.agents.planner import plan_strategies_for_problem
from engine.agents.coder import generate_code_for_candidate
from engine.tools.sandbox import SandboxExecutor, inspect_code_ast
from engine.tools.test_generator import generate_test_suite_for_problem
from engine.tools.oracle import compute_reference_output, check_outputs_match
from engine.tools.benchmark import BenchmarkEngine
from engine.tools.complexity import assess_empirical_scaling, analyze_ast_nesting
from engine.agents.critic import CriticAgent
from engine.agents.repair import repair_candidate
from engine.agents.evolver import evolve_generation
from engine.agents.selector import evaluate_and_rank_candidates
from engine.agents.reporter import generate_archaeology_report

class ArchaeologyOrchestrator:
    def __init__(self, repo: ExperimentRepository = None):
        self.repo = repo or ExperimentRepository()
        self.sandbox = SandboxExecutor(timeout_seconds=3.5, memory_limit_mb=512.0)
        self.benchmarker = BenchmarkEngine(self.sandbox)
        self.critic = CriticAgent()

    def create_experiment(
        self,
        problem_input: str,
        max_candidates: int = 4,
        max_iterations: int = 3,
        benchmark_budget_seconds: float = 15.0
    ) -> Experiment:
        """Initializes a new archaeology experiment."""
        spec = analyze_problem_statement(problem_input)
        exp_id = f"exp_{uuid.uuid4().hex[:8]}"

        exp = Experiment(
            id=exp_id,
            problem_spec=spec,
            current_state=AgentState.ANALYZE,
            max_candidates=max_candidates,
            max_iterations=max_iterations,
            benchmark_budget_seconds=benchmark_budget_seconds
        )

        self._add_timeline(
            exp,
            AgentState.ANALYZE,
            "Problem Analyzed",
            f"Identified family '{spec.problem_family}' with {len(spec.constraints)} constraints and {len(spec.candidate_paradigms)} viable paradigms.",
            level="success",
            metadata={"spec": spec.to_dict()}
        )

        self.repo.save_experiment(exp)
        return exp

    def _add_timeline(self, exp: Experiment, state: AgentState, title: str, detail: str, level: str = "info", metadata: Dict[str, Any] = None):
        evt = TimelineEvent(
            id=f"evt_{uuid.uuid4().hex[:6]}",
            timestamp=time.time(),
            state=state,
            title=title,
            detail=detail,
            level=level,
            metadata=metadata or {}
        )
        exp.timeline.append(evt)
        exp.updated_at = time.time()

    def run_next_step(self, exp: Experiment) -> Experiment:
        """Executes a single step in the state machine."""
        state = exp.current_state

        if state == AgentState.ANALYZE:
            # Transition to PLAN
            exp.current_state = AgentState.PLAN
            candidates = plan_strategies_for_problem(exp.problem_spec, exp.max_candidates)
            exp.candidates = candidates
            self._add_timeline(
                exp,
                AgentState.PLAN,
                f"Generated {len(candidates)} Algorithmic Strategies",
                f"Proposed distinct paradigms: {', '.join([c.paradigm for c in candidates])}",
                level="success"
            )

        elif state == AgentState.PLAN:
            # Transition to GENERATE
            exp.current_state = AgentState.GENERATE
            for c in exp.candidates:
                c.code = generate_code_for_candidate(c, exp.problem_spec)
                c.status = "GENERATED"
            self._add_timeline(
                exp,
                AgentState.GENERATE,
                "Synthesized Candidate Implementations",
                f"Generated Python solve(...) implementations for all {len(exp.candidates)} candidates.",
                level="info"
            )

        elif state == AgentState.GENERATE:
            # Transition to VALIDATE
            exp.current_state = AgentState.VALIDATE
            all_valid = True
            for c in exp.candidates:
                is_safe, error_msg = inspect_code_ast(c.code)
                if not is_safe:
                    c.status = "SYNTAX_ERROR"
                    all_valid = False
                    self._add_timeline(
                        exp,
                        AgentState.VALIDATE,
                        f"AST Validation Failed for {c.name}",
                        error_msg or "AST Parse error",
                        level="error"
                    )
                else:
                    c.status = "VALIDATED"
            
            if all_valid:
                self._add_timeline(
                    exp,
                    AgentState.VALIDATE,
                    "Static AST Validation Passed",
                    "All candidate source codes strictly passed sandbox security and syntax checks.",
                    level="success"
                )

        elif state == AgentState.VALIDATE:
            # Transition to TEST
            exp.current_state = AgentState.TEST
            test_suite = generate_test_suite_for_problem(exp.problem_spec)
            exp.test_cases = test_suite
            exp.test_results = []

            for c in exp.candidates:
                passed_cnt = 0
                for t in test_suite:
                    run_res = self.sandbox.run(c.code, t.input_data)
                    is_match = False
                    
                    if run_res["passed"]:
                        expected = t.expected_output
                        if expected is None:
                            expected = compute_reference_output(exp.problem_spec.problem_family, t.input_data)
                        is_match = check_outputs_match(run_res["actual_output"], expected)
                        if is_match:
                            passed_cnt += 1
                        else:
                            run_res["status"] = ExecutionStatus.WRONG_ANSWER
                            run_res["error_message"] = f"Expected {expected}, got {run_res['actual_output']}"
                    
                    t_res = TestResult(
                        candidate_id=c.id,
                        test_id=t.id,
                        passed=is_match,
                        status=run_res["status"],
                        runtime_ms=run_res["runtime_ms"],
                        memory_mb=run_res["memory_mb"],
                        stdout=run_res["stdout"],
                        stderr=run_res["stderr"],
                        actual_output=run_res["actual_output"],
                        expected_output=t.expected_output,
                        error_type=run_res["error_type"],
                        error_message=run_res["error_message"],
                        category=t.category.value if hasattr(t.category, "value") else str(t.category),
                        description=t.description
                    )
                    exp.test_results.append(t_res)

                c.passed_tests = passed_cnt
                c.total_tests = len(test_suite)
                c.correctness_score = round(passed_cnt / max(1, len(test_suite)), 3)
                c.status = "PASSED" if passed_cnt == len(test_suite) else "FAILED"

                lvl = "success" if passed_cnt == len(test_suite) else "warning"
                self._add_timeline(
                    exp,
                    AgentState.TEST,
                    f"Test Suite Executed: {c.name}",
                    f"Passed {passed_cnt}/{len(test_suite)} tests ({c.correctness_score * 100:.1f}%).",
                    level=lvl
                )

        elif state == AgentState.TEST:
            # Transition to BENCHMARK
            exp.current_state = AgentState.BENCHMARK
            exp.benchmark_results = []

            for c in exp.candidates:
                benchmarks = self.benchmarker.benchmark_candidate(c, exp.problem_spec)
                exp.benchmark_results.extend(benchmarks)
                c.empirical_complexity_assessment = assess_empirical_scaling(benchmarks, c.complexity_time)

            self._add_timeline(
                exp,
                AgentState.BENCHMARK,
                "Deterministic Empirical Benchmarks Complete",
                f"Benchmarked all candidates across scaling input sizes up to 50k+ elements.",
                level="success"
            )

        elif state == AgentState.BENCHMARK:
            # Transition to CRITIQUE
            exp.current_state = AgentState.CRITIQUE
            exp.critic_reviews = []
            needs_repair = False

            for c in exp.candidates:
                review = self.critic.critique(c, exp.test_results, exp.benchmark_results, exp.problem_spec)
                exp.critic_reviews.append(review)
                
                lvl = "success" if review.action == CriticAction.ACCEPT else ("error" if review.action == CriticAction.DISCARD else "warning")
                self._add_timeline(
                    exp,
                    AgentState.CRITIQUE,
                    f"Critic Review: {c.name} -> {review.action.value}",
                    review.reason,
                    level=lvl
                )

                if review.action in (CriticAction.REPAIR_CORRECTNESS, CriticAction.OPTIMIZE_PERFORMANCE):
                    needs_repair = True

            # If repairs are recommended and under iteration cap, go to REPAIR, else EVOLVE
            if needs_repair and len([c for c in exp.candidates if c.version > 1]) < exp.max_iterations:
                exp.current_state = AgentState.REPAIR
            else:
                exp.current_state = AgentState.EVOLVE

        elif state == AgentState.REPAIR:
            # Execute repair step
            repaired_candidates = []
            for c in exp.candidates:
                c_reviews = [r for r in exp.critic_reviews if r.candidate_id == c.id]
                if c_reviews and c_reviews[-1].action in (CriticAction.REPAIR_CORRECTNESS, CriticAction.OPTIMIZE_PERFORMANCE):
                    repaired = repair_candidate(c, c_reviews[-1], exp.problem_spec)
                    repaired_candidates.append(repaired)
                    self._add_timeline(
                        exp,
                        AgentState.REPAIR,
                        f"Synthesized Repaired Lineage: {repaired.name}",
                        repaired.explanation,
                        level="info"
                    )

            if repaired_candidates:
                # Add repaired versions and test them immediately
                for rc in repaired_candidates:
                    exp.candidates.append(rc)
                    passed_cnt = 0
                    for t in exp.test_cases:
                        run_res = self.sandbox.run(rc.code, t.input_data)
                        expected = t.expected_output
                        if expected is None:
                            expected = compute_reference_output(exp.problem_spec.problem_family, t.input_data)
                        is_match = check_outputs_match(run_res["actual_output"], expected) if run_res["passed"] else False
                        if is_match:
                            passed_cnt += 1
                        
                        exp.test_results.append(TestResult(
                            candidate_id=rc.id,
                            test_id=t.id,
                            passed=is_match,
                            status=run_res["status"],
                            runtime_ms=run_res["runtime_ms"],
                            memory_mb=run_res["memory_mb"],
                            stdout=run_res["stdout"],
                            stderr=run_res["stderr"],
                            actual_output=run_res["actual_output"],
                            expected_output=expected,
                            error_type=run_res["error_type"],
                            error_message=run_res["error_message"],
                            category=t.category.value if hasattr(t.category, "value") else str(t.category),
                            description=t.description
                        ))
                    rc.passed_tests = passed_cnt
                    rc.total_tests = len(exp.test_cases)
                    rc.correctness_score = round(passed_cnt / max(1, len(exp.test_cases)), 3)
                    rc.status = "PASSED" if passed_cnt == len(exp.test_cases) else "FAILED"

                    # Run benchmark for repaired candidate
                    r_benchmarks = self.benchmarker.benchmark_candidate(rc, exp.problem_spec)
                    exp.benchmark_results.extend(r_benchmarks)
                    rc.empirical_complexity_assessment = assess_empirical_scaling(r_benchmarks, rc.complexity_time)

                    self._add_timeline(
                        exp,
                        AgentState.REPAIR,
                        f"Repaired Candidate Verified: {rc.name}",
                        f"Passed {passed_cnt}/{len(exp.test_cases)} tests post-repair.",
                        level="success" if passed_cnt == len(exp.test_cases) else "warning"
                    )

            exp.current_state = AgentState.EVOLVE

        elif state == AgentState.EVOLVE:
            # Run evolutionary algorithm search module
            evo_logs = evolve_generation(exp.candidates, exp.problem_spec, generation_number=1)
            exp.evolution_history = evo_logs
            self._add_timeline(
                exp,
                AgentState.EVOLVE,
                "Genetic Algorithm Mutation Search",
                f"Evaluated population genome; explored {len(evo_logs)} micro-architectural mutations.",
                level="info"
            )
            exp.current_state = AgentState.SELECT

        elif state == AgentState.SELECT:
            # Multi-objective Pareto Frontier and weighted selection
            ranked_cands, winner = evaluate_and_rank_candidates(exp.candidates, exp.benchmark_results)
            exp.candidates = ranked_cands
            exp.winner_candidate_id = winner.id if winner else None

            if winner:
                self._add_timeline(
                    exp,
                    AgentState.SELECT,
                    f"🏆 Winner Selected: {winner.name}",
                    f"Scored {winner.composite_score:.4f} with non-dominated Pareto optimality and 100% verification.",
                    level="success"
                )
            else:
                self._add_timeline(
                    exp,
                    AgentState.SELECT,
                    "Selection Concluded without Passing Winner",
                    "None of the candidate algorithms met the 100% correctness threshold.",
                    level="warning"
                )

            exp.current_state = AgentState.REPORT

        elif state == AgentState.REPORT:
            # Synthesize final archaeology report
            report = generate_archaeology_report(exp)
            exp.final_report = report
            exp.current_state = AgentState.DONE

            self._add_timeline(
                exp,
                AgentState.DONE,
                "Archaeological Exploration Complete",
                f"Generated comprehensive report with trade-offs, evidence, and mathematical bounds.",
                level="success"
            )

        self.repo.save_experiment(exp)
        return exp

    def run_all(self, exp: Experiment) -> Experiment:
        """Runs the experiment continuously until reaching DONE or STOPPED."""
        while exp.current_state not in (AgentState.DONE, AgentState.FAILED, AgentState.STOPPED):
            exp = self.run_next_step(exp)
        return exp
