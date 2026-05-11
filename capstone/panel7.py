import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Innovation & AI Integration", layout="wide")

st.title("Innovation & AI Integration")
st.write(
    "Simulate ROI sensitivity for **AI Degree Advisor** investments (pathway models, degree audit AI, "
    "early-warning analytics) and **data quality** (SIS/degree rules completeness). "
    "Includes diminishing returns at high spend."
)

with st.sidebar:
    st.header("Scenario Inputs")
    selected_investment_k = st.slider(
        "AI Investment (K USD)",
        min_value=0,
        max_value=500,
        value=200,
        step=10,
    )
    data_quality_pct = st.slider(
        "Data Quality (%)",
        min_value=0,
        max_value=100,
        value=80,
        step=1,
    )


def roi_percent(investment_k: float, data_quality: float) -> float:
    """
    ROI model:
    - Benefit grows quickly then plateaus around 300K (diminishing returns).
    - Data quality scales value creation, with strongest practical gains near 80%.
    """
    quality_factor = min(data_quality / 80.0, 1.0)
    max_benefit_k = 320.0 * quality_factor
    growth_component = 1 - np.exp(-investment_k / 180.0)
    expected_benefit_k = max_benefit_k * growth_component
    if investment_k <= 0:
        return 0.0
    return ((expected_benefit_k - investment_k) / investment_k) * 100.0


investment_points_k = np.arange(10, 501, 10)
roi_points = [roi_percent(float(inv), float(data_quality_pct)) for inv in investment_points_k]

curve_df = pd.DataFrame(
    {
        "Investment (K USD)": investment_points_k,
        "ROI (%)": roi_points,
    }
)

selected_roi = roi_percent(float(selected_investment_k), float(data_quality_pct))
selected_zone = (
    "Under-investment"
    if selected_investment_k < 150
    else "Optimal range"
    if selected_investment_k <= 300
    else "Over-investment risk"
)

metric_col1, metric_col2, metric_col3 = st.columns(3)
metric_col1.metric("AI Investment", f"${selected_investment_k:,.0f}K")
metric_col2.metric("Data Quality", f"{data_quality_pct}%")
metric_col3.metric("Estimated ROI", f"{selected_roi:.1f}%")

st.subheader("ROI Curve with Investment Zones")
fig = px.line(
    curve_df,
    x="Investment (K USD)",
    y="ROI (%)",
    title="ROI Sensitivity Curve",
    markers=True,
)
fig.add_vrect(x0=0, x1=150, fillcolor="#f59e0b", opacity=0.15, line_width=0)
fig.add_vrect(x0=150, x1=300, fillcolor="#22c55e", opacity=0.12, line_width=0)
fig.add_vrect(x0=300, x1=500, fillcolor="#ef4444", opacity=0.10, line_width=0)
fig.add_vline(x=selected_investment_k, line_width=2, line_dash="dash", line_color="#2563eb")
fig.add_annotation(
    x=selected_investment_k,
    y=selected_roi,
    text=f"Selected: {selected_roi:.1f}%",
    showarrow=True,
    arrowhead=2,
)
fig.update_layout(
    xaxis_title="AI Investment (K USD)",
    yaxis_title="ROI (%)",
    template="plotly_dark",
    paper_bgcolor="#1E2330",
    plot_bgcolor="#1E2330",
    font=dict(family="Inter, sans-serif", color="#F0F4FF"),
    title_font=dict(family="Inter, sans-serif", color="#F0F4FF", size=15),
    margin=dict(l=40, r=20, t=40, b=40),
)
st.plotly_chart(fig, use_container_width=True)

st.markdown(
    """
- **Under-investment (0-150K):** ROI is constrained by limited AI capability deployment.
- **Optimal range (150-300K):** Best balance of ROI and scale; gains accelerate here.
- **Over-investment risk (300-500K):** Diminishing returns; ROI tends to plateau.
"""
)

st.info(
    f"Current scenario is **{selected_zone}** at `${selected_investment_k}K` "
    f"investment with `{data_quality_pct}%` data quality."
)
