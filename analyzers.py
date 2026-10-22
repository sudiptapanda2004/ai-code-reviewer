import ast
import re
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def run_python_ast(code_str: str, check_unsafe: bool = True):
    """Deep AST analysis specific to Python."""
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
            "desc": f"Python Syntax Error: {e.msg}"
        })
    return findings

def run_regex_security_scanner(code_str: str, check_unsafe: bool = True, check_hardcoded: bool = True):
    """Language-agnostic regex security scanner for secrets and dangerous functions."""
    findings = []
    lines = code_str.split("\n")

    dangerous_patterns = [
        (r'\b(eval|exec)\s*\(', "High-risk dynamic code execution (`eval`/`exec`) detected."),
        (r'\bgets\s*\(', "Highly dangerous `gets()` call detected. Vulnerable to critical buffer overflow."),
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
    """Computes Radon metrics for Python code."""
    try:
        blocks = cc_visit(code_str)
        total_cc = sum(b.complexity for b in blocks)
        mi_score = mi_visit(code_str, multi=False)
        return total_cc, mi_score
    except Exception:
        return 0, 100.0