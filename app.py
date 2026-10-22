import streamlit as st
import ast
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from templates import SAMPLE_CODES
from ai_engine import get_ai_client, review_code_with_ai

# Page Configuration
st.set_page_config(
    page_title="SecureCode AI - Automated Reviewer & Vulnerability Scanner",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# High-Contrast, Legible Cyber-Dark Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Inter:wght@400;500;600;700;800&display=swap');

    /* Hide Streamlit default white top header bar */
    header[data-testid="stHeader"] {
        background-color: #070b13 !important;
    }

    /* Global Body Font and Background */
    .stApp {
        background-color: #070b13 !important;
        font-family: 'Inter', sans-serif !important;
        color: #f1f5f9 !important;
        font-size: 15px !important;
    }

    /* Sidebar Background and High-Contrast Typography */
    section[data-testid="stSidebar"] {
        background-color: #0a0f1d !important;
        border-right: 1px solid #1e293b !important;
    }
    
    /* Force high contrast and readable size on all sidebar labels */
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] span {
        color: #f8fafc !important;
        font-size: 15px !important;
        font-weight: 600 !important;
    }

    /* Category section headers in sidebar */
    .sidebar-section-title {
        font-size: 13px !important;
        font-weight: 800 !important;
        color: #38bdf8 !important;
        letter-spacing: 0.8px !important;
        text-transform: uppercase !important;
        margin-top: 18px !important;
        margin-bottom: 6px !important;
        display: block !important;
    }

    .sidebar-nav-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 11px 16px;
        border-radius: 8px;
        font-size: 15px !important;
        font-weight: 600;
        color: #cbd5e1 !important;
        margin-bottom: 6px;
    }
    .sidebar-nav-item.active {
        background: rgba(14, 165, 233, 0.2);
        color: #38bdf8 !important;
        border-left: 4px solid #38bdf8;
    }

    /* Top Navigation Bar */
    .top-navbar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #0d1527;
        border: 1px solid #1e2d48;
        border-radius: 12px;
        padding: 16px 26px;
        margin-bottom: 24px;
    }
    .brand-section {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .brand-name {
        font-size: 1.45rem;
        font-weight: 800;
        color: #38bdf8;
        letter-spacing: -0.5px;
    }
    .brand-sub {
        font-size: 1.05rem;
        color: #94a3b8;
        border-left: 2px solid #243552;
        padding-left: 14px;
        font-weight: 500;
    }
    .user-badge {
        display: flex;
        align-items: center;
        gap: 12px;
        background: #141f36;
        border: 1px solid #243658;
        padding: 8px 18px;
        border-radius: 24px;
        font-size: 1rem;
        font-weight: 600;
        color: #f8fafc;
    }
    .avatar-circle {
        background: linear-gradient(135deg, #0284c7, #38bdf8);
        color: #ffffff;
        font-weight: 800;
        font-size: 0.85rem;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    /* Glass Cards */
    .glass-card {
        background: #0d1527;
        border: 1px solid #1a2942;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 18px;
        box-shadow: 0 4px 24px rgba(0, 0, 0, 0.35);
    }
    .glass-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #1a2942;
        padding-bottom: 14px;
        margin-bottom: 16px;
    }
    .glass-header-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #ffffff;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Posture Radial Ring */
    .posture-score-box {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 10px;
    }
    .score-circle {
        position: relative;
        width: 130px;
        height: 130px;
        border-radius: 50%;
        background: conic-gradient(#10b981 var(--score-deg), #1e293b 0);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.25);
    }
    .score-circle-inner {
        position: absolute;
        width: 102px;
        height: 102px;
        background: #0d1527;
        border-radius: 50%;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }
    .score-number {
        font-size: 1.85rem;
        font-weight: 800;
        color: #ffffff;
    }
    .score-label {
        font-size: 0.8rem;
        color: #10b981;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
    }

    /* Metric Chips */
    .metric-chip {
        background: #111c33;
        border: 1px solid #1f3050;
        border-radius: 10px;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
    }
    .metric-chip-title {
        font-size: 0.85rem;
        color: #cbd5e1;
        font-weight: 500;
    }
    .metric-chip-val {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Diagnostics Table */
    .diag-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.95rem;
        margin-top: 6px;
    }
    .diag-table th {
        text-align: left;
        padding: 12px;
        color: #94a3b8;
        font-weight: 700;
        border-bottom: 1px solid #1a2942;
        font-size: 0.95rem;
    }
    .diag-table td {
        padding: 12px;
        border-bottom: 1px solid #162238;
        font-size: 0.95rem;
        line-height: 1.5;
    }
    .badge-critical {
        background: rgba(239, 68, 68, 0.22);
        color: #fca5a5;
        border: 1px solid #ef4444;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-high {
        background: rgba(249, 115, 22, 0.22);
        color: #fdba74;
        border: 1px solid #f97316;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
    }
    .badge-medium {
        background: rgba(234, 179, 8, 0.22);
        color: #fde047;
        border: 1px solid #eab308;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.85rem;
        font-weight: 700;
    }

    /* Severity Bars */
    .sev-bar-container {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        font-size: 0.95rem;
    }
    .sev-bar-label {
        width: 75px;
        font-weight: 600;
    }
    .sev-bar-track {
        flex: 1;
        height: 8px;
        background: #1e293b;
        border-radius: 4px;
        overflow: hidden;
    }
    .sev-bar-fill {
        height: 100%;
        border-radius: 4px;
    }

    /* Code Textarea */
    textarea {
        background-color: #060b14 !important;
        border: 1px solid #1e2d48 !important;
        color: #38bdf8 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 14.5px !important;
        line-height: 1.6 !important;
        border-radius: 10px !important;
    }

    /* Markdown output styling for AI Review */
    .stMarkdown p, .stMarkdown li {
        font-size: 15.5px !important;
        line-height: 1.65 !important;
        color: #e2e8f0 !important;
    }
    .stMarkdown h3 {
        font-size: 1.25rem !important;
        font-weight: 700 !important;
        color: #38bdf8 !important;
        margin-top: 18px !important;
    }
</style>
""", unsafe_allow_html=True)

# Top Bar
st.markdown("""
<div class="top-navbar">
    <div class="brand-section">
        <span style="font-size: 1.7rem;">🛡️</span>
        <span class="brand-name">SecureCode <span style="color:#0ea5e9;">AI</span></span>
        <span class="brand-sub">AI Code Reviewer & Vulnerability Scanner</span>
    </div>
    <div class="user-badge">
        <div class="avatar-circle">SP</div>
        <span>Sudipta Panda</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Sidebar with high-contrast categories
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 16px 0;">
        <div class="sidebar-nav-item active">⚡ Code Scanner</div>
        <div class="sidebar-nav-item">🕒 Scan History</div>
        <div class="sidebar-nav-item">📑 Reports</div>
        <div class="sidebar-nav-item">⚙️ Settings</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<span class="sidebar-section-title">PROJECT CONTROLS</span>', unsafe_allow_html=True)
    language = st.selectbox(
        "Programming Language",
        ["Python", "Java", "JavaScript", "C", "C++", "Go"],
        index=0
    )
    
    st.markdown('<span class="sidebar-section-title">STATIC RULE TOGGLES</span>', unsafe_allow_html=True)
    check_unsafe = st.checkbox("Catch Unsafe Calls (eval, exec, system, gets)", value=True)
    check_secrets = st.checkbox("Scan Hardcoded Secrets/Keys", value=True)
    
    st.markdown('<span class="sidebar-section-title">AI SEMANTIC ENGINE</span>', unsafe_allow_html=True)
    enable_ai = st.toggle("Enable Semantic AI Review", value=True)

    st.markdown("""
    <div style="margin-top: 36px; padding: 16px; background: #0d1527; border: 1px solid #1e293b; border-radius: 10px;">
        <span style="font-size: 1.1rem;">🔒</span>
        <span style="font-size: 0.95rem; font-weight:700; color:#f8fafc;"> Smarter code. Safer apps.</span>
        <p style="font-size: 0.85rem; color: #94a3b8; margin-top: 6px; margin-bottom: 0; line-height: 1.4;">Automated AST parsing combined with Gemini code intelligence.</p>
    </div>
    """, unsafe_allow_html=True)

# Deterministic Analyzers
def run_python_ast(code_str: str, check_unsafe: bool):
    findings = []
    try:
        tree = ast.parse(code_str)
        for node in ast.walk(tree):
            if check_unsafe and isinstance(node, ast.Call):
                func_name = getattr(node.func, 'id', None)
                if func_name in ['eval', 'exec', '__import__']:
                    findings.append({
                        "line": node.lineno,
                        "level": "HIGH",
                        "desc": f"Direct execution of unsafe call `{func_name}()` exposes code to Remote Code Execution (RCE)."
                    })
    except SyntaxError as e:
        findings.append({
            "line": e.lineno,
            "level": "CRITICAL",
            "desc": f"Syntax Error: {e.msg}"
        })
    return findings

def run_regex_security_scanner(code_str: str, check_unsafe: bool, check_hardcoded: bool):
    findings = []
    lines = code_str.split("\n")

    dangerous_patterns = [
        (r'\b(eval|exec)\s*\(', "High-risk dynamic code execution (`eval`/`exec`) detected."),
        (r'\bgets\s*\(', "Dangerous `gets()` call detected. Vulnerable to critical buffer overflow."),
        (r'\bsystem\s*\(', "Dangerous `system()` invocation. Direct command execution risk."),
        (r'Runtime\.getRuntime\(\)\.exec\(', "Unsanitized `Runtime.getRuntime().exec()` invocation. Command injection hazard."),
        (r'exec\.Command\(', "Execution of shell command without rigorous sanitization.")
    ]

    secret_pattern = re.compile(
        r'(api[_-]?key|secret|token|password|auth|jwt)\s*[:=]\s*["\'][A-Za-z0-9_\-\.]{6,}["\']', 
        re.IGNORECASE
    )

    for idx, line in enumerate(lines, start=1):
        if check_unsafe:
            for pattern, msg in dangerous_patterns:
                if re.search(pattern, line):
                    findings.append({"line": idx, "level": "HIGH", "desc": msg})

        if check_hardcoded and secret_pattern.search(line):
            findings.append({
                "line": idx,
                "level": "MEDIUM",
                "desc": "Probable hardcoded credential, secret, or token assigned as a string literal."
            })

    return findings

def run_radon_metrics(code_str: str):
    try:
        blocks = cc_visit(code_str)
        total_cc = sum(b.complexity for b in blocks)
        mi_score = mi_visit(code_str, multi=False)
        return total_cc, mi_score
    except Exception:
        return 0, 100.0

# Top Grid Layout
col_editor, col_posture, col_breakdown = st.columns([1.4, 0.9, 0.9])

with col_editor:
    ext = "py" if language == "Python" else language.lower()
    st.markdown(f"""
    <div class="glass-header" style="margin-bottom: 8px;">
        <div class="glass-header-title">
            <span>💻</span> Code Input <span style="font-size:0.85rem; color:#94a3b8; font-weight:500; margin-left:8px;">process_user_records.{ext}</span>
        </div>
        <div style="font-size: 0.85rem; font-weight:700; background: #1a2a47; color: #38bdf8; padding: 4px 10px; border-radius: 6px;">
            {language}
        </div>
    </div>
    """, unsafe_allow_html=True)

    code_input = st.text_area(
        label="Code Area",
        value=SAMPLE_CODES[language],
        height=280,
        label_visibility="collapsed"
    )

    analyze_clicked = st.button("🚀 Analyze & Audit Code", type="primary", use_container_width=True)

# Run Static Analysis
if language == "Python":
    raw_findings = run_python_ast(code_input, check_unsafe) + run_regex_security_scanner(code_input, check_unsafe, check_secrets)
    total_cc, mi_score = run_radon_metrics(code_input)
    static_findings = list({f"{f['line']}_{f['desc']}": f for f in raw_findings}.values())
else:
    static_findings = run_regex_security_scanner(code_input, check_unsafe, check_secrets)
    total_cc, mi_score = 0, 100.0

crit = sum(1 for f in static_findings if f["level"] == "CRITICAL")
high = sum(1 for f in static_findings if f["level"] == "HIGH")
med = sum(1 for f in static_findings if f["level"] == "MEDIUM")
total_issues = len(static_findings)

# Dynamic Quality Calculation
score = max(10, int(mi_score - (crit * 25) - (high * 15) - (med * 5) - max(0, total_cc - 5) * 2))
score_deg = int((score / 100) * 360)

with col_posture:
    st.markdown(f"""
    <div class="glass-card">
        <div class="glass-header">
            <div class="glass-header-title">🛡️ Security Posture</div>
        </div>
        <div class="posture-score-box">
            <div class="score-circle" style="--score-deg: {score_deg}deg;">
                <div class="score-circle-inner">
                    <div class="score-number">{score}</div>
                    <div class="score-label">{'Good' if score >= 65 else 'At Risk'}</div>
                </div>
            </div>
            <div style="font-size: 0.9rem; color:#cbd5e1; font-weight:600; margin-top: 12px;">Security Quality Score</div>
        </div>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 16px;">
            <div class="metric-chip">
                <div><div class="metric-chip-title">Total Issues</div><div class="metric-chip-val">{total_issues}</div></div>
                <span style="font-size:1.2rem; color:#ef4444;">⚠️</span>
            </div>
            <div class="metric-chip">
                <div><div class="metric-chip-title">Complexity</div><div class="metric-chip-val">{total_cc}</div></div>
                <span style="font-size:1.2rem; color:#38bdf8;">🔀</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col_breakdown:
    max_count = max(total_issues, 1)
    st.markdown(f"""
    <div class="glass-card">
        <div class="glass-header">
            <div class="glass-header-title">📊 Issue Severity Breakdown</div>
        </div>
        <div class="sev-bar-container">
            <div class="sev-bar-label" style="color: #ef4444;">Critical</div>
            <div class="sev-bar-track"><div class="sev-bar-fill" style="width:{(crit/max_count)*100}%; background:#ef4444;"></div></div>
            <div style="width: 24px; text-align:right; font-weight:700; color:#ef4444;">{crit}</div>
        </div>
        <div class="sev-bar-container">
            <div class="sev-bar-label" style="color: #f97316;">High</div>
            <div class="sev-bar-track"><div class="sev-bar-fill" style="width:{(high/max_count)*100}%; background:#f97316;"></div></div>
            <div style="width: 24px; text-align:right; font-weight:700; color:#f97316;">{high}</div>
        </div>
        <div class="sev-bar-container">
            <div class="sev-bar-label" style="color: #eab308;">Medium</div>
            <div class="sev-bar-track"><div class="sev-bar-fill" style="width:{(med/max_count)*100}%; background:#eab308;"></div></div>
            <div style="width: 24px; text-align:right; font-weight:700; color:#eab308;">{med}</div>
        </div>
        <div class="sev-bar-container">
            <div class="sev-bar-label" style="color: #94a3b8;">Low</div>
            <div class="sev-bar-track"><div class="sev-bar-fill" style="width:0%; background:#64748b;"></div></div>
            <div style="width: 24px; text-align:right; font-weight:700; color:#94a3b8;">0</div>
        </div>
        <div style="margin-top: 18px; padding-top: 12px; border-top: 1px solid #1a2942;">
            <div class="metric-chip" style="margin-bottom:0;">
                <div><div class="metric-chip-title">Maintainability Index</div><div class="metric-chip-val">{mi_score:.1f} / 100</div></div>
                <span style="font-size:1.2rem; color:#10b981;">📈</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Lower Deck: Static Diagnostics & AI Semantic Review
col_diag, col_ai = st.columns([1, 1.2])

with col_diag:
    st.markdown('<div class="glass-header"><div class="glass-header-title">🔍 Static Analysis Diagnostics</div></div>', unsafe_allow_html=True)

    if static_findings:
        rows_html = ""
        for item in static_findings:
            lvl = item["level"].lower()
            badge_class = f"badge-{lvl}" if lvl in ["critical", "high", "medium"] else "badge-medium"
            rows_html += f"""<tr>
<td style="color: #94a3b8; font-weight: 700;">Line {item['line']}</td>
<td><span class="{badge_class}">{item['level']}</span></td>
<td style="color: #f1f5f9;">{item['desc']}</td>
</tr>"""

        table_html = f"""<table class="diag-table">
<thead>
<tr>
<th style="width: 20%;">Location</th>
<th style="width: 22%;">Severity</th>
<th style="width: 58%;">Rule Finding</th>
</tr>
</thead>
<tbody>
{rows_html}
</tbody>
</table>"""
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.markdown("""
<div style="padding: 24px; text-align: center; color: #10b981; background: #0d1e2e; border: 1px solid #14384d; border-radius: 8px; font-weight: 600;">
    ✅ No static vulnerabilities or code-smell patterns flagged.
</div>
""", unsafe_allow_html=True)

with col_ai:
    st.markdown('<div class="glass-header"><div class="glass-header-title">✨ Semantic AI Review (Gemini Intelligence)</div></div>', unsafe_allow_html=True)
    
    if not enable_ai:
        st.info("ℹ️ Semantic AI Review is disabled in the sidebar.")
    elif analyze_clicked or "ai_result" in st.session_state:
        client = get_ai_client()
        if not client:
            st.error("⚠️ `GEMINI_API_KEY` missing in `.env`.")
        else:
            if analyze_clicked:
                with st.spinner("🤖 Performing AST & LLM reasoning..."):
                    try:
                        st.session_state["ai_result"] = review_code_with_ai(client, code_input, language)
                    except Exception as err:
                        st.session_state["ai_result"] = None
                        st.error(f"Semantic Engine Error: {err}")
            
            if st.session_state.get("ai_result"):
                st.markdown(st.session_state["ai_result"])
    else:
        st.markdown("""
        <div style="padding: 32px; text-align: center; color: #94a3b8; background: #0d1527; border: 1px dashed #243552; border-radius: 10px; font-size: 1rem;">
            Click <b>🚀 Analyze & Audit Code</b> above to trigger deep semantic reasoning and refactoring suggestions.
        </div>
        """, unsafe_allow_html=True)