"""
Cloud Strategy Simulation - Streamlit Web App
Revenue growth simulation, AI investments analysis, and multi-tenant user management.
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from growth_model import (
    calculate_growth_rates,
    revenue_from_growth,
    cash_flow_table,
)
from auth_utils import (
    register_user,
    verify_user,
    list_users,
    delete_user,
    add_admin,
    is_admin,
    ADMIN_EMAIL,
)

# Page config
st.set_page_config(
    page_title="Cloud Strategy Simulation",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = None
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


def render_login():
    """Login/Signup form in sidebar."""
    with st.sidebar:
        st.header("Account")
        if st.session_state.authenticated:
            st.success(f"Logged in as {st.session_state.user_email}")
            if st.session_state.is_admin:
                st.info("Admin")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.is_admin = False
                st.rerun()
            return True
        
        tab1, tab2 = st.tabs(["Login", "Sign Up"])
        with tab1:
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login"):
                ok, admin = verify_user(email, password)
                if ok:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.session_state.is_admin = admin
                    st.rerun()
                else:
                    st.error("Invalid credentials")
        with tab2:
            new_email = st.text_input("Email", key="signup_email")
            new_pw = st.text_input("Password", type="password", key="signup_pw")
            if st.button("Create Account"):
                ok, msg = register_user(new_email, new_pw)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)
        return False


def _regression_line(x: list, y: list, x_smooth: list = None):
    """Fit y = slope*x + intercept; return y values at x_smooth (or x) for the trend line."""
    x_arr = np.asarray(x, dtype=float)
    y_arr = np.asarray(y, dtype=float)
    if len(x_arr) < 2:
        return list(y_arr)
    slope, intercept = np.polyfit(x_arr, y_arr, 1)
    x_out = np.asarray(x_smooth if x_smooth is not None else x)
    return (slope * x_out + intercept).tolist()


def revenue_simulation_tab():
    """Revenue growth simulation with all controls and charts."""
    st.header("Revenue Growth Rate Simulation")
    st.caption("Adjust variables to simulate 5-year growth. Based on Porter's Five Forces and business factors.")
    
    # Sidebar: Variable sliders
    with st.sidebar:
        if st.session_state.authenticated:
            st.divider()
            st.subheader("Simulation Parameters")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        initial_growth = st.slider(
            "Initial Growth Rate (%)",
            -99.0, 99.0, 20.0, 0.1,
            help="Base growth rate before variable effects",
        )
    with c2:
        initial_revenue = st.number_input(
            "Initial Revenue ($)",
            min_value=0,
            value=1_000_000,
            step=100_000,
            format="%d",
        )
        initial_capital = st.number_input(
            "Initial Capital ($)",
            min_value=0,
            value=500_000,
            step=50_000,
            format="%d",
        )
        initial_expense = st.number_input(
            "Initial Expense ($)",
            min_value=0,
            value=1_000_000,
            step=100_000,
            format="%d",
        )
    
    st.subheader("Porter's Five Forces & Business Factors")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        competition = st.slider("Competition", 0.0, 1.0, 0.1, 0.01, help="+0.1 → growth -1%")
        new_entrant = st.slider("New Entrant", 0.0, 1.0, 0.0, 0.01, help="+0.1 → growth -1%")
        supplier_power = st.slider("Supplier's Bargaining Power", 0.0, 1.0, 0.1, 0.01, help="+0.1 → growth +1%")
    
    with col2:
        buyer_power = st.slider("Buyer's Bargaining Power", 0.0, 1.0, 0.1, 0.01, help="+0.1 → growth -1%")
        substitute = st.slider("Substitute", 0.0, 1.0, 0.0, 0.01, help="+0.1 → growth -10%")
        product_market_fit = st.slider("Product-Market Fit", 0.0, 1.0, 0.7, 0.01, help="+0.1 → growth +0.5%")
    
    with col3:
        differentiator = st.slider("Differentiator", 0.0, 1.0, 0.5, 0.01, help="+0.1 → growth +0.5%")
    
    st.subheader("Variable Weights (0.0 to 1.0)")
    w_cols = st.columns(7)
    weight_names = [
        "competition", "new_entrant", "supplier", "buyer",
        "substitute", "product_market_fit", "differentiator"
    ]
    weights = {}
    for i, name in enumerate(weight_names):
        with w_cols[i % 7]:
            weights[name] = st.slider(name.replace("_", " ").title(), 0.0, 1.0, 1.0, 0.01)
    
    st.subheader("Leadership & Process")
    l_cols = st.columns(3)
    with l_cols[0]:
        adaptive_learning = st.slider("Adaptive Learning", 0.0, 1.0, 0.5, 0.01, help="+0.1 → differentiator +0.1")
    with l_cols[1]:
        deep_learning = st.slider("Deep Learning", 0.0, 1.0, 0.5, 0.01, help="+0.1 → differentiator +0.2, substitute -0.1")
    with l_cols[2]:
        process_mgmt = st.slider("Process Management", 0.0, 1.0, 0.5, 0.01, help="+0.1 → buyer power +0.1")
    
    # Calculate growth rates
    growth_rates = calculate_growth_rates(
        initial_growth_rate=initial_growth,
        competition=competition,
        new_entrant=new_entrant,
        supplier_power=supplier_power,
        buyer_power=buyer_power,
        substitute=substitute,
        product_market_fit=product_market_fit,
        differentiator=differentiator,
        adaptive_learning=adaptive_learning,
        deep_learning=deep_learning,
        process_mgmt=process_mgmt,
        weights=weights,
        years=5,
    )
    
    revenues = revenue_from_growth(initial_revenue, growth_rates)
    
    # Charts
    st.subheader("Charts")
    
    # 1. Linear chart: X = growth rate (%), Y = Year
    fig_growth = go.Figure()
    years_1_5 = list(range(1, 6))
    fig_growth.add_trace(
        go.Scatter(
            x=growth_rates,
            y=years_1_5,
            mode="lines+markers",
            name="Growth Rate (%)",
            line=dict(color="#1f77b4", width=3),
        )
    )
    reg_y = _regression_line(growth_rates, years_1_5)
    fig_growth.add_trace(
        go.Scatter(
            x=growth_rates,
            y=reg_y,
            mode="lines",
            name="Regression",
            line=dict(color="#1f77b4", width=1.5, dash="dash"),
        )
    )
    fig_growth.update_layout(
        title="Growth Rate (%) by Year",
        xaxis_title="Growth Rate (%)",
        yaxis_title="Year",
        yaxis=dict(tickvals=[1, 2, 3, 4, 5]),
        template="plotly_white",
        height=400,
    )
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # 2. Radar chart
    radar_cats = ["Competition", "New Entrant", "Supplier", "Buyer", "Substitute", "PMF", "Differentiator"]
    radar_vals = [
        competition, new_entrant, supplier_power, buyer_power,
        substitute, product_market_fit, differentiator,
    ]
    fig_radar = go.Figure()
    fig_radar.add_trace(
        go.Scatterpolar(
            r=radar_vals + [radar_vals[0]],
            theta=radar_cats + [radar_cats[0]],
            fill="toself",
            name="Current Values",
        )
    )
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        title="Radar Chart - Variable Levels",
        showlegend=False,
        height=400,
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 3. Revenue chart: X = revenue ($), Y = Year
    years_1_5 = list(range(1, 6))
    fig_rev = go.Figure()
    fig_rev.add_trace(
        go.Scatter(
            x=revenues,
            y=years_1_5,
            mode="lines+markers",
            name="Revenue ($)",
            line=dict(color="#2ca02c", width=3),
        )
    )
    reg_y_rev = _regression_line(revenues, years_1_5)
    fig_rev.add_trace(
        go.Scatter(
            x=revenues,
            y=reg_y_rev,
            mode="lines",
            name="Regression",
            line=dict(color="#2ca02c", width=1.5, dash="dash"),
        )
    )
    fig_rev.update_layout(
        title="Revenue ($) by Year",
        xaxis_title="Revenue ($)",
        yaxis_title="Year",
        yaxis=dict(tickvals=[1, 2, 3, 4, 5]),
        template="plotly_white",
        height=400,
    )
    st.plotly_chart(fig_rev, use_container_width=True)
    
    # Sensitivity analysis
    st.subheader("Sensitivity Analysis")
    sens_baseline = st.slider("Baseline (%)", 80, 120, 100, 1)
    best = 120
    worst = 80
    st.caption(f"Best case: {best}% | Baseline: {sens_baseline}% | Worst case: {worst}%")
    
    sens_rates = {
        "Best (120%)": [r * 1.2 for r in growth_rates],
        "Baseline (100%)": growth_rates,
        "Worst (80%)": [r * 0.8 for r in growth_rates],
    }
    
    sens_years = list(range(1, 6))
    fig_sens = go.Figure()
    sens_colors = ["#1f77b4", "#2ca02c", "#d62728"]
    for (label, rates), color in zip(sens_rates.items(), sens_colors):
        fig_sens.add_trace(
            go.Scatter(
                x=sens_years,
                y=rates,
                mode="lines+markers",
                name=label,
                line=dict(color=color),
            )
        )
        reg_rates = _regression_line(sens_years, rates)
        fig_sens.add_trace(
            go.Scatter(
                x=sens_years,
                y=reg_rates,
                mode="lines",
                name=f"{label} (regression)",
                line=dict(color=color, width=1.5, dash="dash"),
            )
        )
    fig_sens.update_layout(
        title="Sensitivity - Growth Rate Variance from Baseline",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template="plotly_white",
        height=400,
    )
    st.plotly_chart(fig_sens, use_container_width=True)
    
    # Sensitivity revenue table
    sens_revenues = {
        "Scenario": ["Best (120%)", "Baseline (100%)", "Worst (80%)"],
        "Year 1": [],
        "Year 2": [],
        "Year 3": [],
        "Year 4": [],
        "Year 5": [],
    }
    for mul, scenario in [(1.2, "Best (120%)"), (1.0, "Baseline (100%)"), (0.8, "Worst (80%)")]:
        adj_rates = [r * mul for r in growth_rates]
        revs = revenue_from_growth(initial_revenue, adj_rates)
        for i, r in enumerate(revs):
            sens_revenues[f"Year {i+1}"].append(f"${r:,.0f}")
    # Build table properly
    sens_df = pd.DataFrame({
        "Scenario": sens_revenues["Scenario"],
        "Year 1": sens_revenues["Year 1"],
        "Year 2": sens_revenues["Year 2"],
        "Year 3": sens_revenues["Year 3"],
        "Year 4": sens_revenues["Year 4"],
        "Year 5": sens_revenues["Year 5"],
    })
    st.dataframe(sens_df, use_container_width=True, hide_index=True)
    
    # Cash flow table
    st.subheader("5-Year Cash Flow Table")
    cf_rows = cash_flow_table(initial_capital, initial_expense, revenues, growth_rates)
    cf_df = pd.DataFrame(cf_rows)
    for col in ["Capital", "Revenue", "Expense", "Net Profit", "Cumulative Cash"]:
        cf_df[col] = cf_df[col].apply(lambda x: f"${x:,.0f}")
    st.dataframe(cf_df, use_container_width=True, hide_index=True)


def ai_investments_tab():
    """AI Investments vs US New Business Apps visualization."""
    st.header("AI Investments & US New Business Apps")
    st.caption("Growth rates and gap analysis from 2015-2023, with 2024-2025 predictions.")
    
    # Default data
    years_base = list(range(2015, 2024))
    ai_default = [24, 33, 53, 79, 95, 146, 276, 189, 252]
    biz_default = [2.8, 2.9, 3.2, 3.5, 3.5, 4.3, 5.4, 5.0, 5.4]
    
    with st.expander("Adjust Data (2015-2023)", expanded=False):
        c1, c2 = st.columns(2)
        with c1:
            st.write("**AI Investments ($ Billions)**")
            ai_vals = []
            for y, v in zip(years_base, ai_default):
                ai_vals.append(st.slider(f"{y}", 0, 500, int(v), 1, key=f"ai_{y}"))
        with c2:
            st.write("**US New Business Apps (Millions)**")
            biz_vals = []
            for y, v in zip(years_base, biz_default):
                biz_vals.append(st.slider(f"{y}", 0.0, 10.0, float(v), 0.1, key=f"biz_{y}"))
    
    # Compute growth rates
    def growth_rates(vals):
        out = [0]
        for i in range(1, len(vals)):
            if vals[i-1] > 0:
                out.append((vals[i] - vals[i-1]) / vals[i-1] * 100)
            else:
                out.append(0)
        return out
    
    ai_growth = growth_rates(ai_vals)
    biz_growth = growth_rates(biz_vals)
    
    # Predict 2024, 2025 (simple avg of last 3 years growth)
    avg_ai = sum(ai_growth[-3:]) / 3
    avg_biz = sum(biz_growth[-3:]) / 3
    ai_2024 = ai_vals[-1] * (1 + avg_ai / 100)
    ai_2025 = ai_2024 * (1 + avg_ai / 100)
    biz_2024 = biz_vals[-1] * (1 + avg_biz / 100)
    biz_2025 = biz_2024 * (1 + avg_biz / 100)
    
    pred_ai_growth = [(ai_2024 - ai_vals[-1]) / ai_vals[-1] * 100, (ai_2025 - ai_2024) / ai_2024 * 100]
    pred_biz_growth = [(biz_2024 - biz_vals[-1]) / biz_vals[-1] * 100, (biz_2025 - biz_2024) / biz_2024 * 100]
    
    all_years = years_base + [2024, 2025]
    ai_growth_all = ai_growth + pred_ai_growth
    biz_growth_all = biz_growth + pred_biz_growth
    
    # Gap analysis
    gap = [a - b for a, b in zip(ai_growth_all, biz_growth_all)]
    
    # Linear chart: Y = growth rates, X = Years (with regression lines)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=ai_growth_all,
            mode="lines+markers",
            name="AI Investments Growth (%)",
            line=dict(color="#1f77b4", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=_regression_line(all_years, ai_growth_all),
            mode="lines",
            name="AI (regression)",
            line=dict(color="#1f77b4", width=1.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=biz_growth_all,
            mode="lines+markers",
            name="US Business Apps Growth (%)",
            line=dict(color="#ff7f0e", width=2),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=_regression_line(all_years, biz_growth_all),
            mode="lines",
            name="Business Apps (regression)",
            line=dict(color="#ff7f0e", width=1.5, dash="dash"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=gap,
            mode="lines+markers",
            name="Gap (AI - Business)",
            line=dict(color="#2ca02c", width=2, dash="dot"),
        )
    )
    fig.add_trace(
        go.Scatter(
            x=all_years,
            y=_regression_line(all_years, gap),
            mode="lines",
            name="Gap (regression)",
            line=dict(color="#2ca02c", width=1.5, dash="dash"),
        )
    )
    fig.update_layout(
        title="Growth Rates (%) by Year",
        xaxis_title="Year",
        yaxis_title="Growth Rate (%)",
        template="plotly_white",
        height=450,
        legend=dict(orientation="h"),
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Gap table
    st.subheader("Gap Analysis (AI - Business Apps Growth %)")
    gap_df = pd.DataFrame({
        "Year": all_years,
        "AI Growth (%)": [round(g, 1) for g in ai_growth_all],
        "Business Apps Growth (%)": [round(g, 1) for g in biz_growth_all],
        "Gap (%)": [round(g, 1) for g in gap],
    })
    st.dataframe(gap_df, use_container_width=True, hide_index=True)


def admin_tab():
    """Admin user management."""
    if not st.session_state.is_admin:
        st.warning("Admin access required.")
        return
    
    st.header("User Management Console")
    users = list_users()
    
    for u in users:
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.write(f"**{u['email']}**" + (" (Admin)" if u["is_admin"] else ""))
            with col2:
                if not u["is_admin"] and u["email"] != st.session_state.user_email:
                    if st.button("Delete", key=f"del_{u['email']}"):
                        ok, msg = delete_user(u["email"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            with col3:
                if not u["is_admin"]:
                    if st.button("Make Admin", key=f"admin_{u['email']}"):
                        ok, msg = add_admin(u["email"])
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
            st.divider()
    
    st.subheader("Add Admin")
    new_admin = st.text_input("User email to promote")
    if st.button("Promote to Admin"):
        if new_admin:
            ok, msg = add_admin(new_admin)
            if ok:
                st.success(msg)
            else:
                st.error(msg)
        else:
            st.error("Enter email")


def main():
    render_login()
    
    st.title("Cloud Strategy Simulation")
    st.markdown("Revenue growth simulation, cash flow analysis, and AI investment trends.")
    
    tabs = st.tabs([
        "Revenue Growth Simulation",
        "AI Investments & Business Apps",
        "Admin Console",
    ])
    
    with tabs[0]:
        revenue_simulation_tab()
    
    with tabs[1]:
        ai_investments_tab()
    
    with tabs[2]:
        admin_tab()


if __name__ == "__main__":
    main()
