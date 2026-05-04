import streamlit as st


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(max_value, value))


st.set_page_config(page_title="AI Degree Advisor — Platform Delivery", layout="wide")

st.title("Implementation Roadmap & DevOps Plan")
st.write(
    "Model delivery performance for the **AI Degree Advisor** platform: automation and team size affect "
    "release cadence and reliability for models, APIs, and integrations that students and advisors rely on."
)

col1, col2 = st.columns(2)
with col1:
    automation_pct = st.slider("Automation (%)", min_value=0, max_value=100, value=70)
with col2:
    team_size = st.slider("Team Size", min_value=2, max_value=25, value=8)


# Baseline assumptions
baseline_frequency = 10.0  # deployments per month
baseline_failure_rate = 15.0  # percent

# Main driver: automation impact
automation_frequency_multiplier = 1 + (automation_pct / 100) * 0.7
automation_failure_multiplier = 1 - (automation_pct / 100) * 0.5

# Team-size effect: small bonus for 5-9 members, slight coordination drag when large
if team_size < 5:
    team_frequency_factor = 0.92
    team_failure_factor = 1.08
elif team_size <= 9:
    team_frequency_factor = 1.05
    team_failure_factor = 0.95
elif team_size <= 15:
    team_frequency_factor = 1.00
    team_failure_factor = 1.00
else:
    team_frequency_factor = 0.90
    team_failure_factor = 1.12

deployment_frequency = baseline_frequency * automation_frequency_multiplier * team_frequency_factor
failure_rate = baseline_failure_rate * automation_failure_multiplier * team_failure_factor
failure_rate = clamp(failure_rate, 1.0, 40.0)

frequency_change_pct = ((deployment_frequency - baseline_frequency) / baseline_frequency) * 100
failure_change_pct = ((failure_rate - baseline_failure_rate) / baseline_failure_rate) * 100

metric_col1, metric_col2 = st.columns(2)
with metric_col1:
    st.metric(
        "Deployment Frequency (per month)",
        f"{deployment_frequency:.1f}",
        f"{frequency_change_pct:+.0f}%",
    )
with metric_col2:
    st.metric(
        "Change Failure Rate",
        f"{failure_rate:.1f}%",
        f"{failure_change_pct:+.0f}%",
        delta_color="inverse",
    )


def health_color(frequency_delta: float, failure_delta: float) -> tuple[str, str]:
    # Positive when deploys go up and failures go down.
    score = frequency_delta - failure_delta
    if score >= 60:
        return "#16a34a", "Excellent"
    if score >= 30:
        return "#22c55e", "Good"
    if score >= 5:
        return "#eab308", "Moderate"
    return "#dc2626", "Needs Attention"


color, label = health_color(frequency_change_pct, failure_change_pct)

# Export key panel outputs for cross-panel scenarios (e.g., Panel 9).
st.session_state["panel5_export"] = {
    "automation_pct": float(automation_pct),
    "team_size": int(team_size),
    "deployment_frequency": float(deployment_frequency),
    "failure_rate": float(failure_rate),
    "frequency_change_pct": float(frequency_change_pct),
    "failure_change_pct": float(failure_change_pct),
    "health_label": label,
}

st.markdown("### Deployment Health")
st.markdown(
    f"""
    <div style="padding: 0.9rem; border-radius: 0.75rem; background-color: {color}22; border: 1px solid {color};">
      <strong style="color: {color}; font-size: 1.1rem;">{label}</strong><br/>
      <span>Automation at <strong>{automation_pct}%</strong> with team size <strong>{team_size}</strong>
      estimates deployment frequency <strong>{frequency_change_pct:+.0f}%</strong> and
      failure rate <strong>{failure_change_pct:+.0f}%</strong> versus baseline.</span>
    </div>
    """,
    unsafe_allow_html=True,
)

if automation_pct > 70:
    st.success(
        "High automation detected: expected about +50% deployment frequency and around -40% failure trend."
    )
else:
    st.info("Increase automation above 70% to unlock the strongest reliability gains.")
