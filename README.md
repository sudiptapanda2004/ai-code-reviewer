# 🛡️ AI-Powered Automated Code Reviewer & Vulnerability Scanner

A hybrid code inspection tool combining deterministic static code analysis with Large Language Model (LLM) reasoning to catch security vulnerabilities, compute maintainability metrics, and provide context-aware code refactoring.

---

## 🚀 Key Features

* **Deterministic Static AST Inspection:** Analyzes Python's Abstract Syntax Tree (`ast`) to catch critical security risks such as unsafe evaluations (`eval()`, `exec()`) and hardcoded credentials.
* **Radon Software Metrics:** Computes Cyclomatic Complexity (CC) and Maintainability Index (MI) scores.
* **Semantic LLM Review:** Uses the Google Gemini 2.5 Flash model to detect logic flaws, performance bottlenecks, and generate clean, secure refactored code.
* **Interactive UI:** Built using Streamlit for instant feedback and side-by-side diagnostic views.

---

## 🛠️ Tech Stack

* **Language:** Python 3.10+
* **Frontend / Dashboard:** [Streamlit](https://streamlit.io/)
* **Static Analysis:** Python `ast` module, [Radon](https://radon.readthedocs.io/)
* **AI Engine:** Google Gemini API (`gemini-2.5-flash` via `google-genai` SDK)

---

## 📦 Installation & Setup

### 1. Clone the repository
```bash
git clone [https://github.com/YOUR_USERNAME/ai-code-reviewer.git](https://github.com/YOUR_USERNAME/ai-code-reviewer.git)
cd ai-code-reviewer

# Create and activate a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

# 🔑 Configuration
Get a free Gemini API key from Google AI Studio and enter it in the application's sidebar to activate semantic review.

