import streamlit as st
from gsheets_helper import load_users

st.set_page_config(
    page_title="Killeen Admin Hub",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)

def load_custom_css():
    st.markdown(
        """
        <style>
        /* Reduce excessive default top whitespace on all pages */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1100px;
        }

        /* Give bordered task cards a subtle shadow and crisp left accent border */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            background-color: #FFFFFF;
            border-radius: 10px;
            border-left: 5px solid #1B5E20;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
            margin-bottom: 0.5rem;
        }

        /* Polish form containers */
        div[data-testid="stForm"] {
            background-color: #FFFFFF;
            border-radius: 12px;
            padding: 1.5rem;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
        }

        /* Mobile-specific adjustments (phones & small tablets) */
        @media (max-width: 640px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 0.8rem;
                padding-right: 0.8rem;
            }
            div[data-testid="stForm"] {
                padding: 1rem;
            }
            input, select {
                font-size: 16px !important;
            }
        }

        /* Hide the Deploy button and developer menu on BOTH desktop and mobile */
        .stAppDeployButton { display: none; }
        #MainMenu { visibility: hidden; }

        </style>
        """,
        unsafe_allow_html=True,
    )

load_custom_css()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""


def login_screen():
    # 1. Full-width centered header (breathes across the page on one line)
    st.markdown(
        """
        <div style='text-align: center; padding: 1.5rem 0 1.2rem 0;'>
            <h1 style='margin: 0; font-size: clamp(1.7rem, 4vw, 2.5rem); font-weight: 700;'>
                🏫 Killeen NS Admin Hub
            </h1>
            <p style='color: #64748B; font-size: 1.05rem; margin-top: 0.4rem;'>
                Select your name and enter your PIN to continue
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    users_df = load_users()
    users_df["Username"] = users_df["Username"].astype(str).str.strip()
    users_df["Pin_clean"] = users_df["Pin"].astype(str).str.strip()
    user_list = users_df["Username"].tolist()

    # 2. Narrow centered column strictly for the login card
    _, center_col, _ = st.columns([1, 1.2, 1])
    with center_col:
        with st.form("login_form"):
            selected_user = st.selectbox("Select User", options=user_list)
            pin_input = st.text_input("PIN", type="password", max_chars=8)
            submitted = st.form_submit_button("Log In", type="primary", use_container_width=True)

            if submitted:
                clean_pin = pin_input.strip()
                match = users_df[
                    (users_df["Username"] == selected_user) &
                    (users_df["Pin_clean"] == clean_pin)
                ]

                if not match.empty:
                    user_row = match.iloc[0]
                    st.session_state.authenticated = True
                    st.session_state.username = user_row["Username"]
                    st.session_state.role = str(user_row["Role"]).strip()
                    st.rerun()
                else:
                    st.error("Incorrect PIN. Please try again.")

# --- THIS PART ACTUALLY RUNS THE GATEKEEPER ---
if not st.session_state.authenticated:
    login_screen()
    st.stop()

secretarial_page = st.Page("views/secretarial.py", title="Secretarial To-Do", icon="🗂️")
management_page = st.Page("views/management.py", title="Management To-Do", icon="📋")
staff_page = st.Page("views/staff.py", title="Staff To-Do", icon="👩‍🏫")
records_page = st.Page("views/all_records.py", title="Full Sheet Viewer", icon="📊")
delete_page = st.Page("views/admin_manage.py", title="Manage & Delete", icon="🗑️")

role = st.session_state.role
if role == "Management":
    allowed_pages = [management_page, secretarial_page, staff_page, records_page, delete_page]
elif role == "Secretarial":
    allowed_pages = [secretarial_page]
else:
    allowed_pages = [staff_page]


pg = st.navigation(allowed_pages)

with st.sidebar:
    st.success(f"🔓 {st.session_state.username} ({role})")
    if st.button("🔄 Refresh Tasks", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    if st.button("Log Out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.session_state.role = ""
        st.rerun()

pg.run()
