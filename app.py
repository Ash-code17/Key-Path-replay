import json
from datetime import datetime, timedelta, timezone
from io import BytesIO

import pandas as pd
import streamlit as st

st.set_page_config(page_title="KeyPath Replay", page_icon="🔐", layout="wide")

st.title("🔐 KeyPath Replay")
st.caption("Simple, safe integration-key replay simulator | Case CR-26-047")
st.warning(
    "Demo mode only: all replay actions are synthetic. This app does not connect to real APIs "
    "or systems, and it does not use real credentials."
)

# Sample key profiles based on the case brief
KEYS = {
    "key-tb-07": {
        "owner": "tb-sync-svc", "scope": "Read / Write", "modules": "All modules",
        "ip_limit": "None", "expiry": "No expiry", "status": "Active"
    },
    "tb-sync-svc": {
        "owner": "Platform Integration", "scope": "Admin",
        "modules": "All modules", "ip_limit": "None",
        "expiry": "No expiry", "status": "Active"
    },
    "key-tb-03": {
        "owner": "Legacy Sync", "scope": "Read",
        "modules": "Vendor", "ip_limit": "Configured", 
        "expiry": "90 days", "status": "Active (legacy)"
    },
}

REQUIRED = {
    "E01 / E18 API logs": ["request_id", "api_key_id", "endpoint", "method", "status"],
    "E19 Vendor changes": ["request_id", "field", "changed_by", "approval_ref"],
    "E15 Network flows": ["src_ip", "dst_system", "bytes_out"],
    "E02 Support audit": ["actor", "action", "object_id", "result"],
    "E05 File access": ["principal", "action", "path", "result"],
}

if "evidence" not in st.session_state:
    st.session_state.evidence = {}
if "events" not in st.session_state:
    st.session_state.events = []

overview, ingest, profile, replay, proof = st.tabs(
    ["Overview", "Evidence Upload", "Key Profile", "Safe Replay", "Proof Pack"]
)

with overview:
    st.subheader("What does KeyPath Replay do?")
    st.write(
        "It demonstrates what a broadly permissioned integration key could do in a "
        "synthetic environment, then lists the records an investigator would expect to review."
    )
    c1, c2, c3 = st.columns(3)
    c1.metric("Key profiles", len(KEYS))
    c2.metric("Evidence types", len(REQUIRED))
    c3.metric("Replay actions", len(st.session_state.events))
    st.markdown("**Workflow**")
    st.write("1. Upload evidence copies  →  2. Review key permissions  →  "
             "3. Run a synthetic replay  →  4. Export the proof pack.")
    st.info(
        "The case presentation identifies broad permissions as a configuration weakness. "
        "That alone does not prove that a key was misused."
    )

with ingest:
    st.subheader("Upload evidence files")
    st.write("Upload CSV or JSON copies. Original files are not edited.")
    evidence_type = st.selectbox("Evidence type", list(REQUIRED))
    file = st.file_uploader("Choose a CSV or JSON file", type=["csv", "json"])
    if file is not None:
        try:
            if file.name.lower().endswith(".json"):
                data = json.load(file)
                if isinstance(data, dict):
                    data = data.get("records", [data])
                df = pd.DataFrame(data)
            else:
                df = pd.read_csv(file)
            missing = [col for col in REQUIRED[evidence_type] if col not in df.columns]
            st.session_state.evidence[evidence_type] = df
            if missing:
                st.error("Missing required columns: " + ", ".join(missing))
            else:
                st.success("File loaded. Required columns are present.")
        except Exception as error:
            st.error(f"Could not read this file: {error}")

    if st.session_state.evidence:
        st.markdown("**Uploaded evidence**")
        for name, df in st.session_state.evidence.items():
            with st.expander(f"{name} — {len(df)} rows"):
                st.dataframe(df, use_container_width=True)

