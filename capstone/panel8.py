import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Org Change & Adoption", layout="wide")

st.title("Org Change & Adoption")
st.write(
    "Simulate monthly adoption progress based on training hours and leadership engagement."
)

with st.sidebar:
    st.header("Inputs")
    training_hours = st.slider("Training Hours (per employee)", 0, 40, 20, 1)
    leadership_engagement = st.slider("Leadership Engagement (%)", 0, 100, 60, 1)
    simulation_months = st.slider("Simulation Months", 3, 12, 6, 1)


def adoption_and_resistance(
    month: int, total_months: int, train_hours: int, leader_pct: int
) -> tuple[float, float]:
    # Stronger training and leadership increase reachable adoption.
    # At ~30h training + >70% leadership, adoption reaches ~80% near month 6.
    max_adoption = min(95.0, 35.0 + train_hours * 0.9 + leader_pct * 0.25)
    growth_rate = 0.10 + (train_hours / 40.0) * 0.22 + (leader_pct / 100.0) * 0.28
    month_ratio = month / max(total_months, 1)
    adoption = max_adoption * (1 - (2.71828 ** (-growth_rate * month_ratio * 6.0)))
    adoption = min(adoption, max_adoption)
    resistance = max(5.0, 100.0 - adoption - (leader_pct * 0.08))
    return adoption, resistance


records = []
for month in range(1, simulation_months + 1):
    adoption_pct, resistance_idx = adoption_and_resistance(
        month, simulation_months, training_hours, leadership_engagement
    )
    records.append(
        {
            "Month": month,
            "Adoption Rate (%)": adoption_pct,
            "Resistance Index": resistance_idx,
        }
    )

df = pd.DataFrame(records)
final_adoption = float(df.iloc[-1]["Adoption Rate (%)"])
final_resistance = float(df.iloc[-1]["Resistance Index"])

col1, col2, col3 = st.columns(3)
col1.metric("Training", f"{training_hours} h")
col2.metric("Leadership Engagement", f"{leadership_engagement}%")
col3.metric("Adoption by Month " + str(simulation_months), f"{final_adoption:.1f}%")

st.session_state["panel8_export"] = {
    "training_hours": int(training_hours),
    "leadership_engagement_pct": int(leadership_engagement),
    "simulation_months": int(simulation_months),
    "final_adoption_pct": float(final_adoption),
    "final_resistance_index": float(final_resistance),
}

chart_df = df.melt(
    id_vars="Month",
    value_vars=["Adoption Rate (%)", "Resistance Index"],
    var_name="Series",
    value_name="Value",
)

st.subheader("Adoption Over Time with Resistance Index")
fig = px.line(
    chart_df,
    x="Month",
    y="Value",
    color="Series",
    markers=True,
    title="Employee Adoption vs Resistance Trend",
)
fig.update_layout(yaxis_title="Percent / Index", xaxis=dict(dtick=1))
st.plotly_chart(fig, use_container_width=True)

st.dataframe(
    df.style.format({"Adoption Rate (%)": "{:.1f}%", "Resistance Index": "{:.1f}"}),
    use_container_width=True,
)

if training_hours >= 30 and leadership_engagement > 70 and simulation_months >= 6:
    st.success(
        f"High enablement scenario detected: adoption reaches {final_adoption:.1f}% "
        f"by month {simulation_months}, with resistance reduced to {final_resistance:.1f}."
    )
else:
    st.info(
        "Increase training toward 30h and leadership above 70% to approach "
        "80%+ adoption by month 6."
    )
