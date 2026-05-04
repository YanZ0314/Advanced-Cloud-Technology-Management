import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="AI Degree Advisor — Integrated Simulation", layout="wide")

st.title("Final Simulation Dashboard — AI Degree Advisor")
st.write(
    "**AI Degree Advisor** is a cloud and AI-enabled academic advising platform: optimize pathways, "
    "reduce excess credits, improve progression, and **scale advising without scaling staff**. "
    "In this app, **Panels 1–9 appear inside the named simulation flows** in the sidebar (not as separate items); "
    "run those flows first, then open **Integrated outcomes dashboard** to see cost, uptime, adoption, and outcome "
    "indicators together. Values **auto-seed** from session exports when you have visited the relevant flows "
    "this session."
)

panel1_export = st.session_state.get("panel1_export", {})
panel5_export = st.session_state.get("panel5_export", {})
panel6_export = st.session_state.get("panel6_export", {})
panel8_export = st.session_state.get("panel8_export", {})
panel9_export = st.session_state.get("panel9_export", {})

# ~$500K/year reference → ~$41.7K/month when no Panel 6 export
_default_annual = float(panel1_export.get("baseline_annual_cost", 500000.0))
default_cost = float(
    panel6_export.get(
        "monthly_cost_usd",
        _default_annual / 12.0,
    )
)
default_uptime = float(panel6_export.get("expected_uptime_pct", 99.36))
default_adoption = float(
    panel9_export.get("final_adoption_pct", panel8_export.get("final_adoption_pct", 60.0))
)
_default_months = int(panel9_export.get("horizon_months", 18))
_default_months = max(6, min(36, _default_months))


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


def delivery_quality_multiplier(p5: dict | None) -> float:
    """Stronger Panel 5 automation + lower change failure → slightly higher modeled institutional impact."""
    if not p5:
        return 1.0
    auto = float(p5.get("automation_pct", 50.0))
    fail = float(p5.get("failure_rate", 15.0))
    reliability = max(0.0, (15.0 - fail) / 20.0)
    return float(
        clamp(0.94 + (auto / 100.0) * 0.14 + reliability * 0.10, 0.92, 1.15)
    )


with st.sidebar:
    st.header("Linked inputs")
    monthly_cost_usd = st.slider("Monthly platform cost (USD)", 5000, 80000, int(default_cost), 500)
    uptime_pct = st.slider("Expected uptime (%)", 98.0, 99.99, default_uptime, 0.01)
    base_adoption_pct = st.slider(
        "Base adoption potential (%)",
        10.0,
        95.0,
        default_adoption,
        0.5,
        help="Seeded from Panel 9 student adoption (and Panel 8 org adoption if no Panel 9 run).",
    )
    months = st.slider("Projection horizon (months)", 6, 36, _default_months, 1)


_delivery_m = delivery_quality_multiplier(panel5_export if panel5_export else None)

cost_efficiency_score = clamp(100.0 - (monthly_cost_usd - 5000) / 750.0, 0.0, 100.0)
uptime_factor = clamp(0.65 + ((uptime_pct - 98.0) / 1.99) * 0.45, 0.65, 1.10)
cost_factor = clamp(0.75 + (cost_efficiency_score / 100.0) * 0.35, 0.75, 1.10)
linked_adoption_ceiling = clamp(base_adoption_pct * uptime_factor * cost_factor, 15.0, 99.0)

records = []
curve_speed = 0.22 + ((uptime_pct - 98.0) / 1.99) * 0.12
for month in range(1, months + 1):
    progress = 1 - (2.71828 ** (-curve_speed * month))
    adoption_pct = linked_adoption_ceiling * progress
    records.append({"Month": month, "Linked adoption (%)": adoption_pct})

df = pd.DataFrame(records)
final_adoption = float(df.iloc[-1]["Linked adoption (%)"])

# Proxy institutional outcomes; Panel 5 delivery quality acts as a multiplier (aligned with Panel 9 blend story).
impact_score = (
    (linked_adoption_ceiling / 100.0)
    * (uptime_factor / 1.10)
    * (cost_efficiency_score / 100.0)
    * _delivery_m
)
time_to_degree_reduction_pct = clamp(4.0 + impact_score * 22.0, 0.0, 18.0)
excess_credits_reduction_pct = clamp(6.0 + impact_score * 28.0, 0.0, 28.0)
advisor_workload_reduction_pct = clamp(8.0 + impact_score * 35.0, 0.0, 38.0)

