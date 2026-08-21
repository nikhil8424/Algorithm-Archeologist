# ⚡ Algorithm Archaeologist

> An autonomous multi-agent framework for discovering, testing, benchmarking, repairing, and selecting algorithmic solutions.

Algorithm Archaeologist treats algorithm design as an experimental discovery process rather than one-shot code generation. It explores multiple candidate approaches, generates implementations, validates them against trusted reference oracles, subjects them to adversarial tests, benchmarks performance, analyzes complexity, and identifies strong candidates using Pareto optimization.

## ✨ Core Features

- **Problem Analysis** — Converts a computational problem into a structured specification.
- **Multi-Agent Discovery** — Planner, Coder, Tester, Critic, Selector, and Reporter agents.
- **Candidate Synthesis** — Generates multiple algorithmic implementations.
- **Adversarial Testing** — Exercises edge cases, pathological inputs, duplicates, ordering extremes, and stress cases.
- **Trusted Oracles** — Compares candidate outputs against deterministic reference solutions.
- **Secure Execution** — AST inspection and isolated subprocess execution for generated code.
- **Benchmarking** — Measures runtime and resource behavior across increasing input sizes.
- **Complexity Analysis** — Compares theoretical expectations with empirical scaling.
- **Pareto Optimization** — Finds non-dominated candidates across performance, memory, and other objectives.
- **Explainable Reports** — Produces experiment artifacts and research-style summaries.
- **Streamlit Dashboard** — Provides an interactive view of experiments and results.
- **Docker Support** — Includes containerization and Docker Compose configuration.

## 🧠 Architecture

```text
Problem
   │
   ▼
Problem Analyzer
   │
   ▼
Algorithm Planner
   │
   ├── Candidate A
   ├── Candidate B
   └── Candidate C
          │
          ▼
   Code Generation
          │
          ▼
   AST / Sandbox Gate
          │
          ▼
   Adversarial Testing
          │
          ▼
   Trusted Oracle
      ┌───┴───┐
    FAIL     PASS
      │        │
      ▼        ▼
   Critic   Benchmark
      │        │
      └───┬────┘
          ▼
   Complexity Analysis
          │
          ▼
   Pareto Selection
          │
          ▼
   Explainable Report
```

## 📁 Project Structure

```text
algorithm-archaeologist/
├── app/
│   ├── agents/          # Discovery and reasoning agents
│   ├── tools/           # Execution, testing, oracle, profiling
│   ├── models/          # Typed experiment and result schemas
│   ├── storage/         # SQLite persistence
│   ├── llm/             # LLM/provider abstraction
│   └── evaluation/      # Metrics and Pareto ranking
├── frontend/
│   └── streamlit_app.py
├── experiments/         # Experiment artifacts
├── reports/             # Generated reports
├── sandbox/             # Temporary execution workspace
├── tests/               # Automated tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## 🚀 Quick Start

### 1. Clone

```bash
git clone https://github.com/nikhil8424/Algorithm-Archeologist.git
cd Algorithm-Archeologist
```

### 2. Install

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 3. Configure

Copy `.env.example` to `.env` and configure the required provider/API settings.

### 4. Run an Experiment

```bash
python app/main.py create --problem shortest-path-100k --candidates 4 --auto-run
```

### 5. Run Sandbox Execution

```bash
python app/main.py sandbox-run --code "def solve(arr): return max(arr)" --input '{"arr": [1, 2, 3]}'
```

### 6. Launch Dashboard

```bash
streamlit run frontend/streamlit_app.py --server.port 3000
```

### 7. Run Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

## 🔬 Experiment Lifecycle

```text
Analyze → Discover → Generate → Validate → Attack → Repair → Benchmark → Rank → Explain
```

The system separates **correctness** from **performance**: an implementation must first survive validation before its performance is meaningfully compared.

## 📊 Evaluation Dimensions

Candidates can be compared using:

| Dimension | Purpose |
|---|---|
| Correctness | Does the implementation produce the expected result? |
| Robustness | Does it survive adversarial inputs? |
| Runtime | How quickly does it execute? |
| Memory | How much memory does it require? |
| Complexity | How does performance scale with input size? |
| Pareto Efficiency | Is another candidate better across all objectives? |

## 🐳 Docker

```bash
docker build -t algorithm-archaeologist .
docker compose up --build
```

## 🔐 Security Note

Generated code is treated as untrusted. The project includes AST inspection and isolated execution, but these mechanisms should not be considered a complete security boundary for hostile workloads. Production deployments should add hardened container/OS isolation, resource limits, restricted networking, and defense-in-depth controls.

## 🔭 Research Direction

Algorithm Archaeologist can support research into:

- AI-assisted algorithm discovery
- automated program synthesis
- adversarial evaluation of generated code
- self-repairing algorithms
- empirical complexity estimation
- multi-agent software engineering
- Pareto-based algorithm selection
- evolutionary and autonomous algorithm search

## 🗺️ Roadmap

- [ ] Expand supported problem families
- [ ] Add richer algorithm mutation/evolution
- [ ] Improve benchmark visualization
- [ ] Add experiment replay and comparison
- [ ] Support additional LLM providers
- [ ] Add distributed benchmarking
- [ ] Strengthen execution isolation
- [ ] Add research-grade evaluation datasets

## 👨‍💻 Author

**Nikhil Gupta**  
Computer Science | AI & ML | Agentic AI | Algorithms

GitHub: https://github.com/nikhil8424

## 📄 License

Add the project's selected open-source license before publishing for reuse.

---

> **Dig deeper. Test harder. Benchmark everything. Discover better algorithms.**
