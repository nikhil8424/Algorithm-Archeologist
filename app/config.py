import os
from pathlib import Path
from dataclasses import dataclass, field

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIR = BASE_DIR / "app"
EXPERIMENTS_DIR = BASE_DIR / "experiments"
REPORTS_DIR = BASE_DIR / "reports"
SANDBOX_DIR = BASE_DIR / "sandbox"
DATABASE_PATH = BASE_DIR / "experiments.db"

# Ensure runtime directories exist
EXPERIMENTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
SANDBOX_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class Config:
    app_name: str = "Algorithm Archaeologist"
    version: str = "1.0.0"
    database_url: str = f"sqlite:///{DATABASE_PATH}"
    sqlite_path: str = str(DATABASE_PATH)
    
    # Sandbox Limits
    sandbox_timeout_seconds: float = 3.0
    sandbox_max_memory_mb: float = 256.0
    sandbox_strict_ast: bool = True
    
    # Default pipeline settings
    default_candidates_count: int = 4
    benchmark_scales: list = field(default_factory=lambda: [100, 1000, 5000, 20000, 50000])
    
    # LLM Settings
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    default_llm_model: str = field(default_factory=lambda: os.getenv("LLM_MODEL", "gemini-2.5-flash"))
    temperature: float = 0.2

config = Config()
