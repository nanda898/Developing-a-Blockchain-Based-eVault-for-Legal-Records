"""
eVault – Streamlit UI
"""

import streamlit as st, requests

API = "http://localhost:5000"

st.set_page_config(page_title="eVault", page_icon="📄", layout="wide")
st.title("📄 Blockchain based eVault for Legal Records")

tabs = st.tabs([
    "🔼 Upload",
    "🔽 Download",
    "📜 Audit Logs",
    "📑 All Logs"
])

# ─── Upload ────────────────────────────────────────────────────
with tabs[0]:
    st.header("Upload document")
    owner = st.text_input("Your name / ID")
    meta  = st.text_area("Metadata / description")
    file  = st.file_uploader("Choose file")
    if st.button("Upload"):
        if not file:
            st.error("Please choose a file.")
            st.stop()
        r = requests.post(f"{API}/upload",
                          files={"file": (file.name, file.getvalue())},
                          data={"owner": owner, "meta": meta})
        if r.ok:
            st.success(f"Uploaded! Document ID: {r.json()['docId']}")
        else:
            st.error(f"Upload failed ({r.status_code}): {r.text[:300]}")

# ─── Download ──────────────────────────────────────────────────
with tabs[1]:
    st.header("Download by ID")
    did = st.text_input("Document ID")
    if st.button("Get download link"):
        r = requests.get(f"{API}/download/{did}")
        if r.ok:
            d = r.json()
            st.markdown(f"[Download file]({d['url']}) _(15 min link)_")
            st.code(d["hash"], language="text")
        else:
            st.error(f"Not found ({r.status_code})")

# ─── Audit Logs (per doc) ──────────────────────────────────────
with tabs[2]:
    st.header("Audit log for a document")
    did2 = st.text_input("Document ID  ")
    if st.button("Fetch log"):
        rows = requests.get(f"{API}/logs/{did2}").json()
        if rows:
            st.table(rows)
        else:
            st.info("No log entries.")

# ─── NEW: All Logs tab ────────────────────────────────────────
with tabs[3]:
    st.header("Recent activity (latest N)")
    num = st.slider("Max rows", 10, 500, 100, 10)
    if st.button("Refresh"):
        r = requests.get(f"{API}/logs/all", params={"limit": num})
        if r.ok:
            st.table(r.json())
        else:
            st.error(f"Server error ({r.status_code})")
