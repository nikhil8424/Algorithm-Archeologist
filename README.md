# ⚡ Algorithm Archaeologist

**Algorithm Archaeologist** is an autonomous multi-agent framework for excavating, synthesizing, adversarial-fuzzing, empirical-benchmarking, and Pareto-optimizing algorithmic candidates.

---

## 🏛️ Directory & Architecture Structure

```
algorithm-archaeologist/
│
├── app/
│   ├── main.py                     # Master pipeline orchestrator & CLI entrypoint
│   ├── config.py                   # Global configuration & environment settings
│   │
│   ├── agents/                     # Multi-Agent Discovery Team
│   │   ├── planner.py              # Paradigm decomposition & complexity analysis
│   │   ├── coder.py                # Candidate AST synthesis & code generation
│   │   ├── tester.py               # Adversarial fuzzing execution orchestrator
│   │   ├── critic.py               # Root-cause failure diagnosis & genetic repair
│   │   ├── selector.py             # Multi-objective Pareto champion selector
│   │   └── reporter.py             # Explainable research synthesis generation
│   │
│   ├── tools/                      # Deterministic Tools & Isolated Runtimes
│   │   ├── problem_analyzer.py     # Spec ingestion & problem family classifier
│   │   ├── executor.py             # Subprocess isolated execution & resource profiler
│   │   ├── sandbox.py              # Static AST security gatekeeper
│   │   ├── test_generator.py       # 7-Category adversarial test suite generator
│   │   ├── oracle.py               # Deterministic mathematical ground-truth solvers
│   │   ├── benchmark.py            # Multi-scale stress benchmarker (N=10 to 50k+)
│   │   ├── profiler.py             # Memory & cyclomatic complexity profiler
│   │   └── complexity.py           # Empirical curve fitting & asymptotic regression
│   │
│   ├── models/                     # Strongly Typed Pydantic Schemas
│   │   ├── problem.py              # ProblemSpec & ProblemFamily enums
│   │   ├── candidate.py            # AlgorithmCandidate & Complexity metadata
│   │   ├── testcase.py             # TestCase, TestCategory, TestResult
│   │   ├── results.py              # BenchmarkResult, ParetoPoint, CriticVerdict
│   │   └── experiment.py           # Experiment, PipelineStage, TimelineEvent, FinalReport
│   │
│   ├── storage/                    # Persistence Layer
│   │   ├── database.py             # SQLite connection & schema initialization
│   │   └── repositories.py         # ExperimentRepository CRUD operations
│   │
│   ├── llm/                        # LLM & Heuristic Abstraction Layer
│   │   ├── provider.py             # Gemini / API client provider interface
│   │   ├── prompts.py              # System prompts & few-shot instructions
│   │   └── structured_output.py    # Schema validation & code cleaners
│   │
│   └── evaluation/                 # Metrics & Optimization Engine
│       ├── evaluator.py            # Unified candidate evaluator
│       ├── ranking.py              # True Non-Dominated Pareto sorting algorithm
│       └── metrics.py              # Speedup ratios & composite fitness scoring
│
├── frontend/
│   └── streamlit_app.py            # Full-featured Streamlit Discovery Dashboard
│
├── tests/                          # Automated Pytest / Unittest test suite
│
├── experiments/                    # Serialized experiment JSON artifacts
├── reports/                        # Exported Markdown synthesis reports
├── sandbox/                        # Temporary isolated runtime workspace
│
├── requirements.txt                # Python package dependencies
├── .env.example                    # Environment variable template
├── Dockerfile                      # Production container build
├── docker-compose.yml              # Multi-container orchestration
├── README.md                       # Project documentation
└── .gitignore                      # Git exclusion rules
```

---

## 🚀 Quickstart Guide

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Run the Autonomous Pipeline CLI
```bash
# Create and run an excavation expedition
python3 app/main.py create --problem shortest-path-100k --candidates 4 --auto-run

# Run isolated sandbox code execution
python3 app/main.py sandbox-run --code "def solve(arr): return max(arr)" --input '{"arr": [1, 2, 3]}'
```

### 3. Launch Streamlit Web UI
```bash
streamlit run frontend/streamlit_app.py --server.port 3000
```

### 4. Run Automated Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py" -v
```
