import streamlit as st
from gsheets_helper import load_tasks, add_task, mark_task_complete

SHEET_NAME = "Secretarial_ToDo"

st.title("🗂️ Secretarial To-Do & Invoices")

# 1. Two Tabs: Standard To-Do vs. Invoice Entry
tab_todo, tab_invoice = st.tabs(["📝 Add To-Do", "🧾 Add Invoice"])

with tab_todo:
    with st.form("add_secretarial_task", clear_on_submit=True):
        col1, col2 = st.columns([4, 1], vertical_alignment="bottom")
        with col1:
            new_task = st.text_input("New Task Description", placeholder="e.g., Order toner cartridges for main office")
        with col2:
            submitted_todo = st.form_submit_button("➕ Add Task", type="primary", use_container_width=True)

        if submitted_todo:
            if new_task.strip():
                add_task(SHEET_NAME, new_task, st.session_state.username, task_type="To-Do", due_date="")
                st.toast("Task added!", icon="✅")
                st.rerun()
            else:
                st.warning("Please enter a task description first.")

with tab_invoice:
    with st.form("add_secretarial_invoice", clear_on_submit=True):
        i_col1, i_col2, i_col3 = st.columns([3.5, 1.5, 1], vertical_alignment="bottom")
        with i_col1:
            invoice_desc = st.text_input("Invoice Details / Supplier", placeholder="e.g., ESB Electricity Bill - €420.00")
        with i_col2:
            due_date_val = st.date_input("Date to be Submitted", format="DD/MM/YYYY")
        with i_col3:
            submitted_inv = st.form_submit_button("🧾 Add Invoice", type="primary", use_container_width=True)

        if submitted_inv:
            if invoice_desc.strip():
                due_str = due_date_val.strftime("%d/%m/%Y")
                add_task(SHEET_NAME, invoice_desc, st.session_state.username, task_type="Invoice", due_date=due_str)
                st.toast("Invoice added!", icon="🧾")
                st.rerun()
            else:
                st.warning("Please enter the invoice details first.")

st.divider()

# 2. Combined Pending Tasks & Invoices List
st.subheader("Pending Tasks & Invoices")
tasks_df = load_tasks(SHEET_NAME)

if tasks_df.empty:
    st.info("No tasks or invoices recorded yet.")
else:
    pending_df = tasks_df.loc[tasks_df["Status"].astype(str).str.strip().str.lower() == "pending"]
    total_pending = len(pending_df)
    total_completed = len(tasks_df) - total_pending

    m1, m2 = st.columns(2)
    m1.metric("📌 Pending Items", total_pending)
    m2.metric("✅ Completed All-Time", total_completed)

    if pending_df.empty:
        st.success("🎉 All caught up! No pending tasks or invoices.")
    else:
        for _, row in pending_df.iterrows():
            item_type = str(row.get("Type", "")).strip()
            due_date = str(row.get("Due Date", "")).strip()

            with st.container(border=True):
                c1, c2, c3, c4 = st.columns([4, 1.8, 1.4, 1.2])

                # Highlight Invoices clearly with a tag and submission due date
                if item_type.lower() == "invoice":
                    c1.markdown(f"🧾 **[INVOICE]** **{row['Description']}**")
                    c2.caption(f"⏰ Submit by: **{due_date}**" if due_date else f"📅 Added: {row['Date Added']}")
                else:
                    c1.markdown(f"**{row['Description']}**")
                    c2.caption(f"📅 {row['Date Added']}")

                c3.caption(f"👤 {row['Added By']}")

                if c4.button("✔ Complete", key=f"sec_done_{row['sheet_row']}", use_container_width=True):
                    mark_task_complete(SHEET_NAME, int(row["sheet_row"]), status_col=3)
                    st.toast("Marked as complete!", icon="🎉")
                    st.rerun()
