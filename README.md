# 🛡️ AI-Powered Automated Code Reviewer & Vulnerability Scanner

A hybrid code intelligence and security auditing platform built with Python, Streamlit, and Google GenAI. The application combines local deterministic parsing (Abstract Syntax Trees and Radon software metrics) with Large Language Model semantic reasoning to deliver real-time vulnerability detection, maintainability scoring, and automated refactoring.

---

## 🚀 Key Features

- **Hybrid Analysis Architecture:** 
  - **Deterministic Static Engine:** Uses Python's native `ast` module and regex heuristic scanners to detect dangerous calls (`eval`, `exec`, `system`, `gets`) and exposed credentials without latency.
  - **Quantitative Code Metrics:** Computes real-time **Cyclomatic Complexity (CC)** and **Maintainability Index (MI)** via `radon`.
  - **Semantic AI Engine:** Leverages Google's Gemini Flash model to identify subtle logical bugs, memory hazards, edge-case failures, and generate clean, idiomatic refactors.
- **Multi-Language Support:** Static checks and AI review configured for **Python, Java, JavaScript, C, C++, and Go**.
- **Modular Design:** Strict Separation of Concerns (SoC) dividing templates, static analyzers, and AI client logic.
- **Enterprise Secret Management:** Secure credential loading via background `.env` configurations.

---

## 🛠️ Project Architecture

ai-code-reviewer/
│
├── .env.example          # Template for required environment variables
├── .gitignore            # Excludes venv, .env, and cache files
├── requirements.txt      # Project dependencies
├── README.md             # Documentation
│
├── templates.py          # Pre-configured multi-language code snippets
├── analyzers.py          # AST parser, regex security checks, Radon metrics
├── ai_engine.py          # Gemini API client with automated retry/fallback logic
└── app.py                # Streamlit UI controller and presentation layer

---

## 📦 Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/](https://github.com/)<YOUR_USERNAME>/ai-code-reviewer.git
   cd ai-code-reviewer

# Create and activate a virtual environment:
 python -m venv venv
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Install dependencies:
pip install -r requirements.txt

# Configure API Credentials:
Create a .env file in the project root:
GEMINI_API_KEY=your_gemini_api_key_here

# Run the Application:
streamlit run app.py