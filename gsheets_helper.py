import streamlit as st
import gspread
import pandas as pd
from datetime import date



@st.cache_resource
def get_spreadsheet():
    """Authorize gspread once and return the Master Workbook."""
    gc = gspread.service_account_from_dict(st.secrets["gcp_service_account"])
    return gc.open_by_url(st.secrets["sheet_url"])

@st.cache_data(ttl=15)
def load_users() -> pd.DataFrame:
    """Fetch all rows from the Users tab as a DataFrame."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet("Users")
    records = worksheet.get_all_records()
    st.cache_data.clear()
    return pd.DataFrame(records)

@st.cache_data(ttl=15)
def load_tasks(sheet_name: str) -> pd.DataFrame:
    """Fetch all rows from a task sheet and track their exact Google Sheet row number."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet(sheet_name)
    records = worksheet.get_all_records()
    df = pd.DataFrame(records)
    if not df.empty:
        # Row 1 in Google Sheets is the header, so data starts at Row 2
        df["sheet_row"] = range(2, len(df) + 2)
    return df


def add_task(sheet_name: str, description: str, added_by: str):
    """Append a new Pending task row to the bottom of the sheet."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet(sheet_name)
    today_str = date.today().strftime("%d/%m/%Y")
    worksheet.append_row([today_str, description.strip(), "Pending", added_by])
    st.cache_data.clear()

def mark_task_complete(sheet_name: str, sheet_row: int, status_col: int = 3):
    """Update only the Status cell of a specific row to 'Complete'."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet(sheet_name)
    worksheet.update_cell(sheet_row, status_col, "Complete")
    st.cache_data.clear()

def add_management_task(description: str, timeframe: str, added_by: str):
    """Append a new Pending management plan row with a Timeframe."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet("Management_ToDo")
    today_str = date.today().strftime("%d/%m/%Y")
    worksheet.append_row([today_str, description.strip(), timeframe, "Pending", added_by])
    st.cache_data.clear()

def update_management_task(sheet_row: int, description: str, timeframe: str, status: str):
    """Update Description (Col B), Timeframe (Col C), and Status (Col D) in one API call."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet("Management_ToDo")
    worksheet.update(f"B{sheet_row}:D{sheet_row}", [[description.strip(), timeframe, status]])
    st.cache_data.clear()

def delete_task_row(sheet_name: str, sheet_row: int):
    """Permanently delete a specific row from the chosen worksheet."""
    sh = get_spreadsheet()
    worksheet = sh.worksheet(sheet_name)
    worksheet.delete_rows(sheet_row)
    st.cache_data.clear()
