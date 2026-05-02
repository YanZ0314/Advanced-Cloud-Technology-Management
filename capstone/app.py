from pathlib import Path
import runpy

import streamlit as st


BASE_DIR = Path(__file__).resolve().parent

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
    "Combined View - Panel 1 + Panel 5": [
        "Panel 1 - Budget Planning & Cost Estimation",
        "Panel 5 - Implementation Roadmap & DevOps Plan",
    ],
    "Combined View - Panel 2 + Panel 6": [
        "Panel 2 - ROI & Value Analysis",
        "Panel 6 - Performance & Resilience Design",
    ],
    "Combined View - Panel 3 + Panel 7": [
        "Panel 3 - Governance & Compliance",
        "Panel 7 - Innovation & AI Integration",
    ],
    "Combined View - Panel 4 + Panel 8": [
        "Panel 4 - Governance Model Refinement",
        "Panel 8 - Org Change & Adoption",
    ],
    "Combined View - Panel 5 + Panel 9": [
        "Panel 5 - Implementation Roadmap & DevOps Plan",
        "Panel 9 - Product Diffusion & Market Strategy",
    ],
}

PORTFOLIO_VIEWS = {
    "Combined View - Panel 1 + Panel 5",
    "Combined View - Panel 2 + Panel 6",
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


nav_options = list(PANEL_FILES.keys()) + list(COMBINED_VIEWS.keys())

st.sidebar.title("Cloud Capstone App")
selected_panel = st.sidebar.radio("Navigate Panels", nav_options)

if selected_panel in COMBINED_VIEWS:
    render_combined_view(selected_panel)
else:
    panel_path = PANEL_FILES[selected_panel]
    if not panel_path.exists():
        st.error(f"Missing panel file: {panel_path.name}")
        st.stop()
    run_panel_script(panel_path)
