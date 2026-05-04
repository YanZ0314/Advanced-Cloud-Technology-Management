from pathlib import Path
import runpy

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

# Sidebar display names (avoid "Combined View / Panel N" in the UI).
NAV_BUDGET_PLATFORM = "Budget & platform delivery"
NAV_ROI_RESILIENCE = "ROI & resilience design"
NAV_COMPLIANCE_AI = "Compliance & AI innovation"
NAV_GOVERNANCE_CHANGE = "Governance & change adoption"
NAV_STUDENT_DIFFUSION = "Student adoption & diffusion"
NAV_OUTCOMES_DASHBOARD = "Integrated outcomes dashboard"

PANEL_FILES = {
    "Panel 1 - Budget Planning & Cost Estimation": BASE_DIR / "panel1.py",
    "Panel 2 - ROI & Value Analysis": BASE_DIR / "panel2.py",
    "Panel 3 - Governance & Compliance": BASE_DIR / "panel3.py",
    "Panel 4 - Governance Model Refinement": BASE_DIR / "panel4.py",
    "Panel 5 - Implementation Roadmap & DevOps Plan": BASE_DIR / "panel5.py",
    "Panel 6 - Performance & Resilience Design": BASE_DIR / "panel6.py",
    "Panel 7 - Innovation & AI Integration": BASE_DIR / "panel7.py",
    "Panel 8 - Org Change & Adoption": BASE_DIR / "panel8.py",
    "Panel 9 - Product Diffusion & Market Strategy": BASE_DIR / "panel9.py",
    "Panel 10 - Final Simulation Dashboard": BASE_DIR / "panel10.py",
}

COMBINED_VIEWS = {
    NAV_BUDGET_PLATFORM: [
        "Panel 1 - Budget Planning & Cost Estimation",
        "Panel 5 - Implementation Roadmap & DevOps Plan",
    ],
    NAV_ROI_RESILIENCE: [
        "Panel 2 - ROI & Value Analysis",
        "Panel 6 - Performance & Resilience Design",
    ],
    NAV_COMPLIANCE_AI: [
        "Panel 3 - Governance & Compliance",
        "Panel 7 - Innovation & AI Integration",
    ],
    NAV_GOVERNANCE_CHANGE: [
        "Panel 4 - Governance Model Refinement",
        "Panel 8 - Org Change & Adoption",
    ],
    # Platform delivery (Panel 5) sits under Budget & platform delivery; this page is student diffusion only.
    NAV_STUDENT_DIFFUSION: [
        "Panel 9 - Product Diffusion & Market Strategy",
    ],
}

PORTFOLIO_VIEWS = {
    NAV_BUDGET_PLATFORM,
    NAV_ROI_RESILIENCE,
    NAV_COMPLIANCE_AI,
    NAV_GOVERNANCE_CHANGE,
}


def run_panel_script(panel_path: Path) -> None:
    original_set_page_config = st.set_page_config

    def safe_set_page_config(*args, **kwargs):
        try:
            original_set_page_config(*args, **kwargs)
        except Exception:
            # Ignore duplicate page-config calls in combined views.
            pass

    st.set_page_config = safe_set_page_config
    try:
        runpy.run_path(str(panel_path), run_name="__main__")
    finally:
        st.set_page_config = original_set_page_config


def render_combined_view(view_name: str) -> None:
    panel_labels = COMBINED_VIEWS[view_name]
    panel_paths = [PANEL_FILES[label] for label in panel_labels]

    if any(not path.exists() for path in panel_paths):
        st.error("One or more panel files are missing for the combined view.")
        st.stop()

    # Single-page entry (e.g. student diffusion only; Panel 5 is under Budget & platform delivery).
    if len(panel_paths) == 1:
        st.markdown(f"## {view_name}")
        if view_name == NAV_STUDENT_DIFFUSION:
            st.info(
                "**Platform delivery (Panel 5)** is under **Budget & platform delivery**. "
            )
        st.markdown(f"### {panel_labels[0]}")
        run_panel_script(panel_paths[0])
        return

    if view_name in PORTFOLIO_VIEWS:
        st.markdown(f"## {view_name}")
        for idx, (panel_label, panel_path) in enumerate(zip(panel_labels, panel_paths), start=1):
            st.markdown(f"### Section {idx}: {panel_label}")
            run_panel_script(panel_path)
            if idx < len(panel_paths):
                st.divider()
    else:
        tabs = st.tabs(panel_labels)
        for tab, panel_path in zip(tabs, panel_paths):
            with tab:
                run_panel_script(panel_path)


PANEL_10_INTERNAL = "Panel 10 - Final Simulation Dashboard"
# Sidebar: simulation flows + integrated dashboard (individual panels 1–9 are inside those flows).
nav_options = list(COMBINED_VIEWS.keys()) + [NAV_OUTCOMES_DASHBOARD]

st.sidebar.title("AI Degree Advisor Simulator")
selected_panel = st.sidebar.radio("Navigate", nav_options)

if selected_panel in COMBINED_VIEWS:
    render_combined_view(selected_panel)
elif selected_panel == NAV_OUTCOMES_DASHBOARD:
    panel_path = PANEL_FILES[PANEL_10_INTERNAL]
    if not panel_path.exists():
        st.error(f"Missing panel file: {panel_path.name}")
        st.stop()
    run_panel_script(panel_path)
else:
    st.error("Unknown navigation selection.")
    st.stop()
