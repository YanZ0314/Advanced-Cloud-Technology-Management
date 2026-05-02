import streamlit as st


st.set_page_config(page_title="Governance and Controls Mapper", layout="wide")

st.title("Governance & Compliance")
st.write(
    "This app maps governance and execution boards to control responsibilities "
    "across SOC 2, HIPAA, and ISO 27001."
)

st.header("1) Organizational Chart (Governance and Execution Boards)")

org_chart = """
digraph G {
    rankdir=TB;
    graph [fontsize=12];
    node [shape=box, style="rounded,filled", color="#1f4e79", fillcolor="#e8f1fb", fontname="Arial"];
    edge [color="#4d4d4d"];

    Board [label="Board of Directors\\n(Governance Oversight)"];
    Steering [label="Security & Compliance Steering Committee\\n(Governance Board)"];
    Risk [label="Risk & Audit Committee\\n(Governance Board)"];

    SecOps [label="Security Operations Board\\n(Execution Board)"];
    IAM [label="IAM Working Group\\n(Execution Board)"];
    DataProt [label="Data Protection Council\\n(Execution Board)"];
    InternalAudit [label="Internal Audit Team\\n(Execution Function)"];

    Board -> Steering;
    Board -> Risk;
    Steering -> SecOps;
    Steering -> IAM;
    Steering -> DataProt;
    Risk -> InternalAudit;
}
"""

st.graphviz_chart(org_chart)

st.header("2) Responsibilities by Board and Function")

responsibilities = [
    {
        "Board / Function": "Board of Directors",
        "Primary Responsibility": "Approve security strategy and risk appetite; enforce accountability.",
        "Key Framework Focus": "SOC 2 CC1, ISO 27001 Clause 5",
    },
    {
        "Board / Function": "Security & Compliance Steering Committee",
        "Primary Responsibility": "Own enterprise control roadmap and review compliance posture monthly.",
        "Key Framework Focus": "SOC 2 CC2/CC3, HIPAA 164.308(a)(1), ISO 27001 Clauses 6 and 9",
    },
    {
        "Board / Function": "Risk & Audit Committee",
        "Primary Responsibility": "Validate independent assurance outcomes and track remediation progress.",
        "Key Framework Focus": "SOC 2 CC4, ISO 27001 Clause 9.2",
    },
    {
        "Board / Function": "IAM Working Group",
        "Primary Responsibility": "Run IAM policy audits; enforce least privilege and access recertification.",
        "Key Framework Focus": "SOC 2 CC6, HIPAA 164.312(a), ISO 27001 Annex A.9",
    },
    {
        "Board / Function": "Data Protection Council",
        "Primary Responsibility": "Mandate AES-256 encryption at rest and monitor encryption key management.",
        "Key Framework Focus": "SOC 2 CC6/CC7, HIPAA 164.312(a)(2)(iv), ISO 27001 Annex A.10",
    },
    {
        "Board / Function": "Security Operations Board",
        "Primary Responsibility": "Track incidents, vulnerabilities, and control performance metrics weekly.",
        "Key Framework Focus": "SOC 2 CC7, HIPAA 164.308(a)(6), ISO 27001 Annex A.16",
    },
    {
        "Board / Function": "Internal Audit Team",
        "Primary Responsibility": "Perform quarterly reviews and test evidence quality across all controls.",
        "Key Framework Focus": "SOC 2 Monitoring Activities, HIPAA periodic evaluations, ISO 27001 Clause 9.2",
    },
]

st.table(responsibilities)

st.header("Framework-to-Control Mapping")

framework_controls = {
    "SOC 2": [
        "CC6.1 Logical access controls (IAM policy audits)",
        "CC6.7 Data transmission and storage protection (AES-256 at rest)",
        "CC4.1 Monitoring and periodic evaluations (quarterly reviews)",
    ],
    "HIPAA": [
        "164.312(a)(1) Access control and unique user identification (IAM audits)",
        "164.312(a)(2)(iv) Encryption and decryption (AES-256 encryption safeguards)",
        "164.308(a)(8) Evaluation standard (quarterly compliance and risk reviews)",
    ],
    "ISO 27001": [
        "Annex A.9 Access Control (IAM policy audits and recertification)",
        "Annex A.10 Cryptography (AES-256 key and encryption management)",
        "Clause 9.2 Internal Audit (quarterly control testing and governance review)",
    ],
}

for framework, controls in framework_controls.items():
    with st.expander(framework, expanded=True):
        for item in controls:
            st.write(f"- {item}")

st.header("Control Calendar")
st.markdown(
    "- **Monthly:** Steering Committee compliance health review  \n"
    "- **Quarterly:** Internal audit reviews and access recertification  \n"
    "- **Continuous:** Encryption enforcement and security event monitoring"
)

