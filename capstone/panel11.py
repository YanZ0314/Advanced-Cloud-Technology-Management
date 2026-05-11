import datetime
import random

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Cloud Cost Management", layout="wide")

st.title("Cloud Cost Management Panel")
st.write(
    "Explore AWS cloud spend interactively. Connects to **AWS Cost Explorer** when credentials "
    "are available, or switches automatically to **Demo Mode** with synthetic spend data."
)

# ── AWS credential probe ──────────────────────────────────────────────────────
_AWS_LIVE = False
try:
    import boto3
    boto3.client("sts").get_caller_identity()
    _AWS_LIVE = True
except Exception:
    pass

# ── Demo data ─────────────────────────────────────────────────────────────────
_SERVICE_BASES = {
    "Amazon EC2": 14200, "Amazon S3": 3100, "Amazon RDS": 7800,
    "AWS Lambda": 1200, "Amazon CloudFront": 2400, "Amazon EKS": 9500,
    "Amazon ElastiCache": 4300, "AWS Data Transfer": 1800,
    "Amazon DynamoDB": 2900, "Amazon SageMaker": 6100,
    "Amazon Redshift": 5200, "Amazon Route 53": 420,
    "AWS CloudTrail": 310, "Amazon SNS": 180, "Amazon SQS": 260,
}
_REGION_BASES = {
    "us-east-1": 22000, "us-west-2": 15000, "eu-west-1": 11000,
    "ap-southeast-1": 7500, "eu-central-1": 8200, "ap-northeast-1": 6100,
}
_ACCOUNT_BASES = {
    "Account-111111111111": 42000,
    "Account-222222222222": 31000,
    "Account-333333333333": 18000,
}
_GROUP_BASES = {
    "SERVICE": _SERVICE_BASES,
    "REGION": _REGION_BASES,
    "LINKED_ACCOUNT": _ACCOUNT_BASES,
}


def _demo_data(start: datetime.date, end: datetime.date, granularity: str, group_by: str) -> pd.DataFrame:
    rng = random.Random(42)
    if granularity == "MONTHLY":
        dates = [p.to_timestamp().date() for p in pd.period_range(start=start, end=end, freq="M")]
    else:
        dates = pd.date_range(start=start, end=end, freq="D").date.tolist()
    bases = _GROUP_BASES[group_by]
    daily_scale = 1.0 if granularity == "MONTHLY" else 1.0 / 30.0
    rows = []
    for i, d in enumerate(dates):
        trend = 1.0 + 0.003 * i
        for g, base in bases.items():
            noise = rng.gauss(1.0, 0.10)
            spike = 3.2 if rng.random() < 0.018 else 1.0
            cost = max(0.0, base * trend * noise * spike * daily_scale)
            rows.append({"Date": d, "Group": g, "Cost": round(cost, 2)})
    return pd.DataFrame(rows)


def _aws_data(start: datetime.date, end: datetime.date, granularity: str, metric: str, group_by: str) -> pd.DataFrame:
    import boto3
    client = boto3.client("ce", region_name="us-east-1")
    result = client.get_cost_and_usage(
        TimePeriod={"Start": start.strftime("%Y-%m-%d"), "End": end.strftime("%Y-%m-%d")},
        Granularity=granularity,
        Metrics=[metric],
        GroupBy=[{"Type": "DIMENSION", "Key": group_by}],
    )
    rows = []
    for period in result.get("ResultsByTime", []):
        d = datetime.datetime.strptime(period["TimePeriod"]["Start"], "%Y-%m-%d").date()
        for grp in period.get("Groups", []):
            rows.append({
                "Date": d,
                "Group": grp["Keys"][0],
                "Cost": round(float(grp["Metrics"][metric]["Amount"]), 2),
            })
    return pd.DataFrame(rows) if rows else pd.DataFrame(columns=["Date", "Group", "Cost"])


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Controls")
    st.caption(f"Data source: **{'🟢 AWS Live' if _AWS_LIVE else '🟡 Demo Mode'}**")
    if not _AWS_LIVE:
        st.info("No AWS credentials detected — using synthetic demo data.")

    today = datetime.date.today()
    default_start = today - datetime.timedelta(days=180)
    date_val = st.date_input(
        "Date range",
        value=(default_start, today),
        min_value=today - datetime.timedelta(days=730),
        max_value=today,
    )
    if isinstance(date_val, (list, tuple)) and len(date_val) == 2:
        start_date, end_date = date_val[0], date_val[1]
    else:
        start_date, end_date = default_start, today
    if start_date >= end_date:
        end_date = start_date + datetime.timedelta(days=1)

    granularity = st.selectbox("Granularity", ["MONTHLY", "DAILY"])
    metric = st.selectbox("Cost metric", ["UNBLENDED_COST", "AMORTIZED_COST"])
    group_by = st.selectbox("Group by", ["SERVICE", "REGION", "LINKED_ACCOUNT"])
    top_n = st.slider("Top-N groups", 3, 15, 7)
    savings_pct = st.slider("Cost-reduction policy (%)", 0, 30, 0)

