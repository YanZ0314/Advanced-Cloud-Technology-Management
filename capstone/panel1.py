import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Budget Planning & Cost Estimation", layout="wide")

st.title("Budget Planning & Cost Estimation")
st.write(
    "Estimate a 5-year cash-flow plan with yearly OpEx/CapEx projections and ROI metrics."
)

with st.sidebar:
    st.header("Inputs")
    year_1_opex = st.number_input(
        "1st Year OpEx ($)",
        min_value=0.0,
        value=216000.0,
        step=1000.0,
        help="Example default: $18K/mo AWS => $216K per year",
    )
    year_1_capex = st.number_input(
        "1st Year CapEx ($)",
        min_value=0.0,
        value=320000.0,
        step=1000.0,
        help="Example default: $320K/year server CapEx to be eliminated",
    )
    annual_opex_change_pct = st.number_input(
        "Annual OpEx change (%)",
        value=3.0,
        step=0.5,
        help="Positive values increase OpEx each year; negative values reduce it.",
    )
    annual_capex_change_pct = st.number_input(
        "Annual CapEx change (%)",
        value=-100.0,
        step=1.0,
        help="Use -100% for full CapEx elimination after Year 1 if desired.",
    )
    roi_horizon = st.slider("ROI Horizon (years)", min_value=1, max_value=5, value=3)


def project_values(start_value: float, annual_change_pct: float, years: int = 5) -> list[float]:
    values = [start_value]
    growth_factor = 1 + (annual_change_pct / 100.0)
    for _ in range(1, years):
        next_value = values[-1] * growth_factor
        values.append(max(next_value, 0.0))
    return values


years = [1, 2, 3, 4, 5]
opex_values = project_values(year_1_opex, annual_opex_change_pct)
capex_values = project_values(year_1_capex, annual_capex_change_pct)
total_cost = [op + cp for op, cp in zip(opex_values, capex_values)]

df = pd.DataFrame(
    {
        "Year": years,
        "OpEx ($)": opex_values,
        "CapEx ($)": capex_values,
        "Total Cash Flow ($)": total_cost,
    }
)
df["Cumulative Cash Flow ($)"] = df["Total Cash Flow ($)"].cumsum()

baseline_annual_cost = year_1_opex + year_1_capex
baseline_horizon_cost = baseline_annual_cost * roi_horizon
projected_horizon_cost = df.loc[df["Year"] <= roi_horizon, "Total Cash Flow ($)"].sum()
savings_horizon = baseline_horizon_cost - projected_horizon_cost
roi_pct = (
    (savings_horizon / projected_horizon_cost) * 100
    if projected_horizon_cost > 0
    else 0.0
)

col1, col2, col3 = st.columns(3)
col1.metric("Baseline Cost (ROI Horizon)", f"${baseline_horizon_cost:,.0f}")
col2.metric("Projected Cost (ROI Horizon)", f"${projected_horizon_cost:,.0f}")
col3.metric("ROI (%)", f"{roi_pct:,.1f}%")

st.session_state["panel1_export"] = {
    "baseline_annual_cost": float(baseline_annual_cost),
    "projected_horizon_cost": float(projected_horizon_cost),
    "roi_pct": float(roi_pct),
    "year_1_opex": float(year_1_opex),
    "year_1_capex": float(year_1_capex),
}

st.subheader("5-Year Cash Flow Table")
st.dataframe(
    df.style.format(
        {
            "OpEx ($)": "${:,.0f}",
            "CapEx ($)": "${:,.0f}",
            "Total Cash Flow ($)": "${:,.0f}",
            "Cumulative Cash Flow ($)": "${:,.0f}",
        }
    ),
    use_container_width=True,
)

st.subheader("Cost Projection Chart")
chart_df = df.melt(
    id_vars="Year",
    value_vars=["OpEx ($)", "CapEx ($)", "Total Cash Flow ($)"],
    var_name="Cost Type",
    value_name="Amount ($)",
)
fig = px.line(
    chart_df,
    x="Amount ($)",
    y="Year",
    color="Cost Type",
    markers=True,
    title="5-Year Projection (x=$, y=Year)",
)
fig.update_layout(yaxis=dict(dtick=1))
st.plotly_chart(fig, use_container_width=True)

st.subheader("Assumptions and Justification")
st.markdown(
    f"""
- **Time horizon:** 5 years, with ROI evaluation at **{roi_horizon} years**.
- **OpEx baseline assumption:** Year 1 starts at **${year_1_opex:,.0f}**, then changes by
  **{annual_opex_change_pct:.1f}% annually** (e.g., cloud usage growth, reserved instance pricing, inflation).
- **CapEx baseline assumption:** Year 1 starts at **${year_1_capex:,.0f}**, then changes by
  **{annual_capex_change_pct:.1f}% annually** (e.g., on-prem server refresh avoided in cloud migration scenarios).
- **Baseline for ROI comparison:** keeps Year 1 total cost flat every year
  (**${baseline_annual_cost:,.0f}/year**) to show impact from your entered annual change assumptions.
- **Interpretation:** Positive ROI indicates projected savings versus baseline over the selected horizon.
"""
)
