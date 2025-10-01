## 💼 CFO Copilot (FP&A Coding Assignment)

This project is a mini "CFO Copilot" that answers finance questions from monthly CSVs and returns concise, board-ready answers with charts.

### Features
- **Natural language Q&A** about finance metrics via `Streamlit` UI
- **Metrics supported** via `agent/tools.py`:
  - Revenue vs Budget (USD)
  - Gross Margin % = (Revenue – COGS) / Revenue
  - Opex total grouped by category
  - EBITDA = Revenue – COGS – Opex
  - Cash Runway = latest cash ÷ avg monthly net burn (last 3 months)
- **Inline charts** rendered with `matplotlib`
- **Export to PDF** button for the current answer + chart
- **Unit tests** with `pytest`

### Project Structure
```
app.py             # Streamlit app (entry point)
requirements.txt   # Python dependencies
README.md          # Documentation
agent/
  ├── agent.py     # Lightweight intent/dispatch to metric functions
  └── tools.py     # Finance metric functions
fixtures/          # CSV data: data.csv, budget.csv, fx.csv, cash.csv
tests/
  └── test_tools.py
```

### Setup
```bash
python -m venv venv
./venv/Scripts/activate   # Windows
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run app.py
```

### Run Tests
```bash
pytest
```

### Data Inputs (fixtures/)
- `data.csv` (actuals): `month, entity, account_category, amount, currency`
- `budget.csv`: same columns as actuals
- `fx.csv`: `month, currency, rate_to_usd`
- `cash.csv`: `month, entity, cash_usd`

The code hardens joins and drops bad rows so messy CSV tails won’t break calculations.

### How It Works
- `agent/agent.py` parses a user question and routes it to a function in `agent/tools.py`.
- Each function returns `(text, fig)` where `fig` is a Matplotlib figure (or `None`).
- `app.py` loads fixtures once, calls `run_agent`, displays the text and chart, and can export a simple PDF snapshot.

### Notes
- This project uses a non-interactive Matplotlib backend (`Agg`) for compatibility with tests and headless environments.
- Virtual environments and generated artifacts are excluded via `.gitignore`.

### Example Questions
- “What was January 2023 revenue vs budget for ParentCo?”
- “Show Gross Margin % trend for ParentCo.”
