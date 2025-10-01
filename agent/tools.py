import pandas as pd
import matplotlib
# Use a non-interactive backend suitable for headless/test environments
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def convert_to_usd(df: pd.DataFrame, fx: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the 'amount' column of a DataFrame to USD using fx rates.

    Parameters:
        df (pd.DataFrame): DataFrame with columns ['month', 'currency', 'amount']
        fx (pd.DataFrame): DataFrame with columns ['month', 'currency', 'rate_to_usd']

    Returns:
        pd.DataFrame: Original DataFrame with new column 'amount_usd'
    """
    # Clean incoming data: drop rows with missing required keys
    required_cols = ["month", "currency", "amount"]
    clean_df = df.dropna(subset=required_cols)

    # Clean FX: keep only rows with complete keys and one rate per (month,currency)
    fx_required_cols = ["month", "currency", "rate_to_usd"]
    clean_fx = fx.dropna(subset=fx_required_cols)
    # If duplicates exist, prefer the first occurrence
    clean_fx = clean_fx.drop_duplicates(subset=["month", "currency"], keep="first")

    # Merge df with fx on month and currency
    merged = clean_df.merge(clean_fx, on=["month", "currency"], how="left")

    # Compute USD amount; rows lacking fx rate are dropped to ensure non-null amount_usd
    merged = merged.dropna(subset=["rate_to_usd"])  # ensure we can compute amount_usd
    merged["amount_usd"] = merged["amount"] * merged["rate_to_usd"]
    return merged



def get_revenue_vs_budget(month: str, entity: str, actuals: pd.DataFrame, budget: pd.DataFrame, fx: pd.DataFrame):
    """
    Returns Revenue vs Budget for a given month and entity in USD, with a bar chart.

    Parameters:
        month (str): Month in 'YYYY-MM' format
        entity (str): Entity name
        actuals (pd.DataFrame): Actuals data (with columns ['month','entity','account_category','amount','currency'])
        budget (pd.DataFrame): Budget data (same structure as actuals)
        fx (pd.DataFrame): FX rates (columns ['month','currency','rate_to_usd'])

    Returns:
        text (str), fig (matplotlib.figure.Figure)
    """

    # Convert to USD
    actuals_usd = convert_to_usd(actuals, fx)
    budget_usd = convert_to_usd(budget, fx)

    # Filter Revenue rows
    actual_rev = actuals_usd[
        (actuals_usd["month"] == month) &
        (actuals_usd["entity"] == entity) &
        (actuals_usd["account_category"] == "Revenue")
    ]["amount_usd"].sum()

    budget_rev = budget_usd[
        (budget_usd["month"] == month) &
        (budget_usd["entity"] == entity) &
        (budget_usd["account_category"] == "Revenue")
    ]["amount_usd"].sum()

    # Prepare text
    text = f"Revenue in {month} for {entity}: Actual ${actual_rev:,.0f} vs Budget ${budget_rev:,.0f}"

    # Create bar chart
    fig, ax = plt.subplots()
    ax.bar(["Actual", "Budget"], [actual_rev, budget_rev], color=["blue", "orange"])
    ax.set_title(f"Revenue vs Budget - {month} ({entity})")
    ax.set_ylabel("USD")

    return text, fig



def get_gross_margin_trend1(actuals: pd.DataFrame, fx: pd.DataFrame, entity: str = "ParentCo"):
    """
    Calculate Gross Margin % trend over time for a given entity.

    Parameters:
        actuals (pd.DataFrame): Actuals data (columns: month, entity, account_category, amount, currency)
        fx (pd.DataFrame): FX rates (columns: month, currency, rate_to_usd)
        entity (str): Entity to filter (default: "ParentCo")

    Returns:
        text (str), fig (matplotlib.figure.Figure)
    """

    # Convert amounts to USD
    df_usd = convert_to_usd(actuals, fx)

    # Filter by entity
    df_usd = df_usd[df_usd["entity"] == entity]

    # Pivot table to have Revenue and COGS side by side per month
    pivot = df_usd.pivot_table(
        index="month",
        columns="account_category",
        values="amount_usd",
        aggfunc="sum"
    ).reset_index()

    # Calculate Gross Margin %
    pivot["GrossMarginPct"] = (pivot["Revenue"] - pivot["COGS"]) / pivot["Revenue"] * 100

    # Prepare text
    text = f"Gross Margin % Trend for {entity}:"

    # Plot trend
    fig, ax = plt.subplots()
    ax.plot(pivot["month"], pivot["GrossMarginPct"], marker="o", linestyle="-", color="green")
    ax.set_title(f"Gross Margin % Trend - {entity}")
    ax.set_xlabel("Month")
    ax.set_ylabel("Gross Margin %")
    plt.xticks(rotation=45)
    plt.tight_layout()

    return text, fig


def get_opex_breakdown1(month: str, entity: str, actuals: pd.DataFrame, fx: pd.DataFrame):
    """
    Returns Opex total by category for a given month and entity in USD, with a bar chart.

    Parameters:
        month (str): Month in 'YYYY-MM' format
        entity (str): Entity name
        actuals (pd.DataFrame): Actuals data (columns: month, entity, account_category, amount, currency)
        fx (pd.DataFrame): FX rates (columns: month, currency, rate_to_usd)

    Returns:
        text (str), fig (matplotlib.figure.Figure)
    """

    # Convert amounts to USD
    df_usd = convert_to_usd(actuals, fx)

    # Filter for entity and month, and only Opex categories
    opex_df = df_usd[
        (df_usd["month"] == month) &
        (df_usd["entity"] == entity) &
        (df_usd["account_category"].str.startswith("Opex"))
    ]

    # Group by category and sum amounts
    opex_summary = opex_df.groupby("account_category")["amount_usd"].sum()

    # Prepare text
    text_lines = [f"Opex breakdown for {month} ({entity}):"]
    for category, amount in opex_summary.items():
        text_lines.append(f"{category}: ${amount:,.0f}")
    text = "\n".join(text_lines)

    # Plot bar chart
    fig, ax = plt.subplots()
    ax.bar(opex_summary.index, opex_summary.values, color="purple")
    ax.set_title(f"Opex Breakdown - {month} ({entity})")
    ax.set_ylabel("USD")
    plt.xticks(rotation=45)
    plt.tight_layout()

    return text, fig


def get_ebitda_trend(actuals: pd.DataFrame, fx: pd.DataFrame, entity: str = "ParentCo"):
    """
    Calculate EBITDA (proxy) trend over time for a given entity.
    EBITDA = Revenue - COGS - Opex (sum of all Opex:* categories)
    """
    df_usd = convert_to_usd(actuals, fx)
    df_usd = df_usd[df_usd["entity"] == entity]

    # Pivot to wide format
    pivot = df_usd.pivot_table(
        index="month",
        columns="account_category",
        values="amount_usd",
        aggfunc="sum"
    ).reset_index()
    print(pivot)
    # Compute Opex as sum of all "Opex:*" columns
    opex_cols = [c for c in pivot.columns if isinstance(c, str) and c.startswith("Opex")]
    pivot["OpexTotal"] = pivot[opex_cols].sum(axis=1) if opex_cols else 0

    # Compute EBITDA
    pivot["EBITDA"] = pivot["Revenue"] - pivot["COGS"] - pivot["OpexTotal"]

    # Text output
    text = f"EBITDA trend for {entity} over time."

    # Plot
    fig, ax = plt.subplots()
    ax.plot(pivot["month"], pivot["EBITDA"], marker="o", color="purple", label="EBITDA")
    ax.set_title(f"EBITDA Trend - {entity}")
    ax.set_xlabel("Month")
    ax.set_ylabel("USD")
    ax.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()

    return text, fig


def get_ebitda_vs_budget(month: str, entity: str, actuals: pd.DataFrame, budget: pd.DataFrame, fx: pd.DataFrame):
    """
    Compare Actual vs Budget EBITDA for a given month and entity.

    EBITDA = Revenue - COGS - Opex
    """
    actuals_usd = convert_to_usd(actuals, fx)
    budget_usd = convert_to_usd(budget, fx)

    # Filter entity + month
    a = actuals_usd[(actuals_usd["month"] == month) & (actuals_usd["entity"] == entity)]
    b = budget_usd[(budget_usd["month"] == month) & (budget_usd["entity"] == entity)]

    def compute_ebitda(df):
        revenue = df[df["account_category"] == "Revenue"]["amount_usd"].sum()
        cogs = df[df["account_category"] == "COGS"]["amount_usd"].sum()
        opex = df[df["account_category"].str.startswith("Opex")]["amount_usd"].sum()
        return revenue - cogs - opex

    actual_ebitda = compute_ebitda(a)
    budget_ebitda = compute_ebitda(b)

    # Text
    text = f"EBITDA in {month} for {entity}: Actual ${actual_ebitda:,.0f} vs Budget ${budget_ebitda:,.0f}"

    # Chart
    fig, ax = plt.subplots()
    ax.bar(["Actual", "Budget"], [actual_ebitda, budget_ebitda], color=["blue", "orange"])
    ax.set_title(f"EBITDA vs Budget - {month} ({entity})")
    ax.set_ylabel("USD")

    return text, fig


def get_cash_runway(cash: pd.DataFrame, actuals: pd.DataFrame, fx: pd.DataFrame, entity: str = "ParentCo"):
    """
    Calculate cash runway in months for a given entity.
    Cash Runway = Latest Cash / Average Monthly Net Burn (last 3 months)

    Parameters:
        cash (pd.DataFrame): cash.csv with columns ['month', 'entity', 'cash_usd']
        actuals (pd.DataFrame): actuals.csv
        fx (pd.DataFrame): fx.csv
        entity (str): entity name

    Returns:
        text (str), fig (matplotlib.figure.Figure)
    """
    import matplotlib.pyplot as plt

    # Convert actuals to USD
    df_usd = convert_to_usd(actuals, fx)
    df_usd = df_usd[df_usd["entity"] == entity]

    # Compute Opex per month
    df_usd["is_opex"] = df_usd["account_category"].str.startswith("Opex")
    monthly = df_usd.groupby("month").apply(
        lambda g: pd.Series({
            "Revenue": g[g["account_category"] == "Revenue"]["amount_usd"].sum(),
            "COGS": g[g["account_category"] == "COGS"]["amount_usd"].sum(),
            "Opex": g[g["is_opex"]]["amount_usd"].sum(),
        })
    ).reset_index()

    # Compute Net Burn = COGS + Opex - Revenue (cash outflow)
    monthly["NetBurn"] = monthly["COGS"] + monthly["Opex"] - monthly["Revenue"]

    # Average over last 3 months
    last3 = monthly.sort_values("month").tail(3)
    avg_burn = last3["NetBurn"].mean()

    # Get latest cash balance for entity; fall back to overall latest if entity missing
    cash_clean = cash.dropna(subset=["month", "entity", "cash_usd"]).copy()
    entity_cash = cash_clean[cash_clean["entity"] == entity].sort_values("month")
    if len(entity_cash) > 0:
        latest_cash = entity_cash.iloc[-1]["cash_usd"]
    else:
        overall_latest = cash_clean.sort_values("month")
        if len(overall_latest) == 0:
            latest_cash = 0.0
        else:
            latest_cash = overall_latest.iloc[-1]["cash_usd"]

    # Cash Runway in months
    if avg_burn > 0:
        runway_months = latest_cash / avg_burn
    else:
        runway_months = float('inf')  # No burn, infinite runway

    text = f"Cash Runway for {entity}: {runway_months:.1f} months (latest cash ${latest_cash:,.0f}, avg burn ${avg_burn:,.0f}/month)"

    # Optional: plot cash and net burn trend
    fig, ax = plt.subplots()
    ax.plot(monthly["month"], monthly["NetBurn"], marker="o", linestyle="-", label="Net Burn")
    ax.axhline(0, color="black", linewidth=0.8)
    ax.set_title(f"Cash Burn Trend - {entity}")
    ax.set_xlabel("Month")
    ax.set_ylabel("USD")
    plt.xticks(rotation=45)
    plt.legend()
    plt.tight_layout()

    return text, fig

