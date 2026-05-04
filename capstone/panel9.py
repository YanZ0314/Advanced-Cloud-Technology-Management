import math

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="AI Degree Advisor — Student Adoption", layout="wide")

st.title("Product Diffusion & Market Strategy")
st.write(
    "Model **student** adoption of AI Degree Advisor (self-service pathways, alerts) using outreach intensity "
    "and **network effects** (peers, cohort norms). **B2C** ≈ direct student engagement; **B2B** ≈ institution-led rollout."
)

with st.sidebar:
    st.header("Scenario Inputs")
    market_type = st.selectbox(
        "Segment",
        options=["B2B (institution-led)", "B2C (student-facing)"],
        index=1,
    )
    marketing_pct = st.slider("Student communication / launch intensity (% of plan)", 0, 100, 55, 1)
    network_effect = st.slider("Network Effect Strength", 0.0, 1.0, 0.6, 0.05)
    horizon_months = st.slider("Time Horizon (months)", 6, 36, 18, 1)

    panel5_export = st.session_state.get("panel5_export")
    can_blend_panel5 = bool(panel5_export)
    use_panel5_blend = st.toggle(
        "Blend Panel 5 delivery into effective inputs",
        value=can_blend_panel5,
        disabled=not can_blend_panel5,
        help="When on, uses Panel 5 automation % and change failure rate to raise effective "
        "launch intensity and trust-driven network effects. Run **Budget & platform delivery** first to populate exports.",
    )


def segment_model_key(segment: str) -> str:
    return "B2C" if "B2C" in segment else "B2B"


def effective_marketing_network(
    mkt: float, net: float, p5: dict | None, blend: bool
) -> tuple[float, float]:
    """Optional blend: higher automation supports stronger rollout; lower failure boosts trust / word-of-mouth."""
    if not blend or not p5:
        return float(mkt), float(net)
    auto = float(p5.get("automation_pct", 0.0))
    fail = float(p5.get("failure_rate", 15.0))
    # Slide marketing upward with automation (platform readiness).
    m_eff = min(100.0, mkt + (auto / 100.0) * 20.0)
    # Reliability vs baseline failure 15%.
    reliability_boost = max(0.0, (15.0 - fail) / 20.0)
    n_eff = min(1.0, net + (auto / 100.0) * 0.14 + reliability_boost * 0.22)
    return m_eff, n_eff


def logistic_adoption(month: int, market: str, mkt_pct: float, net_effect: float) -> float:
    market_scale = 1.08 if market == "B2C" else 0.90
    market_center_shift = -1.2 if market == "B2C" else 1.8

    growth_rate = (0.10 + (mkt_pct / 100.0) * 0.14 + net_effect * 0.24) * market_scale
    midpoint = 10.0 - (mkt_pct / 100.0) * 3.0 - net_effect * 3.8 + market_center_shift

    adoption = 100.0 / (1.0 + math.exp(-growth_rate * (month - midpoint)))
    return max(0.0, min(100.0, adoption))


_model_key = segment_model_key(market_type)

eff_mkt, eff_net = effective_marketing_network(
    float(marketing_pct), float(network_effect), panel5_export, use_panel5_blend
)

records = []
for month in range(1, horizon_months + 1):
    records.append(
        {
            "Month": month,
            "Adoption (%)": logistic_adoption(month, _model_key, eff_mkt, eff_net),
        }
    )

df = pd.DataFrame(records)
final_adoption = float(df.iloc[-1]["Adoption (%)"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("Market", market_type)
if use_panel5_blend and can_blend_panel5 and (eff_mkt != marketing_pct or eff_net != network_effect):
    col2.metric("Launch intensity (effective)", f"{eff_mkt:.0f}%", f"slider {marketing_pct}%")
    col3.metric("Network effect (effective)", f"{eff_net:.2f}", f"slider {network_effect:.2f}")
else:
    col2.metric("Launch intensity", f"{marketing_pct}%")
    col3.metric("Network effect", f"{network_effect:.2f}")
col4.metric(f"Adoption at Month {horizon_months}", f"{final_adoption:.1f}%")

if use_panel5_blend and can_blend_panel5:
    p5 = panel5_export or {}
    st.caption(
        f"Panel 5 blend: automation **{p5.get('automation_pct', 0):.0f}%**, "
        f"change failure **{p5.get('failure_rate', 0):.1f}%**, health **{p5.get('health_label', '—')}**."
    )
elif not can_blend_panel5:
    st.caption('Open **Budget & platform delivery** first to enable **Blend Panel 5 delivery**.')

st.session_state["panel9_export"] = {
    "market_type": market_type,
    "marketing_pct": int(marketing_pct),
    "network_effect": float(network_effect),
    "effective_marketing_pct": float(eff_mkt),
    "effective_network_effect": float(eff_net),
    "panel5_blend_enabled": bool(use_panel5_blend and can_blend_panel5),
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

if _model_key == "B2C" and eff_net > 0.6 and horizon_months >= 18:
    st.success(
        f"Strong network effects detected: projected {final_adoption:.1f}% student adoption "
        f"by month {horizon_months} (student-facing segment)."
    )
else:
    st.info(
        "In this model, stronger network effects (>0.6) and higher launch intensity "
        "accelerate adoption fastest in student-facing (B2C-style) rollouts."
    )
