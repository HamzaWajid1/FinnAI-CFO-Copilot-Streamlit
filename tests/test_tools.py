# At the top of test_tools.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


import pandas as pd
import pytest
from agent.tools import (
    convert_to_usd,
    get_revenue_vs_budget,
    get_gross_margin_trend1,
    get_opex_breakdown1,
    get_ebitda_trend,
    get_ebitda_vs_budget,
    get_cash_runway
)
import matplotlib.pyplot as plt

# --- Load fixture CSVs ---
@pytest.fixture
def actuals():
    return pd.read_csv("fixtures/data.csv")

@pytest.fixture
def budget():
    return pd.read_csv("fixtures/budget.csv")

@pytest.fixture
def fx():
    return pd.read_csv("fixtures/fx.csv")

@pytest.fixture
def cash():
    return pd.read_csv("fixtures/cash.csv")

entity = "ParentCo"
month = "2023-01"

# --- Test convert_to_usd ---
def test_convert_to_usd(actuals, fx):
    df_usd = convert_to_usd(actuals, fx)
    assert "amount_usd" in df_usd.columns
    assert df_usd["amount_usd"].notnull().all()

# --- Test revenue vs budget ---
def test_revenue_vs_budget(actuals, budget, fx):
    text, fig = get_revenue_vs_budget(month, entity, actuals, budget, fx)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)

# --- Test gross margin trend ---
def test_gross_margin_trend(actuals, fx):
    text, fig = get_gross_margin_trend1(actuals, fx, entity)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)

# --- Test opex breakdown ---
def test_opex_breakdown(actuals, fx):
    text, fig = get_opex_breakdown1(month, entity, actuals, fx)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)

# --- Test EBITDA trend ---
def test_ebitda_trend(actuals, fx):
    text, fig = get_ebitda_trend(actuals, fx, entity)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)

# --- Test EBITDA vs budget ---
def test_ebitda_vs_budget(actuals, budget, fx):
    text, fig = get_ebitda_vs_budget(month, entity, actuals, budget, fx)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)

# --- Test cash runway ---
def test_cash_runway(cash, actuals, fx):
    text, fig = get_cash_runway(cash, actuals, fx, entity)
    assert isinstance(text, str)
    assert isinstance(fig, plt.Figure)
