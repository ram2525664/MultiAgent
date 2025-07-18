import streamlit as st
import json

st.title("🔁 CMD Agent Feedback Log Viewer")

log_file = "Logs/feedback_log.jsonl"

with open(log_file, "r") as f:
    logs = [json.loads(line) for line in f.readlines()]

for log in logs[::-1]:  # Reverse chronological
    with st.expander(log["timestamp"]):
        st.write("🗣️ Input:", log["input"])
        st.write("🛠️ Tool:", log["tool"])
        st.code(log["output"], language="bash")
        st.write("📢 Feedback:", log["feedback"])
