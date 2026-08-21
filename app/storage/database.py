import sqlite3
import json
from pathlib import Path
from typing import Optional
from app.config import config

class Database:
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or config.sqlite_path
        self._init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS experiments (
                id TEXT PRIMARY KEY,
                problem_id TEXT NOT NULL,
                problem_title TEXT NOT NULL,
                current_state TEXT NOT NULL,
                data_json TEXT NOT NULL,
                winner_candidate_id TEXT,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );
            """)
            # Check if problem_title column exists (for migration)
            cursor.execute("PRAGMA table_info(experiments);")
            cols = [row["name"] for row in cursor.fetchall()]
            if "problem_title" not in cols:
                try:
                    cursor.execute("ALTER TABLE experiments ADD COLUMN problem_title TEXT DEFAULT '';")
                except Exception:
                    pass
            if "winner_candidate_id" not in cols:
                try:
                    cursor.execute("ALTER TABLE experiments ADD COLUMN winner_candidate_id TEXT DEFAULT NULL;")
                except Exception:
                    pass

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS benchmark_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                experiment_id TEXT NOT NULL,
                candidate_id TEXT NOT NULL,
                input_size INTEGER NOT NULL,
                runtime_ms REAL NOT NULL,
                memory_mb REAL NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
            );
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                experiment_id TEXT NOT NULL,
                artifact_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL NOT NULL,
                FOREIGN KEY(experiment_id) REFERENCES experiments(id) ON DELETE CASCADE
            );
            """)
            conn.commit()

db = Database()
