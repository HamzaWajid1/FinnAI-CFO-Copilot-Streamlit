import re
from datetime import datetime
from agent.tools import (
    get_revenue_vs_budget,
    get_gross_margin_trend1,
    get_opex_breakdown1,
    get_ebitda_trend,
    get_ebitda_vs_budget,
    get_cash_runway
)

INTENT_FUNCTION_MAP = {
    "revenue_vs_budget": get_revenue_vs_budget,
    "gross_margin_trend": get_gross_margin_trend1,
    "opex_breakdown": get_opex_breakdown1,
    "ebitda_trend": get_ebitda_trend,
    "ebitda_vs_budget": get_ebitda_vs_budget,
    "cash_runway": get_cash_runway,
}

def parse_month_year(text: str) -> str | None:
    """
    Convert user input like 'June 2024' or 'April 2023' to 'YYYY-MM' format.
    """
    try:
        dt = datetime.strptime(text, "%B %Y")  # Full month name + year
        return dt.strftime("%Y-%m")
    except ValueError:
        return None

def classify_intent(question: str) -> str:
    q = question.lower()
    if "revenue" in q and "budget" in q:
        return "revenue_vs_budget"
    elif "gross margin" in q:
        return "gross_margin_trend"
    elif "opex" in q:
        return "opex_breakdown"
    elif "ebitda" in q and "budget" not in q:
        return "ebitda_trend"
    elif "ebitda" in q and "budget" in q:
        return "ebitda_vs_budget"
    elif "cash runway" in q:
        return "cash_runway"
    else:
        return "unknown"

def run_agent(question: str, actuals, budget, fx, cash=None, default_entity="ParentCo"):
    """
    Takes a user question and returns text + chart by calling the correct data function.
    """
    intent = classify_intent(question)
    
    if intent == "unknown":
        return "Sorry, I could not understand the question.", None
    
    func = INTENT_FUNCTION_MAP[intent]

    # Extract 'Month Year' from question (e.g., June 2024) and convert to YYYY-MM
    month_match = re.search(
        r"(January|February|March|April|May|June|July|August|September|October|November|December) \d{4}",
        question,
        re.IGNORECASE
    )
    month = parse_month_year(month_match.group(0)) if month_match else None

    # Call the correct function based on intent
    if intent == "revenue_vs_budget":
        if not month:
            return "Please specify the month (e.g., June 2024) for Revenue vs Budget.", None
        return func(month, default_entity, actuals, budget, fx)
    
    elif intent == "gross_margin_trend":
        return func(actuals, fx, default_entity)
    
    elif intent == "opex_breakdown":
        if not month:
            return "Please specify the month (e.g., June 2024) for Opex breakdown.", None
        return func(month, default_entity, actuals, fx)
    
    elif intent == "ebitda_trend":
        return func(actuals, fx, default_entity)
    
    elif intent == "ebitda_vs_budget":
        if not month:
            return "Please specify the month (e.g., June 2024) for EBITDA vs Budget.", None
        return func(month, default_entity, actuals, budget, fx)
    
    elif intent == "cash_runway":
        if cash is None:
            return "Cash data not provided.", None
        return func(cash, actuals, fx, default_entity)
    
    else:
        return "Intent not implemented.", None
