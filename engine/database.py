"""
SQLite Database and Storage Layer for Algorithm Archaeologist.
Provides thread-safe persistence and querying of experiments, candidate lineages,
test outcomes, empirical benchmarks, and agent timeline telemetry.
"""
import sqlite3
import json
import os
import time
from typing import List, Dict, Any, Optional
from engine.models import (
    Experiment, ProblemSpec, CandidateAlgorithm, TestCase,
    TestResult, BenchmarkResult, CriticReview, TimelineEvent, AgentState
)

DB_PATH = os.environ.get("DATABASE_PATH", "experiments.db")

def get_db_connection(db_path: str = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=30.0)
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path: str = DB_PATH):
    conn = get_db_connection(db_path)
    cur = conn.cursor()
    
    cur.execute("""
    CREATE TABLE IF NOT EXISTS experiments (
        id TEXT PRIMARY KEY,
        problem_id TEXT NOT NULL,
        title TEXT NOT NULL,
        problem_family TEXT NOT NULL,
        current_state TEXT NOT NULL,
        winner_candidate_id TEXT,
        created_at REAL NOT NULL,
        updated_at REAL NOT NULL,
        raw_json TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candidates (
        id TEXT PRIMARY KEY,
        experiment_id TEXT NOT NULL,
        problem_id TEXT NOT NULL,
        name TEXT NOT NULL,
        paradigm TEXT NOT NULL,
        complexity_time TEXT NOT NULL,
        complexity_space TEXT NOT NULL,
        version INTEGER NOT NULL DEFAULT 1,
        parent_candidate_id TEXT,
        status TEXT NOT NULL,
        correctness_score REAL DEFAULT 0,
        median_runtime_ms REAL,
        peak_memory_mb REAL,
        simplicity_score REAL DEFAULT 0.8,
        composite_score REAL,
        is_pareto_optimal INTEGER DEFAULT 0,
        code TEXT NOT NULL,
        raw_json TEXT NOT NULL,
        FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS test_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_id TEXT NOT NULL,
        candidate_id TEXT NOT NULL,
        test_id TEXT NOT NULL,
        category TEXT NOT NULL,
        passed INTEGER NOT NULL,
        status TEXT NOT NULL,
        runtime_ms REAL NOT NULL,
        memory_mb REAL,
        error_type TEXT,
        error_message TEXT,
        FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS benchmarks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        experiment_id TEXT NOT NULL,
        candidate_id TEXT NOT NULL,
        input_size INTEGER NOT NULL,
        median_runtime_ms REAL NOT NULL,
        min_runtime_ms REAL NOT NULL,
        max_runtime_ms REAL NOT NULL,
        memory_mb REAL,
        trials INTEGER NOT NULL,
        raw_times_json TEXT,
        FOREIGN KEY (experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

class ExperimentRepository:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        init_db(self.db_path)

    def save_experiment(self, exp: Experiment):
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        now = time.time()
        exp.updated_at = now
        
        raw_json = json.dumps(exp.to_dict())
        state_val = exp.current_state.value if hasattr(exp.current_state, "value") else str(exp.current_state)

        cur.execute("""
        INSERT INTO experiments (id, problem_id, title, problem_family, current_state, winner_candidate_id, created_at, updated_at, raw_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            current_state = excluded.current_state,
            winner_candidate_id = excluded.winner_candidate_id,
            updated_at = excluded.updated_at,
            raw_json = excluded.raw_json
        """, (
            exp.id,
            exp.problem_spec.id,
            exp.problem_spec.title,
            exp.problem_spec.problem_family,
            state_val,
            exp.winner_candidate_id,
            exp.created_at,
            exp.updated_at,
            raw_json
        ))

        # Save or update candidates
        for c in exp.candidates:
            c_json = json.dumps(c.to_dict())
            cur.execute("""
            INSERT INTO candidates (
                id, experiment_id, problem_id, name, paradigm, complexity_time, complexity_space,
                version, parent_candidate_id, status, correctness_score, median_runtime_ms,
                peak_memory_mb, simplicity_score, composite_score, is_pareto_optimal, code, raw_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                version = excluded.version,
                status = excluded.status,
                correctness_score = excluded.correctness_score,
                median_runtime_ms = excluded.median_runtime_ms,
                peak_memory_mb = excluded.peak_memory_mb,
                composite_score = excluded.composite_score,
                is_pareto_optimal = excluded.is_pareto_optimal,
                code = excluded.code,
                raw_json = excluded.raw_json
            """, (
                c.id, exp.id, c.problem_id, c.name, c.paradigm, c.complexity_time, c.complexity_space,
                c.version, c.parent_candidate_id, c.status, c.correctness_score, c.median_runtime_ms,
                c.peak_memory_mb, c.simplicity_score, c.composite_score, 1 if c.is_pareto_optimal else 0,
                c.code, c_json
            ))

        conn.commit()
        conn.close()

    def get_experiment(self, experiment_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT raw_json FROM experiments WHERE id = ?", (experiment_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return json.loads(row["raw_json"])
        return None

    def list_experiments(self) -> List[Dict[str, Any]]:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("""
        SELECT id, problem_id, title, problem_family, current_state, winner_candidate_id, created_at, updated_at
        FROM experiments
        ORDER BY created_at DESC
        """)
        rows = cur.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def delete_experiment(self, experiment_id: str) -> bool:
        conn = get_db_connection(self.db_path)
        cur = conn.cursor()
        cur.execute("DELETE FROM experiments WHERE id = ?", (experiment_id,))
        cur.execute("DELETE FROM candidates WHERE experiment_id = ?", (experiment_id,))
        cur.execute("DELETE FROM test_results WHERE experiment_id = ?", (experiment_id,))
        cur.execute("DELETE FROM benchmarks WHERE experiment_id = ?", (experiment_id,))
        conn.commit()
        conn.close()
        return True
