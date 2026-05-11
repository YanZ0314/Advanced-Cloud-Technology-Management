import pandas as pd
import streamlit as st
import altair as alt


st.set_page_config(page_title="5-Year Financial Plan", layout="wide")

st.title("ROI & Value Analysis")
st.write(
    "Define tangible and intangible returns for **AI Degree Advisor** (retention, excess credits avoided, "
    "advisor time saved), apply assumptions, and visualize ROI progression over time."
)


st.header("1) Returns Table: Tangible and Intangible")

default_returns = pd.DataFrame(
    [
        {
            "Type": "Tangible",
            "Return Item": "Operational cost savings",
            "Description": "Reduced infrastructure and maintenance costs",
            "Estimated Annual Value (USD)": 120000,
        },
        {
            "Type": "Tangible",
            "Return Item": "Revenue uplift",
            "Description": "Improved conversion and upsell opportunities",
            "Estimated Annual Value (USD)": 90000,
        },
        {
            "Type": "Intangible",
            "Return Item": "Brand trust",
            "Description": "Improved reputation and customer confidence",
            "Estimated Annual Value (USD)": 50000,
        },
        {
            "Type": "Intangible",
            "Return Item": "Agility",
            "Description": "Faster product delivery and decision cycles",
            "Estimated Annual Value (USD)": 45000,
        },
    ]
)

returns_df = st.data_editor(
    default_returns,
    num_rows="dynamic",
    use_container_width=True,
    key="returns_editor",
)

total_tangible = (
    returns_df.loc[returns_df["Type"].str.lower() == "tangible", "Estimated Annual Value (USD)"]
    .fillna(0)
    .sum()
)
total_intangible = (
    returns_df.loc[returns_df["Type"].str.lower() == "intangible", "Estimated Annual Value (USD)"]
    .fillna(0)
    .sum()
)

col1, col2, col3 = st.columns(3)
col1.metric("Total Tangible (Annual USD)", f"${total_tangible:,.0f}")
col2.metric("Total Intangible (Annual USD)", f"${total_intangible:,.0f}")
col3.metric("Total Combined (Annual USD)", f"${(total_tangible + total_intangible):,.0f}")


st.header("2) Assumptions for 5-Year Plan")
st.caption("Example target included: ROI 42% in 3 years, plus brand trust and agility gains.")

left, right = st.columns(2)

with left:
    initial_investment = st.number_input(
        "Initial investment (USD, Year 1)",
        min_value=0.0,
        value=500000.0,
        step=10000.0,
        help="Matches Panel 1 Year 1 total: ~$420K OpEx + $80K CapEx.",
    )
    annual_operating_cost = st.number_input(
        "Annual operating cost (USD)",
        min_value=0.0,
        value=420000.0,
        step=5000.0,
        help="Matches Panel 1 Year 1 OpEx baseline (~$35K/mo).",
    )
    annual_benefit_growth = st.slider(
        "Annual growth of benefits (%)",
        min_value=0.0,
        max_value=50.0,
        value=8.0,
        step=0.5,
    )

with right:
    roi_target_year = st.selectbox("Target ROI year", options=[1, 2, 3, 4, 5], index=2)
    roi_target_value = st.number_input(
        "Target ROI (%)",
        min_value=-100.0,
        max_value=500.0,
        value=15.0,
        step=1.0,
    )
    include_intangible_in_roi = st.checkbox(
        "Include intangible returns in ROI calculation",
        value=True,
    )


st.header("5-Year Financial Plan")

years = list(range(1, 6))

base_tangible = float(total_tangible)
base_intangible = float(total_intangible)

records = []
cumulative_net = -initial_investment

for year in years:
    growth_factor = (1 + annual_benefit_growth / 100) ** (year - 1)
    tangible_benefit = base_tangible * growth_factor
    intangible_benefit = base_intangible * growth_factor
    benefits_for_roi = tangible_benefit + (intangible_benefit if include_intangible_in_roi else 0)

    annual_net_cashflow = benefits_for_roi - annual_operating_cost
    cumulative_net += annual_net_cashflow
    roi_percent = (cumulative_net / initial_investment) * 100 if initial_investment else 0

    records.append(
        {
            "Year": year,
            "Tangible Benefit (USD)": tangible_benefit,
            "Intangible Benefit (USD)": intangible_benefit,
            "Operating Cost (USD)": annual_operating_cost,
            "Net Cash Flow (USD)": annual_net_cashflow,
            "Cumulative Net (USD)": cumulative_net,
            "ROI %": roi_percent,
        }
    )

plan_df = pd.DataFrame(records)
st.dataframe(
    plan_df.style.format(
        {
            "Tangible Benefit (USD)": "${:,.0f}",
            "Intangible Benefit (USD)": "${:,.0f}",
            "Operating Cost (USD)": "${:,.0f}",
            "Net Cash Flow (USD)": "${:,.0f}",
            "Cumulative Net (USD)": "${:,.0f}",
            "ROI %": "{:.1f}%",
        }
    ),
    use_container_width=True,
)


st.header("3) ROI Chart (x = ROI %, y = Year)")

chart = (
    alt.Chart(plan_df)
    .mark_line(point=True)
    .encode(
        x=alt.X("ROI %:Q", title="ROI (%)"),
        y=alt.Y("Year:O", title="Year"),
        tooltip=["Year", alt.Tooltip("ROI %:Q", format=".2f")],
    )
    .properties(height=350)
)
st.altair_chart(chart, use_container_width=True)

target_row = plan_df.loc[plan_df["Year"] == roi_target_year, "ROI %"]
actual_target_roi = float(target_row.iloc[0]) if not target_row.empty else 0.0

if actual_target_roi >= roi_target_value:
    st.success(
        f"Target met: ROI at Year {roi_target_year} is {actual_target_roi:.1f}% "
        f"(target: {roi_target_value:.1f}%)."
    )
else:
    st.warning(
        f"Target not met yet: ROI at Year {roi_target_year} is {actual_target_roi:.1f}% "
        f"(target: {roi_target_value:.1f}%)."
    )
