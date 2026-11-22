import streamlit as st
from gsheets_helper import load_tasks, add_task, mark_task_complete

SHEET_NAME = "Secretarial_ToDo"

st.title("🗂️ Secretarial To-Do List")

# 1. Section to Add a New Task
with st.form("add_secretarial_task", clear_on_submit=True):  # (keep "add_secretarial_task" in secretarial.py)
    col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
    with col1:
        new_task = st.text_input("New Task Description", placeholder="e.g., Submit yard duty preferences for next term")
    with col2:
        submitted = st.form_submit_button("➕ Add Task", type="primary", use_container_width=True)

    if submitted:
        if new_task.strip():
            add_task(SHEET_NAME, new_task, st.session_state.username)
            st.toast("Task added!", icon="✅")
            st.rerun()
        else:
            st.warning("Please enter a task description first.")

st.divider()

# 2. Section to View & Complete Pending Tasks Only
st.subheader("Pending Tasks")
tasks_df = load_tasks(SHEET_NAME)

if tasks_df.empty:
    st.info("No tasks recorded yet.")
else:
    pending_df = tasks_df[tasks_df["Status"].astype(str).str.strip().str.lower() == "pending"]
    total_pending = len(pending_df)
    total_completed = len(tasks_df) - total_pending

    m1, m2 = st.columns(2)
    m1.metric("📌 Pending Tasks", total_pending)
    m2.metric("✅ Completed All-Time", total_completed)

    if pending_df.empty:
        st.success("🎉 All caught up! No pending secretarial tasks.")
    else:
        for _, row in pending_df.iterrows():
            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 1.5, 1.5, 1.2])
                c1.markdown(f"**{row['Description']}**")
                c2.caption(f"📅 {row['Date Added']}")
                c3.caption(f"👤 {row['Added By']}")
                if c4.button("✔ Complete", key=f"sec_done_{row['sheet_row']}", use_container_width=True):
                    mark_task_complete(SHEET_NAME, int(row["sheet_row"]), status_col=3)
                    st.toast("Marked as complete!", icon="🎉")
                    st.rerun()

