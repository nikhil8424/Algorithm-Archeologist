import json
import time
from typing import List, Optional
from app.storage.database import db
from app.models.experiment import Experiment, PipelineStage, TimelineEvent, FinalReport, EvolutionStep
from app.models.problem import ProblemSpec, ProblemFamily
from app.models.candidate import AlgorithmCandidate, Complexity, CandidateOrigin
from app.models.testcase import TestCase, TestCategory, TestResult, TestStatus
from app.models.results import BenchmarkResult, CriticVerdict, DiagnosisAction

class ExperimentRepository:
    def __init__(self):
        self.db = db

    def save(self, experiment: Experiment) -> None:
        experiment.updated_at = time.time()
        data_json = experiment.model_dump_json()
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO experiments (id, problem_id, problem_title, current_state, data_json, winner_candidate_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    current_state = excluded.current_state,
                    data_json = excluded.data_json,
                    winner_candidate_id = excluded.winner_candidate_id,
                    updated_at = excluded.updated_at;
                """,
                (
                    experiment.id,
                    experiment.problem_spec.id,
                    experiment.problem_spec.title,
                    experiment.current_state.value if hasattr(experiment.current_state, "value") else str(experiment.current_state),
                    data_json,
                    experiment.winner_candidate_id,
                    experiment.created_at,
                    experiment.updated_at,
                ),
            )
            conn.commit()

    def get_by_id(self, experiment_id: str) -> Optional[Experiment]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data_json FROM experiments WHERE id = ?", (experiment_id,))
            row = cursor.fetchone()
            if not row:
                return None
            
            data = json.loads(row["data_json"])
            return self._hydrate_experiment(data)

    def _hydrate_experiment(self, d: dict) -> Experiment:
        prob_d = d.get("problem_spec", {})
        prob = ProblemSpec(
            id=prob_d.get("id", ""),
            title=prob_d.get("title", ""),
            description=prob_d.get("description", ""),
            problem_family=ProblemFamily(prob_d.get("problem_family", "array_search")),
            objective=prob_d.get("objective", ""),
            input_signature=prob_d.get("input_signature", {}),
            output_signature=prob_d.get("output_signature", "Any"),
            constraints=prob_d.get("constraints", []),
            theoretical_lower_bound_time=prob_d.get("theoretical_lower_bound_time", "O(N)"),
            theoretical_lower_bound_space=prob_d.get("theoretical_lower_bound_space", "O(1)"),
            tags=prob_d.get("tags", []),
        )

        candidates = []
        for cd in d.get("candidates", []):
            comp_d = cd.get("complexity", {})
            complexity = Complexity(
                time_theoretical=comp_d.get("time_theoretical", "O(N)"),
                space_theoretical=comp_d.get("space_theoretical", "O(1)"),
                time_empirical_fitted=comp_d.get("time_empirical_fitted"),
                space_empirical_fitted=comp_d.get("space_empirical_fitted"),
                asymptotic_constant_factor=comp_d.get("asymptotic_constant_factor", "medium"),
            )
            candidates.append(AlgorithmCandidate(
                id=cd.get("id", ""),
                name=cd.get("name", ""),
                paradigm=cd.get("paradigm", ""),
                strategy_description=cd.get("strategy_description", ""),
                code=cd.get("code", ""),
                origin=CandidateOrigin(cd.get("origin", "initial_plan")),
                generation=cd.get("generation", 0),
                parent_id=cd.get("parent_id"),
                mutation_description=cd.get("mutation_description"),
                complexity=complexity,
                ast_node_count=cd.get("ast_node_count", 0),
                cyclomatic_complexity=cd.get("cyclomatic_complexity", 1),
                passed_correctness=cd.get("passed_correctness", False),
                accuracy_percentage=cd.get("accuracy_percentage", 0.0),
                avg_runtime_ms=cd.get("avg_runtime_ms", 0.0),
                peak_memory_mb=cd.get("peak_memory_mb", 0.0),
                pareto_rank=cd.get("pareto_rank", 999),
                pareto_composite_score=cd.get("pareto_composite_score", 0.0),
                is_pareto_optimal=cd.get("is_pareto_optimal", False),
                is_winner=cd.get("is_winner", False),
            ))

        test_cases = []
        for td in d.get("test_cases", []):
            test_cases.append(TestCase(
                id=td.get("id", ""),
                name=td.get("name", ""),
                category=TestCategory(td.get("category", "normal")),
                description=td.get("description", ""),
                input_payload=td.get("input_payload", {}),
                expected_output=td.get("expected_output"),
                input_size=td.get("input_size", 1),
            ))

        test_results = []
        for tr in d.get("test_results", []):
            test_results.append(TestResult(
                test_id=tr.get("test_id", ""),
                candidate_id=tr.get("candidate_id", ""),
                status=TestStatus(tr.get("status", "PASSED")),
                passed=tr.get("passed", False),
                runtime_ms=tr.get("runtime_ms", 0.0),
                memory_mb=tr.get("memory_mb", 0.0),
                actual_output=tr.get("actual_output"),
                expected_output=tr.get("expected_output"),
                error_message=tr.get("error_message"),
            ))

        benchmarks = []
        for bd in d.get("benchmark_results", []):
            benchmarks.append(BenchmarkResult(
                candidate_id=bd.get("candidate_id", ""),
                input_size=bd.get("input_size", 0),
                scale_label=bd.get("scale_label", ""),
                runtime_ms=bd.get("runtime_ms", 0.0),
                memory_mb=bd.get("memory_mb", 0.0),
                iterations=bd.get("iterations", 1),
                std_dev_ms=bd.get("std_dev_ms", 0.0),
            ))

        verdicts = []
        for vd in d.get("critic_verdicts", []):
            verdicts.append(CriticVerdict(
                candidate_id=vd.get("candidate_id", ""),
                passed_all=vd.get("passed_all", False),
                failure_category=vd.get("failure_category"),
                root_cause_explanation=vd.get("root_cause_explanation", ""),
                recommended_action=DiagnosisAction(vd.get("recommended_action", "ACCEPT")),
                patch_instructions=vd.get("patch_instructions"),
                suggested_code=vd.get("suggested_code"),
            ))

        timeline = []
        for tm in d.get("timeline", []):
            timeline.append(TimelineEvent(
                id=tm.get("id", ""),
                stage=PipelineStage(tm.get("stage", "idle")),
                agent_name=tm.get("agent_name", ""),
                action=tm.get("action", ""),
                details=tm.get("details", ""),
                timestamp=tm.get("timestamp", time.time()),
                metadata=tm.get("metadata", {}),
            ))

        evolution = []
        for ev in d.get("evolution_history", []):
            evolution.append(EvolutionStep(
                generation=ev.get("generation", 1),
                parent_id=ev.get("parent_id", ""),
                child_id=ev.get("child_id", ""),
                mutation_type=ev.get("mutation_type", ""),
                description=ev.get("description", ""),
                fitness_delta_pct=ev.get("fitness_delta_pct", 0.0),
            ))

        report = None
        if d.get("final_report"):
            fr = d["final_report"]
            report = FinalReport(
                executive_summary=fr.get("executive_summary", ""),
                theoretical_vs_empirical_synthesis=fr.get("theoretical_vs_empirical_synthesis", ""),
                winning_candidate_id=fr.get("winning_candidate_id", ""),
                winning_candidate_name=fr.get("winning_candidate_name", ""),
                pareto_tradeoff_analysis=fr.get("pareto_tradeoff_analysis", ""),
                production_recommendations=fr.get("production_recommendations", ""),
                markdown_content=fr.get("markdown_content", ""),
                pathological_cases_identified=fr.get("pathological_cases_identified", []),
                created_at=fr.get("created_at", time.time()),
            )

        return Experiment(
            id=d.get("id", ""),
            problem_spec=prob,
            current_state=PipelineStage(d.get("current_state", "idle")),
            candidates=candidates,
            test_cases=test_cases,
            test_results=test_results,
            benchmark_results=benchmarks,
            critic_verdicts=verdicts,
            evolution_history=evolution,
            winner_candidate_id=d.get("winner_candidate_id"),
            final_report=report,
            timeline=timeline,
            created_at=d.get("created_at", time.time()),
            updated_at=d.get("updated_at", time.time()),
        )

    def list_all(self, limit: int = 50) -> List[dict]:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, problem_id, problem_title, current_state, winner_candidate_id, created_at, updated_at, data_json
                FROM experiments
                ORDER BY updated_at DESC
                LIMIT ?
                """,
                (limit,),
            )
            rows = cursor.fetchall()
            results = []
            for r in rows:
                try:
                    data = json.loads(r["data_json"])
                    candidates_count = len(data.get("candidates", []))
                except Exception:
                    candidates_count = 0
                results.append({
                    "id": r["id"],
                    "problem_id": r["problem_id"],
                    "problem_title": r["problem_title"],
                    "current_state": r["current_state"],
                    "winner_candidate_id": r["winner_candidate_id"],
                    "candidate_count": candidates_count,
                    "created_at": r["created_at"],
                    "updated_at": r["updated_at"],
                })
            return results

    def delete(self, experiment_id: str) -> bool:
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
            conn.commit()
            return cursor.rowcount > 0

experiment_repo = ExperimentRepository()
