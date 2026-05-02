import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Product Diffusion & Market Strategy", layout="wide")

st.title("Product Diffusion & Market Strategy")
st.write(
    "Model customer adoption using marketing spend and network effects, "
    "with different dynamics for B2B and B2C markets."
)

with st.sidebar:
    st.header("Scenario Inputs")
    market_type = st.selectbox("Market", options=["B2B", "B2C"], index=1)
    marketing_pct = st.slider("Marketing Spend (% of target budget)", 0, 100, 55, 1)
    network_effect = st.slider("Network Effect Strength", 0.0, 1.0, 0.6, 0.05)
    horizon_months = st.slider("Time Horizon (months)", 6, 36, 18, 1)


def logistic_adoption(month: int, market: str, mkt_pct: int, net_effect: float) -> float:
    market_scale = 1.08 if market == "B2C" else 0.90
    market_center_shift = -1.2 if market == "B2C" else 1.8

    growth_rate = (0.10 + (mkt_pct / 100.0) * 0.14 + net_effect * 0.24) * market_scale
    midpoint = 10.0 - (mkt_pct / 100.0) * 3.0 - net_effect * 3.8 + market_center_shift

    adoption = 100.0 / (1.0 + math.exp(-growth_rate * (month - midpoint)))
    return max(0.0, min(100.0, adoption))


records = []
for month in range(1, horizon_months + 1):
    records.append(
        {
            "Month": month,
            "Adoption (%)": logistic_adoption(month, market_type, marketing_pct, network_effect),
        }
    )

df = pd.DataFrame(records)
final_adoption = float(df.iloc[-1]["Adoption (%)"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Market", market_type)
col2.metric("Marketing Spend", f"{marketing_pct}%")
col3.metric("Network Effect", f"{network_effect:.2f}")
col4.metric(f"Adoption at Month {horizon_months}", f"{final_adoption:.1f}%")

st.session_state["panel9_export"] = {
    "market_type": market_type,
    "marketing_pct": int(marketing_pct),
    "network_effect": float(network_effect),
    "horizon_months": int(horizon_months),
    "final_adoption_pct": float(final_adoption),
}

st.subheader("S-Curve Adoption Over Time")
fig = px.line(
    df,
    x="Month",
    y="Adoption (%)",
    markers=True,
    title=f"{market_type} Adoption S-Curve",
)
fig.update_layout(xaxis=dict(dtick=1), yaxis=dict(range=[0, 100]))
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.style.format({"Adoption (%)": "{:.1f}%"}), use_container_width=True)

if market_type == "B2C" and network_effect > 0.6 and horizon_months >= 18:
    st.success(
        f"Strong network effects detected: projected {final_adoption:.1f}% adoption "
        f"by month {horizon_months} in B2C."
    )
else:
    st.info(
        "In this model, stronger network effects (>0.6) and higher marketing spend "
        "accelerate adoption fastest in B2C segments."
    )
