import sys
import json
import time
import argparse
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from typing import Optional, Dict, Any, List

from app.config import config, EXPERIMENTS_DIR, REPORTS_DIR
from app.models.experiment import Experiment, PipelineStage, TimelineEvent, EvolutionStep
from app.models.problem import ProblemSpec
from app.models.candidate import AlgorithmCandidate
from app.storage.repositories import experiment_repo
from app.tools.problem_analyzer import problem_analyzer
from app.tools.test_generator import test_generator
from app.tools.benchmark import benchmark_runner
from app.tools.executor import code_executor
from app.tools.sandbox import validate_code_safety
from app.agents.planner import planner_agent
from app.agents.coder import coder_agent
from app.agents.tester import tester_agent
from app.agents.critic import critic_agent
from app.agents.selector import selector_agent
from app.agents.reporter import reporter_agent
from app.evaluation.evaluator import candidate_evaluator

class ArchaeologistOrchestrator:
    """Master State Machine Orchestrator for the Algorithm Archaeologist discovery engine."""

    def create_experiment(self, problem_input: str, candidates_count: int = 4) -> Experiment:
        problem = problem_analyzer.get_preset_problem(problem_input)
        exp_id = f"exp-{int(time.time())}-{problem.id}"

        exp = Experiment(
            id=exp_id,
            problem_spec=problem,
            current_state=PipelineStage.ANALYZE,
        )

        exp.timeline.append(TimelineEvent(
            id=f"evt-{len(exp.timeline)+1}",
            stage=PipelineStage.ANALYZE,
            agent_name="ProblemAnalyzer",
            action="Problem Ingestion & Boundary Analysis",
            details=f"Analyzed problem '{problem.title}' belonging to family '{problem.problem_family.value}'.",
        ))

        experiment_repo.save(exp)
        return exp

    def step(self, experiment_id: str) -> Experiment:
        exp = experiment_repo.get_by_id(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")

        state = exp.current_state

        if state == PipelineStage.ANALYZE:
            exp.current_state = PipelineStage.PLAN
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.PLAN,
                agent_name="PlannerAgent",
                action="Algorithmic Paradigm Decomposition",
                details="Decomposing algorithm solution space into asymptotic paradigms.",
            ))

        elif state == PipelineStage.PLAN:
            plans = planner_agent.plan_paradigms(exp.problem_spec, config.default_candidates_count)
            # Generate code for planned paradigms
            candidates = coder_agent.synthesize_candidates(exp.problem_spec, plans)
            exp.candidates = candidates
            exp.current_state = PipelineStage.GENERATE
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.GENERATE,
                agent_name="CoderAgent",
                action="Candidate Code Synthesis",
                details=f"Synthesized {len(candidates)} distinct algorithm candidate implementations.",
            ))

        elif state == PipelineStage.GENERATE:
            # Generate 7-category adversarial test suite
            tests = test_generator.generate_suite(exp.problem_spec)
            exp.test_cases = tests
            exp.current_state = PipelineStage.VALIDATE
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.VALIDATE,
                agent_name="TestGenerator",
                action="Adversarial Test Suite Generation",
                details=f"Generated {len(tests)} multi-category test cases (Normal, Edge, Boundary, Adversarial Traps, Metamorphic).",
            ))

        elif state == PipelineStage.VALIDATE:
            # Execute candidates against test cases
            results = tester_agent.test_candidates(exp.candidates, exp.test_cases)
            exp.test_results = results
            exp.current_state = PipelineStage.TEST
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.TEST,
                agent_name="TesterAgent",
                action="Adversarial Fuzzing & Execution",
                details=f"Executed {len(results)} total candidate-test pairs inside isolated sandboxes.",
            ))

        elif state == PipelineStage.TEST:
            # Run empirical multi-scale stress benchmarks
            all_benchmarks = []
            for c in exp.candidates:
                b_res = benchmark_runner.run_benchmarks(c, exp.problem_spec)
                all_benchmarks.extend(b_res)
            exp.benchmark_results = all_benchmarks

            # Evaluate metrics & Pareto scores
            exp.candidates = candidate_evaluator.evaluate_candidates(
                exp.candidates, exp.test_results, exp.benchmark_results
            )

            exp.current_state = PipelineStage.BENCHMARK
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.BENCHMARK,
                agent_name="BenchmarkRunner",
                action="Multi-Scale Empirical Benchmarking",
                details=f"Completed empirical stress benchmarks up to scale N=20,000+.",
            ))

        elif state == PipelineStage.BENCHMARK:
            # Critic diagnosis
            verdicts = critic_agent.critique_and_diagnose(exp.candidates, exp.test_results, exp.test_cases)
            exp.critic_verdicts = verdicts
            exp.current_state = PipelineStage.CRITIQUE
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.CRITIQUE,
                agent_name="CriticAgent",
                action="Adversarial Failure Diagnosis",
                details=f"Classified failure modes and identified pathological traps.",
            ))

        elif state == PipelineStage.CRITIQUE:
            # Evolution and genetic repairs if needed
            evolved = []
            for v in exp.critic_verdicts:
                if not v.passed_all and v.suggested_code:
                    parent = next((c for c in exp.candidates if c.id == v.candidate_id), None)
                    if parent:
                        child = critic_agent.evolve_candidate(parent, v)
                        evolved.append(child)
                        exp.evolution_history.append(EvolutionStep(
                            generation=1,
                            parent_id=parent.id,
                            child_id=child.id,
                            mutation_type="AST_PARADIGM_REPAIR",
                            description=v.patch_instructions or "Repaired failure mode",
                            fitness_delta_pct=100.0,
                        ))

            if evolved:
                # Test evolved candidates
                new_results = tester_agent.test_candidates(evolved, exp.test_cases)
                exp.test_results.extend(new_results)
                for child in evolved:
                    b_res = benchmark_runner.run_benchmarks(child, exp.problem_spec)
                    exp.benchmark_results.extend(b_res)
                exp.candidates.extend(evolved)

                # Re-evaluate all candidates
                exp.candidates = candidate_evaluator.evaluate_candidates(
                    exp.candidates, exp.test_results, exp.benchmark_results
                )

            exp.current_state = PipelineStage.EVOLVE
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.EVOLVE,
                agent_name="CriticAgent",
                action="Genetic AST Mutation & Evolution",
                details=f"Evolved {len(evolved)} offspring candidates with AST mutation fixes.",
            ))

        elif state == PipelineStage.EVOLVE:
            # Select Pareto champion
            champion = selector_agent.select_champion(exp.candidates)
            exp.winner_candidate_id = champion.id if champion else None
            exp.current_state = PipelineStage.SELECT
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.SELECT,
                agent_name="SelectorAgent",
                action="Multi-Objective Pareto Selection",
                details=f"Selected champion candidate: '{champion.name if champion else 'None'}'.",
            ))

        elif state == PipelineStage.SELECT:
            # Generate final explainable research report
            champion = next((c for c in exp.candidates if c.id == exp.winner_candidate_id), None)
            report = reporter_agent.generate_report(exp.problem_spec, exp.candidates, champion, exp.critic_verdicts)
            exp.final_report = report
            exp.current_state = PipelineStage.DONE
            exp.timeline.append(TimelineEvent(
                id=f"evt-{len(exp.timeline)+1}",
                stage=PipelineStage.DONE,
                agent_name="ReporterAgent",
                action="Explainable Research Synthesis Export",
                details="Generated comprehensive research synthesis report.",
            ))

            # Save report to reports/ directory
            try:
                report_file = REPORTS_DIR / f"{exp.id}_report.md"
                report_file.write_text(report.markdown_content, encoding="utf-8")
                
                exp_file = EXPERIMENTS_DIR / f"{exp.id}.json"
                exp_file.write_text(exp.model_dump_json(indent=2), encoding="utf-8")
            except Exception:
                pass

        experiment_repo.save(exp)
        return exp

    def run_all(self, experiment_id: str) -> Experiment:
        exp = experiment_repo.get_by_id(experiment_id)
        if not exp:
            raise ValueError(f"Experiment {experiment_id} not found")

        max_steps = 15
        while exp.current_state != PipelineStage.DONE and max_steps > 0:
            exp = self.step(exp.id)
            max_steps -= 1

        return exp

