import streamlit as st
import ast
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from google import genai

# Page configuration
st.set_page_config(
    page_title="AI Code Reviewer & Vulnerability Scanner",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ AI Code Reviewer & Vulnerability Scanner")
st.caption("Hybrid deterministic AST inspection & Radon software metrics with Gemini semantic reasoning.")

# --- SIDEBAR CONFIGURATION ---
with st.sidebar:
    st.header("⚙️ Configuration")
    api_key = st.text_input("Gemini API Key:", type="password", help="Enter your free API key from Google AI Studio")
    st.markdown("---")
    st.markdown("### 🔍 Static Rule Toggles")
    check_eval = st.checkbox("Catch Unsafe Eval/Exec", value=True)
    check_hardcoded = st.checkbox("Scan Hardcoded Secrets/Keys", value=True)
    st.info("💡 Tip: Get a free API key at aistudio.google.com")

# --- STATIC ANALYSIS FUNCTIONS ---
def run_ast_analysis(code_str: str):
    """Parses Abstract Syntax Tree to identify deterministic security risks."""
    findings = []
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            # 1. Unsafe evaluation detection
            if check_eval and isinstance(node, ast.Call):
                func_name = getattr(node.func, 'id', None)
                if func_name in ['eval', 'exec', '__import__']:
                    findings.append({
                        "line": node.lineno,
                        "level": "HIGH",
                        "desc": f"Direct execution of unsafe call `{func_name}()` exposes code to remote code execution (RCE)."
                    })
            
            # 2. Hardcoded potential secrets/tokens
            if check_hardcoded and isinstance(node, ast.Assign):
                for target in node.targets:
                    target_name = getattr(target, 'id', '').lower()
                    if any(secret_word in target_name for secret_word in ['key', 'token', 'secret', 'password']):
                        if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                            findings.append({
                                "line": node.lineno,
                                "level": "MEDIUM",
                                "desc": f"Hardcoded credential pattern detected in variable `{getattr(target, 'id', '')}`."
                            })

    except SyntaxError as e:
        findings.append({
            "line": e.lineno,
            "level": "CRITICAL",
            "desc": f"Syntax Error: {e.msg}"
        })
    return findings

def run_radon_metrics(code_str: str):
    """Computes Cyclomatic Complexity and Maintainability Index."""
    try:
        blocks = cc_visit(code_str)
        total_cc = sum(b.complexity for b in blocks)
        mi_score = mi_visit(code_str, multi=False)
        return total_cc, mi_score
    except Exception:
        return 0, 100.0

# --- USER INTERFACE INPUT ---
sample_code = '''def process_user_records(user_input):
    api_secret_token = "sk_live_98327498273"
    
    # Insecure execution
    computed_result = eval(user_input)
    
    total = 0
    for i in range(10):
        for j in range(10):
            if i == j:
                total += i * j
                
    return total, computed_result
'''

code_input = st.text_area("Source Code to Inspect (Python):", value=sample_code, height=220)

if st.button("🚀 Analyze & Review Code", type="primary"):
    if not code_input.strip():
        st.warning("Please paste valid Python source code.")
        st.stop()

    # Split into 2 columns for a clean side-by-side display
    col_static, col_ai = st.columns([1, 1.2])

    # Left Column: Deterministic Static Engine
    with col_static:
        st.subheader("1. Static Analysis (AST & Radon)")
        
        static_findings = run_ast_analysis(code_input)
        total_cc, mi_score = run_radon_metrics(code_input)

        # Metric Cards
        col_m1, col_m2 = st.columns(2)
        col_m1.metric("Maintainability Index", f"{mi_score:.1f} / 100", delta="Healthy" if mi_score > 65 else "Refactor Needed")
        col_m2.metric("Cyclomatic Complexity", total_cc, delta="High Complexity" if total_cc > 10 else "Optimal", delta_color="inverse")

        # Static findings cards
        if static_findings:
            for item in static_findings:
                if item["level"] in ["HIGH", "CRITICAL"]:
                    st.error(f"**Line {item['line']} [{item['level']}]**: {item['desc']}")
                else:
                    st.warning(f"**Line {item['line']} [{item['level']}]**: {item['desc']}")
        else:
            st.success("✅ Clean AST scan: No hardcoded secrets or unsafe evaluations detected.")

    # Right Column: AI Semantic Review
    with col_ai:
        st.subheader("2. Semantic AI Review (Gemini)")
        
        if not api_key:
            st.info("ℹ️ Enter your Gemini API key in the left sidebar to enable AI analysis and code refactoring.")
        else:
            with st.spinner("Analyzing code logic, edge cases, and generating refactor..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    You are a senior code reviewer and security auditor.
                    Review the following Python code:
                    
                    ```python
                    {code_input}
                    ```
                    
                    Provide concise feedback formatted under these exact Markdown headers:
                    ### 🐞 Bugs & Vulnerabilities
                    ### ⚡ Performance & Clean Code
                    ### 🛠️ Refactored Code
                    (Include the clean, secure Python code in a standard code block)
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt
                    )
                    st.markdown(response.text)
                except Exception as ex:
                    st.error(f"API Error: {ex}")