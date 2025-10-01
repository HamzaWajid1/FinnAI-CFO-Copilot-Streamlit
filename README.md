title: "💼 CFO Copilot (FP&A Coding Assignment)"

description: |
  This is a mini "CFO Copilot" built as part of a coding assessment.
  The app allows a CFO to ask questions about monthly financials (from CSV/Excel files)
  and get back concise answers with charts.

features:
  - Natural language Q&A interface for finance metrics
  - Metrics supported:
      - Revenue vs Budget (USD)
      - Gross Margin % = (Revenue – COGS) / Revenue
      - Opex total grouped by category
      - EBITDA = Revenue – COGS – Opex
      - Cash runway = cash ÷ average monthly net burn (last 3 months)
  - Inline charts (matplotlib) in Streamlit
  - Simple, board-ready answers
  - Unit tests with pytest

project_structure: |
  app.py             # Streamlit app (entry point)
  requirements.txt   # Python dependencies
  README.md          # Documentation
  agent/             # Agent and data tools
    ├── agent.py     # Intent classifier + dispatcher
    └── tools.py     # Finance metric functions
  fixtures/          # Data files (actuals, budget, fx, cash)
  tests/             # Unit tests
    └── test_tools.py

setup:
  steps:
    - "Clone the repository"
    - "cd 'FinnAI coding assignment'"
    - "python -m venv venv"
    - ".\\venv\\Scripts\\activate   # Windows"
    - "pip install -r requirements.txt"

run_app: |
  streamlit run app.py

run_tests: |
  pytest

data:
  location: "fixtures/data.xlsx"
  sheets:
    - actuals
    - budget
    - fx
    - cash

demo_examples:
  - "What was June 2025 revenue vs budget?"
  - "Show Gross Margin % trend"
