"""
Revenue growth rate model based on Porter's Five Forces and business factors.
"""

def calculate_growth_rates(
    initial_growth_rate: float,
    competition: float,
    new_entrant: float,
    supplier_power: float,
    buyer_power: float,
    substitute: float,
    product_market_fit: float,
    differentiator: float,
    adaptive_learning: float,
    deep_learning: float,
    process_mgmt: float,
    weights: dict,
    years: int = 5,
) -> list[float]:
    """
    Calculate growth rates for each year considering variable evolution and cascading effects.
    """
    # Apply leadership effects to differentiator and substitute
    effective_differentiator = differentiator + adaptive_learning * 1.0 + deep_learning * 2.0
    effective_substitute = max(0, substitute - deep_learning)
    
    # Process management effect on buyer power
    effective_buyer_power = buyer_power + process_mgmt
    
    rates = []
    comp = competition
    supp = supplier_power
    buy = buyer_power
    diff = effective_differentiator
    
    for year in range(1, years + 1):
        # Annual competition increase (at least 0.05)
        comp_delta = 0.05
        
        # Cascading effects (per 0.1 change in driving variable)
        comp_delta += new_entrant * 0.5      # +0.05 if new_entrant +0.1
        comp_delta -= supplier_power * 0.5   # -0.05 if supplier +0.1
        comp_delta += effective_buyer_power * 0.5  # +0.05 if buyer +0.1
        comp_delta -= diff * 0.5             # -0.05 if differentiator +0.1
        
        comp = min(1.0, max(0, comp + comp_delta * 0.2))  # Scale for annual update
        
        # Supplier/Buyer cascading from differentiator changes
        if year > 1:
            supp = min(1.0, supp + diff * 0.05)
            buy = min(1.0, buy + (1 - diff) * 0.05)
        
        # Direct effects on growth (per 0.1 change = 1 unit of effect)
        # competition +0.1 -> -1%, buyer +0.1 -> -1%, new_entrant +0.1 -> -1%
        # supplier +0.1 -> +1%, substitute +0.1 -> -10%, pmf +0.1 -> +0.5%, diff +0.1 -> +0.5%
        w = weights
        
        growth_delta = (
            -10 * comp * w.get("competition", 1.0) +
            -10 * new_entrant * w.get("new_entrant", 1.0) +
            10 * supp * w.get("supplier", 1.0) +
            -10 * buy * w.get("buyer", 1.0) +
            -100 * effective_substitute * w.get("substitute", 1.0) +
            5 * product_market_fit * w.get("product_market_fit", 1.0) +
            5 * diff * w.get("differentiator", 1.0)
        )
        
        rate = initial_growth_rate + growth_delta
        rate = max(-99, min(99, rate))
        rates.append(rate)
    
    return rates


def revenue_from_growth(initial_revenue: float, growth_rates: list[float]) -> list[float]:
    """Compute revenue each year from initial revenue and growth rates."""
    revenues = [initial_revenue]
    for g in growth_rates:
        revenues.append(revenues[-1] * (1 + g / 100))
    return revenues[1:]  # Exclude year 0


def cash_flow_table(
    initial_capital: float,
    initial_expense: float,
    revenues: list[float],
    growth_rates: list[float],
) -> dict:
    """Build 5-year cash flow table."""
    capital = initial_capital
    cumulative = capital
    
    rows = []
    for year, (rev, gr) in enumerate(zip(revenues, growth_rates), 1):
        expense = initial_expense  # Fixed expense per year
        net_profit = rev - expense
        cumulative += net_profit
        
        rows.append({
            "Year": year,
            "Capital": capital if year == 1 else 0,
            "Revenue": rev,
            "Expense": expense,
            "Net Profit": net_profit,
            "Cumulative Cash": cumulative,
        })
        capital = 0  # No new capital in following years
    
    return rows
