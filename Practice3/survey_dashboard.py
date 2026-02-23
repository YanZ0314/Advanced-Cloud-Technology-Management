"""
Streamlit dashboard: Survey Descriptive Statistics for Harvard Extension ROI Advisor.
"""
import re
from collections import Counter, defaultdict

import streamlit as st
import pandas as pd

SURVEY_PATH = "survey_responses.txt"


def parse_budget(s: str):
    m = re.search(r"\$([0-9,]+)\s*-\s*\$([0-9,]+)", s)
    if not m:
        return None
    lo = int(m.group(1).replace(",", ""))
    hi = int(m.group(2).replace(",", ""))
    return (lo + hi) / 2 / 1000


def parse_time_ordinal(s: str):
    if not s:
        return None
    s = s.strip().lower()
    if "5-10" in s or "part-time" in s or "1 course" in s:
        return 1
    if "10-15" in s or "1-2 courses" in s:
        return 2
    if "15-20" in s or "2 courses" in s:
        return 3
    if "20+" in s or "full-time" in s:
        return 4
    return 0


def parse_timeline_ordinal(s: str):
    if not s:
        return None
    s = s.strip().lower()
    if "1-2 years" in s:
        return 3
    if "2-3 years" in s:
        return 2
    if "3-5" in s or "flexible" in s:
        return 1
    return 0


def load_survey(path: str):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    for line in lines[2:]:
        line = line.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) < 6:
            continue
        rec = {
            "id": parts[0].strip(),
            "time_commitment": parts[1].strip(),
            "budget_raw": parts[2].strip(),
            "career_change": parts[3].strip(),
            "target_timeline": parts[4].strip(),
            "adopter_category": parts[5].strip(),
        }
        rec["budget_mid"] = parse_budget(rec["budget_raw"])
        rec["time_ordinal"] = parse_time_ordinal(rec["time_commitment"])
        rec["timeline_ordinal"] = parse_timeline_ordinal(rec["target_timeline"])
        rows.append(rec)
    return rows


@st.cache_data
def get_survey_data():
    return load_survey(SURVEY_PATH)


