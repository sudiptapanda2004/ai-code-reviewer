import streamlit as st
from templates import SAMPLE_CODES
from analyzers import run_python_ast, run_regex_security_scanner, run_radon_metrics
from ai_engine import get_ai_client, review_code_with_ai
# Page configuration
st.set_page_config(
    page_title="AI Code Reviewer & Vulnerability Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Metric card styling */
    div[data-testid="stMetric"] {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        padding: 14px 18px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    /* Section headers */
    h3 {
        padding-top: 10px;
    }
    /* Code text area font */
    textarea {
        font-family: 'Consolas', 'Courier New', monospace !important;
        font-size: 13.5px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ AI Code Reviewer & Vulnerability Scanner")
st.caption("Hybrid deterministic code inspection & Radon software metrics with Gemini semantic reasoning.")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Project Controls")
    
    # 1. Language selector
    language = st.selectbox(
        "Programming Language:",
        ["Python", "Java", "JavaScript", "C", "C++", "Go"]
    )
    
    st.markdown("---")
    st.subheader("🔍 Static Rule Toggles")
    check_unsafe = st.checkbox("Catch Unsafe Calls (eval, exec, system, gets)", value=True)
    check_secrets = st.checkbox("Scan Hardcoded Secrets/Keys", value=True)
    
    st.markdown("---")
    st.subheader("🤖 AI Review Options")
    enable_ai = st.toggle("Enable Semantic AI Review", value=True, help="Toggle Gemini LLM semantic feedback on or off.")

# --- MAIN INPUT INTERFACE ---
code_input = st.text_area(
    f"Input {language} Source Code:",
    value=SAMPLE_CODES[language],
    height=250
)

if st.button("🚀 Analyze & Audit Code", type="primary"):
    if not code_input.strip():
        st.warning(f"Please provide valid {language} code to inspect.")
        st.stop()

    # Determine UI columns based on whether AI is enabled
    if enable_ai:
        col_static, col_ai = st.columns([1, 1.2])
    else:
        col_static = st.container()

    # --- MODULE 1: STATIC ANALYSIS ENGINE ---
    with col_static:
        st.subheader(f"1. Static Diagnostics ({language})")

        if language == "Python":
            # Run deep Python AST + Regex scanner
            static_findings = run_python_ast(code_input, check_unsafe) + run_regex_security_scanner(code_input, check_unsafe, check_secrets)
            total_cc, mi_score = run_radon_metrics(code_input)
            
            # Deduplicate findings on the same line
            unique_findings = list({f"{f['line']}_{f['desc']}": f for f in static_findings}.values())

            # Metrics
            m_col1, m_col2 = st.columns(2)
            m_col1.metric("Maintainability Index", f"{mi_score:.1f} / 100", delta="Healthy" if mi_score > 65 else "Refactor Needed")
            m_col2.metric("Cyclomatic Complexity", total_cc, delta="High Complexity" if total_cc > 10 else "Optimal", delta_color="inverse")
            static_findings = unique_findings
        else:
            # Multi-language regex engine
            static_findings = run_regex_security_scanner(code_input, check_unsafe, check_secrets)
            st.info(f"ℹ️ Pattern-based heuristic scanner active for {language}.")

        # Display Diagnostic Alerts
        if static_findings:
            for item in static_findings:
                if item["level"] in ["HIGH", "CRITICAL"]:
                    st.error(f"**Line {item['line']} [{item['level']}]**: {item['desc']}")
                else:
                    st.warning(f"**Line {item['line']} [{item['level']}]**: {item['desc']}")
        else:
            st.success(f"✅ Clean scan: No syntax issues, unsafe functions, or secrets detected.")

    # --- MODULE 2: SEMANTIC AI ENGINE (GEMINI) ---
    # --- MODULE 2: SEMANTIC AI ENGINE (GEMINI) ---
    if enable_ai:
        with col_ai:
            st.subheader(f"2. Semantic AI Review (Gemini - {language})")
            
            client = get_ai_client()
            if not client:
                st.error("⚠️ `GEMINI_API_KEY` not detected. Verify that your `.env` file contains `GEMINI_API_KEY=your_key`.")
            else:
                with st.spinner(f"Evaluating {language} code logic, edge cases, and generating refactor..."):
                    try:
                        ai_feedback = review_code_with_ai(client, code_input, language)
                        st.markdown(ai_feedback)
                    except Exception as err:
                        st.error(f"Semantic Engine Error: {err}")