# ── Load data ─────────────────────────────────────────────────────────────────
with st.spinner("Loading cost data…"):
    if _AWS_LIVE:
        df_raw = _aws_data(start_date, end_date, granularity, metric, group_by)
    else:
        df_raw = _demo_data(start_date, end_date, granularity, group_by)

if df_raw.empty:
    st.warning("No cost data for the selected period.")
    st.stop()

# Top-N filter
top_groups = df_raw.groupby("Group")["Cost"].sum().nlargest(top_n).index.tolist()
df = df_raw[df_raw["Group"].isin(top_groups)].copy()
df_time = df.groupby("Date")["Cost"].sum().reset_index().sort_values("Date").reset_index(drop=True)
total_spend = float(df_time["Cost"].sum())

# ── FinOps metrics ────────────────────────────────────────────────────────────
n = len(df_time)
h = max(1, n // 2)
first_half_cost = df_time["Cost"].iloc[:h].sum()
second_half_cost = df_time["Cost"].iloc[h:].sum()
mom_pct = ((second_half_cost - first_half_cost) / first_half_cost * 100) if first_half_cost > 0 else 0.0

all_totals = df_raw.groupby("Group")["Cost"].sum()
total_all = float(all_totals.sum())
top3_spend = float(all_totals.nlargest(3).sum())
concentration_pct = (top3_spend / total_all * 100) if total_all > 0 else 0.0
top3_names = all_totals.nlargest(3).index.tolist()

win = min(7, max(2, n // 4))
rm = df_time["Cost"].rolling(win, min_periods=1).mean()
rs = df_time["Cost"].rolling(win, min_periods=1).std().fillna(0)
df_time["anomaly"] = (df_time["Cost"] > rm + 2 * rs) & (rs > 0)
anomaly_count = int(df_time["anomaly"].sum())
anom_rows = df_time[df_time["anomaly"]]

savings_amount = total_spend * savings_pct / 100.0

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Spend", f"${total_spend:,.0f}")
k2.metric("Period Trend", f"{mom_pct:+.1f}%")
k3.metric("Top-3 Concentration", f"{concentration_pct:.1f}%")
k4.metric("Anomalous Periods", str(anomaly_count))
k5.metric(
    "Projected Savings",
    f"${savings_amount:,.0f}" if savings_pct else "—",
    f"−{savings_pct}% policy" if savings_pct else None,
)

st.divider()

# ── Shared chart layout ───────────────────────────────────────────────────────
_CL = dict(
    template="plotly_dark",
    paper_bgcolor="#1E2330",
    plot_bgcolor="#1E2330",
    font=dict(family="Inter, sans-serif", color="#F0F4FF"),
    title_font=dict(family="Inter, sans-serif", color="#F0F4FF", size=15),
    margin=dict(l=50, r=20, t=45, b=40),
    legend=dict(bgcolor="rgba(30,35,48,0.85)", bordercolor="#2E3549", borderwidth=1),
    xaxis=dict(showgrid=True, gridcolor="#2E3549"),
    yaxis=dict(showgrid=True, gridcolor="#2E3549", tickprefix="$"),
)

# ── Time-series chart ─────────────────────────────────────────────────────────
st.subheader("Cost over time")
dates_str = df_time["Date"].astype(str).tolist()
fig_ts = go.Figure()
fig_ts.add_trace(go.Scatter(
    x=dates_str, y=df_time["Cost"].tolist(),
    name="Actual cost",
    mode="lines+markers",
    line=dict(color="#4F8EF7", width=2),
    marker=dict(size=4),
    fill="tozeroy",
    fillcolor="rgba(79,142,247,0.10)",
))
if savings_pct > 0:
    fig_ts.add_trace(go.Scatter(
        x=dates_str,
        y=(df_time["Cost"] * (1 - savings_pct / 100)).tolist(),
        name=f"After −{savings_pct}% policy",
        mode="lines",
        line=dict(color="#22D3A5", width=2, dash="dash"),
    ))
if not anom_rows.empty:
    fig_ts.add_trace(go.Scatter(
        x=anom_rows["Date"].astype(str).tolist(),
        y=anom_rows["Cost"].tolist(),
        name="Anomaly",
        mode="markers",
        marker=dict(color="#EF4444", size=11, symbol="x"),
    ))
fig_ts.update_layout(title="Total Cloud Spend", **_CL)
st.plotly_chart(fig_ts, use_container_width=True)

# ── Spend breakdown bar ───────────────────────────────────────────────────────
st.subheader(f"Spend by {group_by.replace('_', ' ').title()} — top {top_n}")
df_bar = df.groupby("Group")["Cost"].sum().reset_index().sort_values("Cost", ascending=False)
fig_bar = go.Figure(go.Bar(
    x=df_bar["Group"].tolist(),
    y=df_bar["Cost"].tolist(),
    marker_color="#4F8EF7",
    text=[f"${v:,.0f}" for v in df_bar["Cost"]],
    textposition="outside",
    textfont=dict(color="#F0F4FF"),
))
fig_bar.update_layout(
    title=f"Cumulative spend by {group_by.replace('_', ' ').title()}",
    xaxis_title="",
    **_CL,
)
st.plotly_chart(fig_bar, use_container_width=True)

# ── FinOps Insights ───────────────────────────────────────────────────────────
st.subheader("FinOps Insights")
f1, f2, f3 = st.columns(3)

with f1:
    trend_color = "#EF4444" if mom_pct > 5 else ("#22D3A5" if mom_pct < -2 else "#F59E0B")
    trend_label = "↑ Increasing" if mom_pct > 5 else ("↓ Decreasing" if mom_pct < -2 else "→ Stable")
    st.markdown("**Period-over-period trend**")
    st.markdown(
        f"<p style='font-size:1.6rem;font-weight:700;color:{trend_color};margin:0'>{mom_pct:+.1f}%</p>"
        f"<p style='color:#8B95B0;margin:0'>{trend_label} — first vs second half of period</p>",
        unsafe_allow_html=True,
    )

with f2:
    conc_color = "#EF4444" if concentration_pct > 80 else ("#F59E0B" if concentration_pct > 60 else "#22D3A5")
    st.markdown("**Top-3 concentration**")
    st.markdown(
        f"<p style='font-size:1.6rem;font-weight:700;color:{conc_color};margin:0'>{concentration_pct:.1f}%</p>"
        f"<p style='color:#8B95B0;margin:0'>{', '.join(top3_names)}</p>",
        unsafe_allow_html=True,
    )

with f3:
    anom_color = "#EF4444" if anomaly_count > 3 else ("#F59E0B" if anomaly_count > 0 else "#22D3A5")
    anom_label = "No anomalies detected" if anomaly_count == 0 else f"{anomaly_count} period(s) flagged (2σ threshold)"
    st.markdown("**Anomaly detection**")
    st.markdown(
        f"<p style='font-size:1.6rem;font-weight:700;color:{anom_color};margin:0'>{anomaly_count}</p>"
        f"<p style='color:#8B95B0;margin:0'>{anom_label}</p>",
        unsafe_allow_html=True,
    )

if not anom_rows.empty:
    with st.expander("Anomalous periods detail"):
        disp = anom_rows[["Date", "Cost"]].copy()
        disp["Date"] = disp["Date"].astype(str)
        disp["Cost"] = disp["Cost"].apply(lambda v: f"${v:,.2f}")
        st.dataframe(disp, use_container_width=True)

# ── Full breakdown table ──────────────────────────────────────────────────────
with st.expander("Full cost breakdown table"):
    df_pivot = df.pivot_table(index="Date", columns="Group", values="Cost", aggfunc="sum", fill_value=0.0)
    df_pivot = df_pivot.sort_index()
    df_pivot.index = df_pivot.index.astype(str)
    st.dataframe(df_pivot.style.format("${:,.0f}"), use_container_width=True)

# ── Session export ─────────────────────────────────────────────────────────────
st.session_state["panel11_export"] = {
    "total_spend": total_spend,
    "mom_pct": float(mom_pct),
    "concentration_pct": float(concentration_pct),
    "anomaly_count": anomaly_count,
    "savings_amount": float(savings_amount),
    "group_by": group_by,
}
