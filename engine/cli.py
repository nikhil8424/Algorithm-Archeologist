"""
Command Line & Process Bridge Interface for Algorithm Archaeologist.
Provides JSON-formatted stdout outputs for Express API backend integration.
"""
import sys
import json
import argparse
from engine.models import Experiment, ProblemSpec, AgentState
from engine.database import ExperimentRepository
from engine.orchestrator import ArchaeologyOrchestrator
from engine.tools.problem_analyzer import PRESET_PROBLEMS
from engine.tools.sandbox import SandboxExecutor

def main():
    parser = argparse.ArgumentParser(description="Algorithm Archaeologist Engine CLI")
    subparsers = parser.add_subparsers(dest="command")

    # List presets
    subparsers.add_parser("presets")

    # List experiments
    subparsers.add_parser("list")

    # Create experiment
    create_p = subparsers.add_parser("create")
    create_p.add_argument("--problem", type=str, required=True)
    create_p.add_argument("--candidates", type=int, default=4)
    create_p.add_argument("--iterations", type=int, default=3)
    create_p.add_argument("--auto-run", action="store_true")

    # Run all steps
    run_p = subparsers.add_parser("run-all")
    run_p.add_argument("--id", type=str, required=True)

    # Step single transition
    step_p = subparsers.add_parser("step")
    step_p.add_argument("--id", type=str, required=True)

    # Get experiment
    get_p = subparsers.add_parser("get")
    get_p.add_argument("--id", type=str, required=True)

    # Delete experiment
    del_p = subparsers.add_parser("delete")
    del_p.add_argument("--id", type=str, required=True)

    # Sandbox execute arbitrary code
    sand_p = subparsers.add_parser("sandbox-run")
    sand_p.add_argument("--code", type=str, required=True)
    sand_p.add_argument("--input", type=str, required=True)

    args = parser.parse_args()
    repo = ExperimentRepository()
    orchestrator = ArchaeologyOrchestrator(repo)

    if args.command == "presets":
        print(json.dumps({"status": "success", "presets": PRESET_PROBLEMS}))

    elif args.command == "list":
        exps = repo.list_experiments()
        print(json.dumps({"status": "success", "experiments": exps}))

    elif args.command == "create":
        exp = orchestrator.create_experiment(
            args.problem,
            max_candidates=args.candidates,
            max_iterations=args.iterations
        )
        if args.auto_run:
            exp = orchestrator.run_all(exp)
        print(json.dumps({"status": "success", "experiment": exp.to_dict()}))

    elif args.command == "run-all":
        raw = repo.get_experiment(args.id)
        if not raw:
            print(json.dumps({"status": "error", "message": f"Experiment '{args.id}' not found"}))
            sys.exit(1)
        # Reconstruct experiment object
        spec = ProblemSpec.from_dict(raw["problem_spec"])
        exp = Experiment(
            id=raw["id"],
            problem_spec=spec,
            current_state=AgentState(raw["current_state"]),
            max_candidates=raw.get("max_candidates", 4),
            max_iterations=raw.get("max_iterations", 3),
            benchmark_budget_seconds=raw.get("benchmark_budget_seconds", 15.0),
            created_at=raw.get("created_at", 0),
            updated_at=raw.get("updated_at", 0)
        )
        # run orchestrator to completion
        exp = orchestrator.run_all(exp)
        print(json.dumps({"status": "success", "experiment": exp.to_dict()}))

    elif args.command == "step":
        raw = repo.get_experiment(args.id)
        if not raw:
            print(json.dumps({"status": "error", "message": f"Experiment '{args.id}' not found"}))
            sys.exit(1)
        spec = ProblemSpec.from_dict(raw["problem_spec"])
        exp = Experiment(
            id=raw["id"],
            problem_spec=spec,
            current_state=AgentState(raw["current_state"]),
            max_candidates=raw.get("max_candidates", 4),
            max_iterations=raw.get("max_iterations", 3),
            benchmark_budget_seconds=raw.get("benchmark_budget_seconds", 15.0),
            created_at=raw.get("created_at", 0),
            updated_at=raw.get("updated_at", 0)
        )
        exp = orchestrator.run_next_step(exp)
        print(json.dumps({"status": "success", "experiment": exp.to_dict()}))

    elif args.command == "get":
        raw = repo.get_experiment(args.id)
        if not raw:
            print(json.dumps({"status": "error", "message": f"Experiment '{args.id}' not found"}))
            sys.exit(1)
        print(json.dumps({"status": "success", "experiment": raw}))

    elif args.command == "delete":
        ok = repo.delete_experiment(args.id)
        print(json.dumps({"status": "success", "deleted": ok}))

    elif args.command == "sandbox-run":
        sandbox = SandboxExecutor()
        try:
            in_data = json.loads(args.input)
        except Exception:
            in_data = args.input
        res = sandbox.run(args.code, in_data)
        print(json.dumps({"status": "success", "result": res}))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
