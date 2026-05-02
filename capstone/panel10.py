import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Final Simulation Dashboard", layout="wide")

st.title("Final Simulation Dashboard")
st.write(
    "Linked simulation across cost, uptime, and adoption. "
    "Values can auto-seed from earlier panels through shared session exports."
)

panel1_export = st.session_state.get("panel1_export", {})
panel6_export = st.session_state.get("panel6_export", {})
panel8_export = st.session_state.get("panel8_export", {})
panel9_export = st.session_state.get("panel9_export", {})

default_cost = float(
    panel6_export.get(
        "monthly_cost_usd",
        panel1_export.get("baseline_annual_cost", 240000.0) / 12.0,
    )
)
default_uptime = float(panel6_export.get("expected_uptime_pct", 99.3))
default_adoption = float(
    panel9_export.get("final_adoption_pct", panel8_export.get("final_adoption_pct", 55.0))
)

with st.sidebar:
    st.header("Linked Inputs")
    monthly_cost_usd = st.slider("Monthly Cost (USD)", 5000, 80000, int(default_cost), 500)
    uptime_pct = st.slider("Expected Uptime (%)", 98.0, 99.99, default_uptime, 0.01)
    base_adoption_pct = st.slider(
        "Base Adoption Potential (%)", 10.0, 95.0, default_adoption, 0.5
    )
    months = st.slider("Projection Horizon (months)", 6, 36, 18, 1)


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


cost_efficiency_score = clamp(100.0 - (monthly_cost_usd - 5000) / 750.0, 0.0, 100.0)
uptime_factor = clamp(0.65 + ((uptime_pct - 98.0) / 1.99) * 0.45, 0.65, 1.10)
cost_factor = clamp(0.75 + (cost_efficiency_score / 100.0) * 0.35, 0.75, 1.10)
linked_adoption_ceiling = clamp(base_adoption_pct * uptime_factor * cost_factor, 15.0, 99.0)

records = []
curve_speed = 0.22 + ((uptime_pct - 98.0) / 1.99) * 0.12
for month in range(1, months + 1):
    progress = 1 - (2.71828 ** (-curve_speed * month))
    adoption_pct = linked_adoption_ceiling * progress
    records.append({"Month": month, "Linked Adoption (%)": adoption_pct})

df = pd.DataFrame(records)
final_adoption = float(df.iloc[-1]["Linked Adoption (%)"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Monthly Cost", f"${monthly_cost_usd:,.0f}")
col2.metric("Expected Uptime", f"{uptime_pct:.2f}%")
col3.metric("Adoption Ceiling (Linked)", f"{linked_adoption_ceiling:.1f}%")
col4.metric(f"Adoption by Month {months}", f"{final_adoption:.1f}%")

st.subheader("Linked Adoption Curve")
fig = px.line(
    df,
    x="Month",
    y="Linked Adoption (%)",
    markers=True,
    title="Cost + Uptime Adjusted Adoption Over Time",
)
fig.update_layout(xaxis=dict(dtick=1), yaxis=dict(range=[0, 100]))
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.style.format({"Linked Adoption (%)": "{:.1f}%"}), use_container_width=True)

st.caption(
    "Link logic: lower monthly cost improves affordability, higher uptime improves trust; "
    "both increase achievable adoption and adoption speed."
)