with profile:
    st.subheader("Integration key profile")
    selected_key = st.selectbox("Choose a key", list(KEYS))
    details = KEYS[selected_key]
    left, right = st.columns(2)
    with left:
        st.write(f"**Key:** {selected_key}")
        st.write(f"**Owner:** {details['owner']}")
        st.write(f"**Permission:** {details['scope']}")
        st.write(f"**Modules:** {details['modules']}")
    with right:
        st.write(f"**IP restriction:** {details['ip_limit']}")
        st.write(f"**Token lifetime:** {details['expiry']}")
        st.write(f"**Status:** {details['status']}")
    if details["scope"] in ("Read / Write", "Admin") or details["modules"] == "All modules":
        st.warning("Broad capability detected. This is a configuration finding, not proof of misuse.")
    else:
        st.success("This sample profile has a narrower permission scope.")

with replay:
    st.subheader("Run a safe synthetic replay")
    st.write("The replay creates five mock events locally. No real request is sent.")
    selected_key = st.selectbox("Key for this replay", list(KEYS), key="replay_key")
    source_ip = st.text_input("Synthetic source IP", "198.51.100.25")
    approval = st.text_input("Synthetic approval reference", "SIM-APPROVAL-01")
    if st.button("Run replay", type="primary"):
        now = datetime.now(timezone.utc)
        steps = [
            ("KEY_CHECK", "GET", "/mock/profile", "SIMULATED"),
            ("FINANCE_DISCOVERY", "GET", "/mock/finance/capabilities", "SIMULATED"),
            ("SYNTHETIC_EXPORT", "POST", "/mock/finance/vendor-export", "SIMULATED"),
            ("VENDOR_CHANGE_ATTEMPT", "POST", "/mock/vendors/bank-details", "BLOCKED_IN_SIMULATION"),
            ("TRACE_REVIEW", "GET", "/mock/audit/footprint", "SIMULATED"),
        ]
        run_id = now.strftime("SIM-%Y%m%d-%H%M%S")
        st.session_state.events = []
        for index, (action, method, endpoint, status) in enumerate(steps, start=1):
            st.session_state.events.append({
                "timestamp_utc": (now + timedelta(minutes=index - 1)).isoformat(),
                "request_id": f"{run_id}-{index:02d}",
                "api_key_id": selected_key,
                "action": action,
                "method": method,
                "endpoint": endpoint,
                "source_ip": source_ip,
                "approval_ref": approval,
                "status": status,
                "environment": "SYNTHETIC"
            })
        st.success(f"Replay complete: {run_id}")

    if st.session_state.events:
        st.dataframe(pd.DataFrame(st.session_state.events), use_container_width=True)

with proof:
    st.subheader("Proof pack")
    if not st.session_state.events:
        st.info("Run a synthetic replay first.")
    else:
        events_df = pd.DataFrame(st.session_state.events)
        st.write("**Generated event timeline**")
        st.dataframe(events_df, use_container_width=True)
        st.write("**Evidence review status**")
        statuses = []
        for name in REQUIRED:
            if name in st.session_state.evidence:
                statuses.append({"Evidence": name, "Status": "Uploaded — review required"})
            else:
                statuses.append({"Evidence": name, "Status": "UNKNOWN — not uploaded"})
        st.dataframe(pd.DataFrame(statuses), use_container_width=True, hide_index=True)

        st.download_button(
            "Download event timeline (CSV)",
            events_df.to_csv(index=False).encode("utf-8"),
            "keypath_timeline.csv",
            "text/csv"
        )
        report = {
            "case_id": "CR-26-047",
            "generated_at_utc": datetime.now(timezone.utc).isoformat(),
            "events": st.session_state.events,
            "evidence_status": statuses,
            "limitations": [
                "All replay events are synthetic.",
                "No external systems or APIs were contacted.",
                "UNKNOWN means evidence was not available or not checked; it is not proof.",
                "This simulation does not establish real-world attribution or intent."
            ]
        }
        st.download_button(
            "Download complete proof pack (JSON)",
            json.dumps(report, indent=2),
            "keypath_proof_pack.json",
            "application/json"
        )

st.divider()
st.caption("KeyPath Replay · CRIMEATHON 2026 · Local synthetic demonstration")
