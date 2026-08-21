import streamlit as st
import pandas as pd
import json
import time
import os
import sys

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.main import orchestrator
from app.storage.repositories import experiment_repo
from app.tools.problem_analyzer import problem_analyzer
from app.tools.executor import code_executor
from app.models.experiment import PipelineStage

st.set_page_config(
    page_title="Algorithm Archaeologist",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS styling for dark sleek dashboard
st.markdown("""
<style>
    .main {
        background-color: #09090b;
        color: #f4f4f5;
    }
    .metric-card {
        background: #18181b;
        border: 1px solid #27272a;
        padding: 1rem;
        border-radius: 0.75rem;
        margin-bottom: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.5rem;
        font-weight: 600;
    }
    .highlight-badge {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        padding: 0.2rem 0.6rem;
        border-radius: 0.375rem;
        border: 1px solid rgba(245, 158, 11, 0.3);
        font-size: 0.8rem;
    }
</style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR -----------------
with st.sidebar:
    st.title("⚡ Algorithm Archaeologist")
    st.caption("Autonomous Algorithmic Discovery & Verification")

    st.divider()
    st.subheader("Archaeological Inquiries")

    # List existing experiments
    saved_exps = experiment_repo.list_all()
    exp_options = {e["id"]: f"{e['problem_title'][:30]}... ({e['current_state']})" for e in saved_exps}

    selected_exp_id = None
    if exp_options:
        selected_exp_id = st.selectbox(
            "Select Existing Run:",
            options=list(exp_options.keys()),
            format_func=lambda x: exp_options[x],
        )

    st.divider()
    st.subheader("Start New Expedition")
    presets = problem_analyzer.list_preset_problems()
    preset_dict = {p.id: p.title for p in presets}
    
    preset_choice = st.selectbox("Preset Problem Catalog:", options=list(preset_dict.keys()), format_func=lambda x: preset_dict[x])
    candidate_count = st.slider("Initial Paradigm Breadth:", min_value=2, max_value=6, value=4)
    auto_run = st.checkbox("Autonomous Fast-Forward (Auto-Run)", value=True)

    if st.button("🚀 Launch Excavation", use_container_width=True, type="primary"):
        with st.spinner("Excavating algorithmic solution space..."):
            new_exp = orchestrator.create_experiment(preset_choice, candidate_count)
            if auto_run:
                new_exp = orchestrator.run_all(new_exp.id)
            st.success(f"Created expedition {new_exp.id}")
            st.rerun()

# ----------------- MAIN VIEW -----------------
if not selected_exp_id and not saved_exps:
    # Auto bootstrap first experiment
    with st.spinner("Initializing first expedition..."):
        first_exp = orchestrator.create_experiment("shortest-path-100k", 4)
        first_exp = orchestrator.run_all(first_exp.id)
        selected_exp_id = first_exp.id

current_exp = experiment_repo.get_by_id(selected_exp_id) if selected_exp_id else None

if current_exp:
    # Header Information
    st.markdown(f"### 🏺 {current_exp.problem_spec.title}")
    col_hdr1, col_hdr2, col_hdr3, col_hdr4 = st.columns(4)
    with col_hdr1:
        st.markdown(f"**Family:** `{current_exp.problem_spec.problem_family.value}`")
    with col_hdr2:
        st.markdown(f"**Lower Bound Time:** `{current_exp.problem_spec.theoretical_lower_bound_time}`")
    with col_hdr3:
        st.markdown(f"**Pipeline Stage:** `{current_exp.current_state.value}`")
    with col_hdr4:
        if current_exp.current_state != PipelineStage.DONE:
            if st.button("▶ Step State", key="step_btn"):
                orchestrator.step(current_exp.id)
                st.rerun()
            if st.button("⚡ Run to Completion", key="run_all_btn"):
                orchestrator.run_all(current_exp.id)
                st.rerun()

    # Tabs for Modules
    tab_cand, tab_tests, tab_bench, tab_pareto, tab_evolve, tab_report, tab_sandbox = st.tabs([
        "🧬 Candidates & AST",
        "🎯 Adversarial Tests",
        "📊 Benchmarks",
        "⚖️ Pareto Frontier",
        "🌱 Evolution",
        "📄 Explainable Report",
        "🧪 Live Sandbox",
    ])

    # 1. CANDIDATES TAB
    with tab_cand:
        st.subheader("Synthesized Algorithmic Candidates")
        for c in current_exp.candidates:
            with st.expander(f"{'⭐ ' if c.is_winner else ''}{c.name} ({c.paradigm}) - Pareto Rank {c.pareto_rank}", expanded=c.is_winner):
                st.write(f"**Strategy:** {c.strategy_description}")
                col_c1, col_c2, col_c3, col_c4 = st.columns(4)
                col_c1.metric("Theoretical Time", c.complexity.time_theoretical)
                col_c2.metric("Theoretical Space", c.complexity.space_theoretical)
                col_c3.metric("Fuzz Accuracy", f"{c.accuracy_percentage:.1f}%")
                col_c4.metric("Avg Runtime", f"{c.avg_runtime_ms:.2f} ms")
                st.code(c.code, language="python")

    # 2. TESTS TAB
    with tab_tests:
        st.subheader("7-Category Adversarial Fuzzing Suite")
        test_rows = []
        for t in current_exp.test_cases:
            res_for_test = [r for r in current_exp.test_results if r.test_id == t.id]
            passed_cands = sum(1 for r in res_for_test if r.passed)
            total_cands = len(res_for_test)
            test_rows.append({
                "Test ID": t.id,
                "Name": t.name,
                "Category": t.category.value,
                "Input Size": t.input_size,
                "Pass Rate": f"{passed_cands}/{total_cands}",
                "Description": t.description,
            })
        if test_rows:
            st.dataframe(pd.DataFrame(test_rows), use_container_width=True)

    # 3. BENCHMARKS TAB
    with tab_bench:
        st.subheader("Empirical Multi-Scale Stress Benchmarking")
        if current_exp.benchmark_results:
            bench_df = pd.DataFrame([b.model_dump() for b in current_exp.benchmark_results])
            cand_map = {c.id: c.name for c in current_exp.candidates}
            bench_df["Candidate"] = bench_df["candidate_id"].map(cand_map)

            pivot_runtime = bench_df.pivot(index="input_size", columns="Candidate", values="runtime_ms")
            st.line_chart(pivot_runtime)
            st.caption("Empirical Runtime (ms) vs. Input Scaling Size N")

    # 4. PARETO TAB
    with tab_pareto:
        st.subheader("Multi-Objective Non-Dominated Pareto Frontier")
        pareto_rows = []
        for c in current_exp.candidates:
            pareto_rows.append({
                "Candidate": c.name,
                "Paradigm": c.paradigm,
                "Runtime (ms)": c.avg_runtime_ms,
                "Memory (MB)": c.peak_memory_mb,
                "Accuracy (%)": c.accuracy_percentage,
                "AST Nodes": c.ast_node_count,
                "Pareto Rank": c.pareto_rank,
                "Optimal Frontier": "✅ Non-Dominated" if c.is_pareto_optimal else "Dominated",
                "Winner": "🏆 Champion" if c.is_winner else "",
            })
        st.dataframe(pd.DataFrame(pareto_rows), use_container_width=True)

    # 5. EVOLUTION TAB
    with tab_evolve:
        st.subheader("Genetic AST Mutations & Lineage")
        if current_exp.evolution_history:
            for step in current_exp.evolution_history:
                st.info(f"**Generation {step.generation}**: Evolved `{step.child_id}` from `{step.parent_id}` via `{step.mutation_type}`: {step.description}")
        else:
            st.write("No genetic repairs required for this problem configuration.")

    # 6. REPORT TAB
    with tab_report:
        st.subheader("Explainable Synthesis Research Report")
        if current_exp.final_report:
            st.markdown(current_exp.final_report.markdown_content)
            st.download_button(
                "📥 Download Synthesis Markdown",
                data=current_exp.final_report.markdown_content,
                file_name=f"{current_exp.id}_report.md",
                mime="text/markdown",
            )
        else:
            st.warning("Pipeline is not yet in 'DONE' stage. Step forward to generate final report.")

    # 7. LIVE SANDBOX TAB
    with tab_sandbox:
        st.subheader("AST-Secured Interactive Sandbox Playground")
        sb_code = st.text_area("Algorithm Python Code:", height=200, value="""def solve(arr):
    # Kadane's algorithm
    max_so_far = arr[0]
    curr = arr[0]
    for x in arr[1:]:
        curr = max(x, curr + x)
        max_so_far = max(max_so_far, curr)
    return max_so_far""")
        sb_input = st.text_area("Input JSON Payload:", height=70, value='{"arr": [-2, 1, -3, 4, -1, 2, 1, -5, 4]}')

        if st.button("▶ Run Sandbox Execution"):
            try:
                payload = json.loads(sb_input)
            except Exception as e:
                payload = sb_input
            res = code_executor.execute(sb_code, payload)
            if res.get("passed"):
                st.success(f"Status: {res.get('status')} | Runtime: {res.get('runtime_ms'):.3f} ms | Memory: {res.get('memory_mb'):.2f} MB")
                st.json({"output": res.get("actual_output")})
            else:
                st.error(f"Status: {res.get('status')} | Error: {res.get('error_message')}")