with st.expander("Session exports feeding this run", expanded=False):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Panel 1 (cost / ROI)**")
        if panel1_export:
            st.caption(
                f"Baseline annual **${panel1_export.get('baseline_annual_cost', 0):,.0f}** · "
                f"ROI (horizon) **{panel1_export.get('roi_pct', 0):.1f}%**"
            )
        else:
            st.caption("Not loaded — open **Budget & platform delivery** (includes budget + platform delivery).")
        st.markdown("**Panel 5 (delivery)**")
        if panel5_export:
            st.caption(
                f"Automation **{panel5_export.get('automation_pct', 0):.0f}%** · "
                f"failure **{panel5_export.get('failure_rate', 0):.1f}%** · "
                f"**{panel5_export.get('health_label', '—')}**"
            )
        else:
            st.caption("Not loaded — open a combined view that includes Panel 5.")
        st.markdown("**Panel 6 (uptime / run rate)**")
        if panel6_export:
            st.caption(
                f"Uptime **{panel6_export.get('expected_uptime_pct', 0):.2f}%** · "
                f"~**${panel6_export.get('monthly_cost_usd', 0):,.0f}**/mo"
            )
        else:
            st.caption("Not loaded — open **ROI & resilience design**.")
    with c2:
        st.markdown("**Panel 8 (org adoption)**")
        if panel8_export:
            st.caption(
                f"Advisor adoption ~**{panel8_export.get('final_adoption_pct', 0):.1f}%** "
                f"@{panel8_export.get('simulation_months', '')} mo"
            )
        else:
            st.caption("Optional — **Governance & change adoption**.")
        st.markdown("**Panel 9 (student adoption)**")
        if panel9_export:
            blend = panel9_export.get("panel5_blend_enabled", False)
            st.caption(
                f"{panel9_export.get('market_type', '')} · final **{panel9_export.get('final_adoption_pct', 0):.1f}%** "
                f"· effective network **{panel9_export.get('effective_network_effect', 0):.2f}**"
            )
            st.caption(f"Panel 5 → Panel 9 blend: **{'on' if blend else 'off'}**")
        else:
            st.caption("Not loaded — open **Student adoption & diffusion**.")

st.subheader("Business case targets (reference)")
st.markdown(
    """
| Outcome | Target range (program narrative) |
| --- | --- |
| Time-to-degree | **−10% to −15%** |
| Excess credits | **~−20%** |
| Advisor workload | **−25% to −30%** |
| Annual platform cost (illustrative) | **~$500K** |
| Year-one value vs. cost | **2–4×** when adoption and reliability land |
"""
)

r1, r2, r3, r4, r5 = st.columns(5)
r1.metric("Monthly platform cost", f"${monthly_cost_usd:,.0f}")
r2.metric("Expected uptime", f"{uptime_pct:.2f}%")
r3.metric("Adoption ceiling (linked)", f"{linked_adoption_ceiling:.1f}%")
r4.metric(f"Linked adoption @ month {months}", f"{final_adoption:.1f}%")
r5.metric(
    "Panel 1 ROI (horizon)",
    f"{panel1_export.get('roi_pct', 0):.1f}%" if panel1_export else "—",
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Modeled time-to-degree improvement", f"{time_to_degree_reduction_pct:.1f}%")
m2.metric("Modeled excess-credit reduction", f"{excess_credits_reduction_pct:.1f}%")
m3.metric("Modeled advisor workload reduction", f"{advisor_workload_reduction_pct:.1f}%")
m4.metric(
    "Delivery quality factor",
    f"{_delivery_m:.2f}",
    "Panel 5 loaded" if panel5_export else "No P5 export",
)

st.subheader("Linked adoption curve")
fig = px.line(
    df,
    x="Month",
    y="Linked adoption (%)",
    markers=True,
    title="Integrated adoption trajectory (cost, uptime, and—when loaded—delivery quality from Panel 5)",
)
fig.update_layout(xaxis=dict(dtick=1), yaxis=dict(range=[0, 100]))
st.plotly_chart(fig, use_container_width=True)

st.dataframe(df.style.format({"Linked adoption (%)": "{:.1f}%"}), use_container_width=True)

with st.expander("Managerial insights (conclusion)", expanded=True):
    st.markdown(
        """
- **Use the simulation flows first**: **Budget & platform delivery**, **ROI & resilience design**, **Compliance & AI innovation**, **Governance & change adoption**, and **Student adoption & diffusion** populate exports when those pages run in-session.
- **Panel 5 → Panel 9 blend**: After visiting **Budget & platform delivery**, enable the blend on **Student adoption & diffusion**; stronger automation and lower change failure raise effective launch and network effects. This dashboard applies a **delivery quality factor** from Panel 5 exports.
- **Invest in reliability**: Registration and compliance-sensitive advising requires trustworthy uptime (Panel 6).
- **Unit economics**: ~**$500K/year** aligns with the business case when modeled outcomes approach targets and value realization hits **2–4×** in year one.
"""
    )

st.caption(
    "Link logic: lower monthly run rate improves affordability; higher uptime improves trust; Panel 5 export "
    "raises modeled outcome range when delivery is healthy; student/org adoption seeds from Panel 9 / Panel 8 exports."
)
