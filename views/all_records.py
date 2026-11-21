import streamlit as st
from gsheets_helper import load_tasks, load_users

st.title("📊 Full Sheet Viewer")
st.caption("Management only: Inspect complete records across any worksheet in a searchable table.")

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

# Load either Users or one of the 3 Task sheets
if sheet_name == "Users":
    df = load_users()
else:
    df = load_tasks(sheet_name)
    # Hide our internal helper column 'sheet_row' from the display table
    if not df.empty and "sheet_row" in df.columns:
        df = df.drop(columns=["sheet_row"])

if df.empty:
    st.info(f"No records found in {selected_label}.")
    st.stop()

# Apply Status filter (only for task sheets that have a Status column)
if "Status" in df.columns and status_filter != "All":
    df = df.loc[df["Status"].astype(str).str.strip().str.lower() == status_filter.lower()]

# Apply keyword search across all columns
if search_query.strip():
    mask = df.apply(lambda row: row.astype(str).str.contains(search_query.strip(), case=False).any(), axis=1)
    df = df.loc[mask]

# Summary metrics + CSV export bar
m1, m2 = st.columns([1, 3])
m1.metric("Rows Shown", len(df))

csv_bytes = df.to_csv(index=False).encode("utf-8")
m2.download_button(
    label="📥 Download Current View as CSV",
    data=csv_bytes,
    file_name=f"{sheet_name}.csv",
    mime="text/csv",
)

# Full interactive table (sortable columns, full-screen expand icon, search)
st.dataframe(df, use_container_width=True, hide_index=True)
