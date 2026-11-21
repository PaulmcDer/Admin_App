import streamlit as st
from gsheets_helper import load_tasks, delete_task_row

st.title("🗑️ Manage & Delete Records")
st.caption("Management only: Permanently remove mistaken or duplicate entries from any task list.")

SHEET_MAP = {
    "📋 Management To-Do": "Management_ToDo",
    "🗂️ Secretarial To-Do": "Secretarial_ToDo",
    "👩‍🏫 Staff To-Do": "Staff_ToDo",
}

col1, col2 = st.columns([2, 1])
with col1:
    selected_label = st.selectbox("Select Sheet to Manage", options=list(SHEET_MAP.keys()))
with col2:
    status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "Complete"])

sheet_name = SHEET_MAP[selected_label]
df = load_tasks(sheet_name)

if df.empty:
    st.info(f"No rows found in {selected_label}.")
    st.stop()

if status_filter != "All":
    df = df[df["Status"].astype(str).str.strip().str.lower() == status_filter.lower()]

if df.empty:
    st.info(f"No '{status_filter}' tasks found in {selected_label}.")
    st.stop()

st.divider()

# 1. Safety toggle right above the list (only appears on this page)
confirm_delete = st.toggle("🔓 Unlock permanent delete buttons", value=False)

for _, row in df.iterrows():
    row_num = int(row["sheet_row"])
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns([4, 1.5, 1.5, 1.2])
        c1.markdown(f"**{row['Description']}**")

        # Show Timeframe if viewing Management_ToDo, otherwise just Status
        if "Timeframe" in df.columns and str(row.get("Timeframe", "")).strip():
            c2.caption(f"🏷️ {row['Timeframe']} • {row['Status']}")
        else:
            c2.caption(f"📌 {row['Status']}")

        c3.caption(f"📅 {row['Date Added']} ({row['Added By']})")

        if confirm_delete:
            if c4.button("🗑️ Delete", key=f"del_{sheet_name}_{row_num}", type="secondary", use_container_width=True):
                delete_task_row(sheet_name, row_num)
                st.toast("Row permanently deleted!", icon="🗑️")
                st.rerun()
