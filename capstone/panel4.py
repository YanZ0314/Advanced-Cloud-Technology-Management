import streamlit as st


st.set_page_config(page_title="Decision Structures + SLA Terms", page_icon=":memo:", layout="wide")

st.title("Governance Model Refinement")
st.caption("Define governance decision bodies and service-level terms in one place.")


if "decision_structures" not in st.session_state:
    st.session_state.decision_structures = [
        {
            "name": "Monthly Cloud Steering Committee",
            "cadence": "Monthly",
            "owners": "CIO, Cloud Architect, Finance Lead",
            "scope": "Cloud strategy, cost optimization, risk acceptance",
        }
    ]

if "sla_terms" not in st.session_state:
    st.session_state.sla_terms = [
        {
            "service": "Core Platform Hosting",
            "target": "99.9%",
            "measurement_window": "Monthly",
            "penalty_or_action": "Service credit and remediation plan",
        }
    ]


st.subheader("Add a Decision Structure")
with st.form("decision_structure_form"):
    ds_name = st.text_input("Structure Name", placeholder="e.g., Monthly Cloud Steering Committee")
    ds_cadence = st.selectbox("Cadence", ["Weekly", "Biweekly", "Monthly", "Quarterly", "Ad hoc"])
    ds_owners = st.text_input("Decision Owners / Members", placeholder="e.g., CIO, Cloud Architect")
    ds_scope = st.text_area(
        "Decision Scope",
        placeholder="e.g., Prioritize cloud investments, approve architecture exceptions",
    )
    add_ds = st.form_submit_button("Add Decision Structure")
    if add_ds:
        if not ds_name.strip():
            st.warning("Please provide a structure name.")
        else:
            st.session_state.decision_structures.append(
                {
                    "name": ds_name.strip(),
                    "cadence": ds_cadence,
                    "owners": ds_owners.strip(),
                    "scope": ds_scope.strip(),
                }
            )
            st.success("Decision structure added.")


st.subheader("Add an SLA Term")
with st.form("sla_form"):
    sla_service = st.text_input("Service Name", placeholder="e.g., Core Platform Hosting")
    sla_target = st.text_input("Availability/Uptime Target", placeholder="e.g., 99.9% uptime")
    sla_window = st.selectbox("Measurement Window", ["Daily", "Weekly", "Monthly", "Quarterly"])
    sla_penalty = st.text_area(
        "Penalty / Response Action",
        placeholder="e.g., Service credit and root-cause review",
    )
    add_sla = st.form_submit_button("Add SLA Term")
    if add_sla:
        if not sla_service.strip() or not sla_target.strip():
            st.warning("Please provide both service name and SLA target.")
        else:
            st.session_state.sla_terms.append(
                {
                    "service": sla_service.strip(),
                    "target": sla_target.strip(),
                    "measurement_window": sla_window,
                    "penalty_or_action": sla_penalty.strip(),
                }
            )
            st.success("SLA term added.")


col1, col2 = st.columns(2)

with col1:
    st.markdown("### Decision Structures")
    if st.session_state.decision_structures:
        st.dataframe(st.session_state.decision_structures, use_container_width=True)
    else:
        st.info("No decision structures defined yet.")

with col2:
    st.markdown("### SLA Terms")
    if st.session_state.sla_terms:
        st.dataframe(st.session_state.sla_terms, use_container_width=True)
    else:
        st.info("No SLA terms defined yet.")


st.divider()
if st.button("Reset to Starter Examples"):
    st.session_state.decision_structures = [
        {
            "name": "Monthly Cloud Steering Committee",
            "cadence": "Monthly",
            "owners": "CIO, Cloud Architect, Finance Lead",
            "scope": "Cloud strategy, cost optimization, risk acceptance",
        }
    ]
    st.session_state.sla_terms = [
        {
            "service": "Core Platform Hosting",
            "target": "99.9%",
            "measurement_window": "Monthly",
            "penalty_or_action": "Service credit and remediation plan",
        }
    ]
    st.success("Reset complete.")