def main():
    st.set_page_config(
        page_title="Survey Statistics | Harvard Extension ROI Advisor",
        page_icon="📊",
        layout="wide",
    )
    st.title("📊 Survey Descriptive Statistics")
    st.caption("Harvard Extension School — AI-Enabled Academic Advisor (ROI Focus)")

    rows = get_survey_data()
    n = len(rows)
    if n == 0:
        st.error("No survey data found.")
        return

    # Key metrics
    career_yes = sum(1 for r in rows if r["career_change"] == "Yes")
    short_timeline = sum(1 for r in rows if r["timeline_ordinal"] in (2, 3))
    early_adopters = sum(
        1 for r in rows if r["adopter_category"] in ("Innovator", "Early Adopter")
    )
    budgets = [r["budget_mid"] for r in rows if r["budget_mid"] is not None]
    avg_budget_k = sum(budgets) / len(budgets) if budgets else 0

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Total responses", f"{n:,}")
    col2.metric("Career changers (Yes)", f"{career_yes:,} ({100*career_yes/n:.1f}%)")
    col3.metric("Short/medium timeline (1-3y)", f"{short_timeline:,} ({100*short_timeline/n:.1f}%)")
    col4.metric("Innovators + Early Adopters", f"{early_adopters:,} ({100*early_adopters/n:.1f}%)")
    col5.metric("Avg budget midpoint (per sem)", f"${avg_budget_k:.1f}k")

    st.divider()

    tab_labels = [
        "Time commitment",
        "Budget",
        "Career change",
        "Target timeline",
        "Adopter category",
    ]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        st.subheader("Time commitment")
        time_counts = Counter(r["time_commitment"] for r in rows)
        time_data = [
            {"Time commitment": k, "Count": v, "Percent": f"{100*v/n:.1f}%"}
            for k, v in sorted(time_counts.items(), key=lambda x: -x[1])
        ]
        time_df = pd.DataFrame(time_data)
        col_a, col_b = st.columns([1, 1])
        with col_a:
            st.dataframe(time_df, use_container_width=True, hide_index=True)
        with col_b:
            st.bar_chart(time_df.set_index("Time commitment")["Count"])
        time_groups = defaultdict(int)
        for r in rows:
            o = r["time_ordinal"]
            if o == 1:
                time_groups["5-10 hrs (1 course / part-time)"] += 1
            elif o == 2:
                time_groups["10-15 hrs (1-2 courses)"] += 1
            elif o == 3:
                time_groups["15-20 hrs (2 courses)"] += 1
            elif o == 4:
                time_groups["20+ hrs (full-time)"] += 1
        st.caption("Grouped:")
        group_data = [
            {"Group": k, "Count": v, "Percent": f"{100*v/n:.1f}%"}
            for k, v in sorted(time_groups.items(), key=lambda x: -x[1])
        ]
        group_df = pd.DataFrame(group_data)
        st.dataframe(group_df, use_container_width=True, hide_index=True)

    with tabs[1]:
        st.subheader("Budget (per semester)")
        budget_counts = Counter(r["budget_raw"] for r in rows)
        budget_data = [
            {"Budget": k, "Count": v, "Percent": f"{100*v/n:.1f}%"}
            for k, v in sorted(budget_counts.items(), key=lambda x: -x[1])
        ]
        budget_df = pd.DataFrame(budget_data)
        st.dataframe(budget_df, use_container_width=True, hide_index=True)
        if budgets:
            st.caption(
                f"Budget midpoint (k$): min={min(budgets):.1f}, max={max(budgets):.1f}, mean={sum(budgets)/len(budgets):.1f}"
            )
        st.bar_chart(budget_df.set_index("Budget")["Count"])

    with tabs[2]:
        st.subheader("Career change?")
        career_counts = Counter(r["career_change"] for r in rows)
        career_data = [
            {"Career change": k, "Count": v, "Percent": f"{100*v/n:.1f}%"}
            for k, v in sorted(career_counts.items(), key=lambda x: -x[1])
        ]
        career_df = pd.DataFrame(career_data)
        c1, c2 = st.columns([1, 1])
        with c1:
            st.dataframe(career_df, use_container_width=True, hide_index=True)
        with c2:
            st.bar_chart(career_df.set_index("Career change")["Count"])

    with tabs[3]:
        st.subheader("Target timeline")
        timeline_counts = Counter(r["target_timeline"] for r in rows)
        timeline_data = [
            {"Target timeline": k, "Count": v, "Percent": f"{100*v/n:.1f}%"}
            for k, v in sorted(timeline_counts.items(), key=lambda x: -x[1])
        ]
        timeline_df = pd.DataFrame(timeline_data)
        t1, t2 = st.columns([1, 1])
        with t1:
            st.dataframe(timeline_df, use_container_width=True, hide_index=True)
        with t2:
            st.bar_chart(timeline_df.set_index("Target timeline")["Count"])
        st.caption(
            f"Short/medium (1-3 years): {short_timeline} ({100*short_timeline/n:.1f}%)  |  "
            f"Longer/flexible (3-5+): {n - short_timeline} ({100*(n - short_timeline)/n:.1f}%)"
        )

    with tabs[4]:
        st.subheader("Adopter category")
        order = ["Innovator", "Early Adopter", "Early Majority", "Late Majority"]
        adopter_counts = Counter(r["adopter_category"] for r in rows)
        adopter_data = [
            {
                "Adopter category": cat,
                "Count": adopter_counts.get(cat, 0),
                "Percent": f"{100*adopter_counts.get(cat, 0)/n:.1f}%",
            }
            for cat in order
        ]
        adopter_df = pd.DataFrame(adopter_data)
        a1, a2 = st.columns([1, 1])
        with a1:
            st.dataframe(adopter_df, use_container_width=True, hide_index=True)
        with a2:
            st.bar_chart(adopter_df.set_index("Adopter category")["Count"])
        st.caption(
            f"Innovators + Early Adopters: {early_adopters} ({100*early_adopters/n:.1f}%)"
        )


if __name__ == "__main__":
    main()

