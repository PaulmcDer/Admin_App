import streamlit as st
from gsheets_helper import load_tasks, add_management_task, update_management_task

SHEET_NAME = "Management_ToDo"
TIMEFRAMES = ["Short Term", "Medium Term", "Long Term"]

st.title("📋 Management To-Do & Strategic Plans")

# 1. Section to Add a New Management Plan
with st.form("add_mgmt_task", clear_on_submit=True):
    col1, col2, col3 = st.columns([3.5, 1.5, 1], vertical_alignment="bottom")
    with col1:
        new_task = st.text_input("Plan / Task Description", placeholder="e.g., Draft Board of Management term report")
    with col2:
        timeframe = st.selectbox("Timeframe", options=TIMEFRAMES)
    with col3:
        submitted = st.form_submit_button("➕ Add Plan", type="primary", use_container_width=True)

    if submitted:
        if new_task.strip():
            add_management_task(new_task, timeframe, st.session_state.username)
            st.toast("Management plan added!", icon="✅")
            st.rerun()
        else:
            st.warning("Please enter a description first.")

st.divider()

# 2. Load Tasks and Organize into Tabs
tasks_df = load_tasks(SHEET_NAME)

if tasks_df.empty:
    st.info("No management tasks recorded yet.")
    st.stop()

# Clean string columns safely
tasks_df["Status_clean"] = tasks_df["Status"].astype(str).str.strip()
tasks_df["Timeframe_clean"] = tasks_df["Timeframe"].astype(str).str.strip()

pending_df = tasks_df.loc[tasks_df["Status_clean"].str.lower() == "pending"]

# At-a-Glance Strategic Summary Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("⚡ Short Term", len(pending_df[pending_df["Timeframe_clean"] == "Short Term"]))
m2.metric("📅 Medium Term", len(pending_df[pending_df["Timeframe_clean"] == "Medium Term"]))
m3.metric("🎯 Long Term", len(pending_df[pending_df["Timeframe_clean"] == "Long Term"]))
m4.metric("✅ Completed", len(tasks_df) - len(pending_df))

st.write("")

tab_short, tab_med, tab_long, tab_all = st.tabs([
    "⚡ Short Term",
    "📅 Medium Term",
    "🎯 Long Term",
    "📚 All & Completed",
])

def render_task_cards(df_subset, tab_prefix: str):
    """Reusable helper to display and edit management tasks inside any tab."""
    if df_subset.empty:
        st.success("No items in this view.")
        return

    for _, row in df_subset.iterrows():
        row_num = int(row["sheet_row"])
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([4, 1.5, 1.5, 1.2])
            c1.markdown(f"**{row['Description']}**")
            c2.caption(f"🏷️ {row['Timeframe_clean']} • {row['Status_clean']}")
            c3.caption(f"📅 {row['Date Added']} ({row['Added By']})")

            # Quick 1-click Complete button if still Pending
            if row["Status_clean"].lower() == "pending":
                if c4.button("✔ Complete", key=f"{tab_prefix}_done_{row_num}", use_container_width=True):
                    update_management_task(row_num, row["Description"], row["Timeframe_clean"], "Complete")
                    st.toast("Plan marked complete!", icon="🎉")
                    st.rerun()

            # Expandable Edit Box right inside the card
            with st.expander("✏️ Edit Plan"):
                with st.form(key=f"{tab_prefix}_edit_form_{row_num}"):
                    edit_desc = st.text_input("Description", value=str(row["Description"]))
                    e_col1, e_col2 = st.columns([1, 1])
                    with e_col1:
                        tf_index = TIMEFRAMES.index(row["Timeframe_clean"]) if row["Timeframe_clean"] in TIMEFRAMES else 0
                        edit_tf = st.selectbox("Timeframe", options=TIMEFRAMES, index=tf_index)
                    with e_col2:
                        status_opts = ["Pending", "Complete"]
                        st_index = 1 if row["Status_clean"].lower() == "complete" else 0
                        edit_status = st.selectbox("Status", options=status_opts, index=st_index)

                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        if edit_desc.strip():
                            update_management_task(row_num, edit_desc, edit_tf, edit_status)
                            st.toast("Changes saved!", icon="💾")
                            st.rerun()
                        else:
                            st.warning("Description cannot be empty.")


pending_df = tasks_df[tasks_df["Status_clean"].str.lower() == "pending"]

with tab_short:
    render_task_cards(pending_df[pending_df["Timeframe_clean"] == "Short Term"], "short")

with tab_med:
    render_task_cards(pending_df[pending_df["Timeframe_clean"] == "Medium Term"], "med")

with tab_long:
    render_task_cards(pending_df[pending_df["Timeframe_clean"] == "Long Term"], "long")

with tab_all:
    render_task_cards(tasks_df, "all")