orchestrator = ArchaeologistOrchestrator()

# ----------------- CLI ROUTER & ENTRYPOINT -----------------
def main():
    parser = argparse.ArgumentParser(description="Algorithm Archaeologist Discovery Engine")
    subparsers = parser.add_subparsers(dest="command")

    # Command: create
    create_parser = subparsers.add_parser("create", help="Create new experiment")
    create_parser.add_argument("--problem", type=str, default="shortest-path-100k", help="Problem ID or description")
    create_parser.add_argument("--candidates", type=int, default=4, help="Candidate count")
    create_parser.add_argument("--auto-run", action="store_true", help="Run through all stages immediately")

    # Command: step
    step_parser = subparsers.add_parser("step", help="Step experiment forward")
    step_parser.add_argument("id", type=str, help="Experiment ID")

    # Command: run-all
    run_parser = subparsers.add_parser("run-all", help="Run experiment to completion")
    run_parser.add_argument("id", type=str, help="Experiment ID")

    # Command: get
    get_parser = subparsers.add_parser("get", help="Get experiment by ID")
    get_parser.add_argument("id", type=str, help="Experiment ID")

    # Command: list
    subparsers.add_parser("list", help="List all experiments")

    # Command: delete
    del_parser = subparsers.add_parser("delete", help="Delete experiment")
    del_parser.add_argument("id", type=str, help="Experiment ID")

    # Command: sandbox-run
    sandbox_parser = subparsers.add_parser("sandbox-run", help="Run snippet inside sandbox")
    sandbox_parser.add_argument("--code", type=str, required=True, help="Python code defining def solve(...)")
    sandbox_parser.add_argument("--input", type=str, default="{}", help="JSON input payload")

    # Command: presets
    subparsers.add_parser("presets", help="List preset problems")

    args = parser.parse_args()

    if args.command == "create":
        exp = orchestrator.create_experiment(args.problem, args.candidates)
        if args.auto_run:
            exp = orchestrator.run_all(exp.id)
        print(json.dumps({"success": True, "experiment": exp.model_dump()}))

    elif args.command == "step":
        exp = orchestrator.step(args.id)
        print(json.dumps({"success": True, "experiment": exp.model_dump()}))

    elif args.command == "run-all":
        exp = orchestrator.run_all(args.id)
        print(json.dumps({"success": True, "experiment": exp.model_dump()}))

    elif args.command == "get":
        exp = experiment_repo.get_by_id(args.id)
        if exp:
            print(json.dumps({"success": True, "experiment": exp.model_dump()}))
        else:
            print(json.dumps({"error": f"Experiment {args.id} not found"}), file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        exps = experiment_repo.list_all()
        print(json.dumps({"success": True, "experiments": exps}))

    elif args.command == "delete":
        deleted = experiment_repo.delete(args.id)
        print(json.dumps({"success": deleted}))

    elif args.command == "sandbox-run":
        try:
            payload = json.loads(args.input)
        except Exception:
            payload = {}
        res = code_executor.execute(args.code, payload)
        print(json.dumps({"success": True, "result": res}))

    elif args.command == "presets":
        presets = [p.model_dump() for p in problem_analyzer.list_preset_problems()]
        print(json.dumps({"success": True, "presets": presets}))

    else:
        # Default: list presets or help
        presets = [p.model_dump() for p in problem_analyzer.list_preset_problems()]
        print(json.dumps({"message": "Algorithm Archaeologist CLI active", "presets": presets}))

if __name__ == "__main__":
    main()
