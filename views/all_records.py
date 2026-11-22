import streamlit as st
from gsheets_helper import load_tasks, load_users, update_user_pin

st.title("📊 Full Sheet Viewer")
st.caption("Inspect complete records across any worksheet in a searchable table.")

is_super_admin = st.session_state.role == "Principal"

SHEET_OPTIONS = {
    "📋 Management To-Do": "Management_ToDo",
    "🗂️ Secretarial To-Do": "Secretarial_ToDo",
    "👩‍🏫 Staff To-Do": "Staff_ToDo",
    "🔑 Users & Roles": "Users",
}

col1, col2, col3 = st.columns([2, 1.5, 1.5])
with col1:
    selected_label = st.selectbox("Select Worksheet", options=list(SHEET_OPTIONS.keys()))
with col2:
    status_filter = st.selectbox("Filter by Status", options=["All", "Pending", "Complete"])
with col3:
    search_query = st.text_input("Search text", placeholder="Filter by keyword or name...")

sheet_name = SHEET_OPTIONS[selected_label]

if sheet_name == "Users":
    raw_users_df = load_users()
    df = raw_users_df.copy()

    # Hide sheet_row always; hide Pin if user is Management (only SuperAdmin sees Pins)
    cols_to_drop = ["sheet_row"]
    if not is_super_admin and "Pin" in df.columns:
        cols_to_drop.append("Pin")
    df = df.drop(columns=[c for c in cols_to_drop if c in df.columns])
else:
    df = load_tasks(sheet_name)
    if not df.empty and "sheet_row" in df.columns:
        df = df.drop(columns=["sheet_row"])

if df.empty:
    st.info(f"No records found in {selected_label}.")
    st.stop()

if "Status" in df.columns and status_filter != "All":
    df = df.loc[df["Status"].astype(str).str.strip().str.lower() == status_filter.lower()]

if search_query.strip():
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query.strip(), case=False).any(), axis=1)
    df = df.loc[mask]

m1, m2 = st.columns([1, 3])
m1.metric("Rows Shown", len(df))

csv_bytes = df.to_csv(index=False).encode("utf-8")
m2.download_button(
    label="📥 Download Current View as CSV",
    data=csv_bytes,
    file_name=f"{sheet_name}.csv",
    mime="text/csv",
)

st.dataframe(df, use_container_width=True, hide_index=True)

# 5. Principal-Only PIN Editor (appears only when viewing Users & logged in as Principal)
if sheet_name == "Users" and is_super_admin and not raw_users_df.empty:
    st.divider()
    st.subheader("🔐 Manage User PINs (Principal Only)")

    with st.form("edit_user_pin_form", clear_on_submit=True):
        p_col1, p_col2, p_col3 = st.columns([2, 1.5, 1], vertical_alignment="bottom")
        with p_col1:
            target_user = st.selectbox("Select Staff Member", options=raw_users_df["Username"].tolist())
        with p_col2:
            new_pin = st.text_input("New PIN", max_chars=8, placeholder="e.g. 4821")
        with p_col3:
            save_pin = st.form_submit_button("💾 Update PIN", type="primary", use_container_width=True)

        if save_pin:
            clean_pin = new_pin.strip()
            if len(clean_pin) >= 4 and clean_pin.isdigit():
                row_num = int(raw_users_df.loc[raw_users_df["Username"] == target_user, "sheet_row"].iloc[0])
                update_user_pin(row_num, clean_pin)
                st.toast(f"PIN updated for {target_user}!", icon="🔐")
                st.rerun()
            else:
                st.warning("Please enter a numeric PIN (at least 4 digits).")
