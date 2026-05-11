import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="AI Degree Advisor — Reliability vs Cost", layout="wide")

st.title("Performance & Resilience Design")
st.write(
    "Simulate availability and cost trade-offs for the **student- and advisor-facing** advising platform: "
    "redundancy and region strategy vs. monthly run rate."
)

base_cost = 12000

with st.sidebar:
    st.header("Scenario Inputs")
    selected_redundancy = st.slider(
        "Redundancy Level",
        min_value=1,
        max_value=5,
        value=3,
        help="Higher levels increase resiliency and monthly operating cost.",
    )
    region_mode = st.toggle(
        "Multi-Region",
        value=False,
        help="Enable to model active-active deployment across two regions.",
    )


def estimate_uptime_cost(level: int, is_multi_region: bool) -> tuple[float, float]:
    # Explicit uptime targets per redundancy level.
    uptime_map = {1: 99.00, 2: 99.20, 3: 99.50, 4: 99.90, 5: 99.99}
    base_uptime = uptime_map.get(level, 99.00)
    # Multi-region adds a reliability boost.
    uptime = base_uptime + (0.22 if is_multi_region else 0.0)
    uptime = min(uptime, 99.99)

    # Explicit monthly base costs — Level 3→4 jump is intentionally steep,
    # reflecting the addition of active failover, cross-zone replication, and DR tooling.
    cost_map = {1: 12000, 2: 15600, 3: 20280, 4: 38000, 5: 48000}
    region_multiplier = 1.45 if is_multi_region else 1.0
    monthly_cost = cost_map.get(level, 12000) * region_multiplier
    return uptime, monthly_cost


points = []
for redundancy in range(1, 6):
    uptime_pct, monthly_cost = estimate_uptime_cost(redundancy, region_mode)
    points.append(
        {
            "Redundancy Level": redundancy,
            "Expected Uptime (%)": uptime_pct,
            "Monthly Cost (USD)": monthly_cost,
        }
    )

curve_df = pd.DataFrame(points)
selected_row = curve_df.loc[curve_df["Redundancy Level"] == selected_redundancy].iloc[0]

col1, col2, col3 = st.columns(3)
col1.metric("Deployment Mode", "Multi-Region" if region_mode else "Single-Region")
col2.metric("Expected Uptime", f"{selected_row['Expected Uptime (%)']:.2f}%")
col3.metric("Monthly Cost", f"${selected_row['Monthly Cost (USD)']:,.0f}")

st.session_state["panel6_export"] = {
    "redundancy_level": int(selected_redundancy),
    "region_mode": "Multi-Region" if region_mode else "Single-Region",
    "expected_uptime_pct": float(selected_row["Expected Uptime (%)"]),
    "monthly_cost_usd": float(selected_row["Monthly Cost (USD)"]),
}

st.subheader("Uptime vs Monthly Cost Curve")
fig = px.line(
    curve_df,
    x="Monthly Cost (USD)",
    y="Expected Uptime (%)",
    markers=True,
    text="Redundancy Level",
    title="Cost-Reliability Trade-off by Redundancy Level (Non-Linear Cost Curve)",
)
fig.update_traces(textposition="top center")
fig.update_layout(
    xaxis_title="Monthly Cost (USD)",
    yaxis_title="Expected Uptime (%)",
    template="plotly_dark",
    paper_bgcolor="#1E2330",
    plot_bgcolor="#1E2330",
    font=dict(family="Inter, sans-serif", color="#F0F4FF"),
    title_font=dict(family="Inter, sans-serif", color="#F0F4FF", size=15),
    margin=dict(l=40, r=20, t=40, b=40),
)
st.plotly_chart(fig, use_container_width=True)

st.subheader("Scenario Table")
st.dataframe(
    curve_df.style.format(
        {"Expected Uptime (%)": "{:.2f}%", "Monthly Cost (USD)": "${:,.0f}"}
    ),
    use_container_width=True,
)

st.info(
    f"Current selection: Redundancy Level {selected_redundancy} in "
    f"{'Multi-Region' if region_mode else 'Single-Region'} mode."
)
