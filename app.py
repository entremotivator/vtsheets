import streamlit as st
import requests
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="TSheets Manager", layout="wide")

# API Configuration
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBS_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"

# Session State
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'timesheets' not in st.session_state:
    st.session_state.timesheets = []

# API Request Wrapper
def api_request(method, url, params=None, data=None):
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request(method, url, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        st.error(f"API Error: {err}")
        return None

# Load Timesheets with Custom Date Range
def get_timesheets(start_date=None, end_date=None):
    if not start_date:
        start_date = datetime(2025, 5, 8).date()
    if not end_date:
        end_date = datetime.now().date()

    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "supplemental_data": "yes"
    }
    data = api_request("GET", TIMESHEETS_ENDPOINT, params=params)
    if data:
        timesheets = list(data.get('results', {}).get('timesheets', {}).values())
        st.session_state.timesheets = sorted(timesheets, key=lambda x: x.get('start'), reverse=True)

# Create Timesheet Entry
def create_timesheet(new_entry):
    payload = {"data": [new_entry]}
    return api_request("POST", TIMESHEETS_ENDPOINT, data=payload)

# Update Timesheet Entry
def update_timesheet(entry_id, updates):
    payload = {"data": [{ "id": entry_id, **updates }]}
    return api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)

# Sidebar Auth
with st.sidebar:
    st.title("🔐 TSheets Login")
    auth_action = st.radio("Session", ["Login", "Logout"])

    if auth_action == "Login":
        token_input = st.text_input("API Token", type="password")
        if st.button("Authenticate"):
            st.session_state.auth_token = token_input
            if api_request("GET", f"{BASE_URL}/current_user"):
                st.success("Authenticated!")
                get_timesheets()
            else:
                st.session_state.auth_token = None
                st.error("Invalid token.")
    else:
        st.session_state.auth_token = None
        st.warning("Logged out.")

# Main Application
if st.session_state.auth_token:
    action = st.sidebar.selectbox("Select Action", ["View Timesheets", "Add Entry", "Edit Entry"])

    if action == "View Timesheets":
        st.title("📋 View Timesheets")
        col1, col2 = st.columns(2)
        start_date = col1.date_input("Start Date", value=datetime(2025, 5, 8).date())
        end_date = col2.date_input("End Date", value=datetime(2025, 5, 8).date())

        if st.button("🔄 Refresh Data"):
            get_timesheets(start_date, end_date)

        if st.session_state.timesheets:
            st.dataframe(
                [
                    {
                        "ID": t["id"],
                        "User": t["user_id"],
                        "Job Code": t["jobcode_id"],
                        "Start": t["start"],
                        "End": t["end"],
                        "Duration": str(timedelta(seconds=t["duration"])),
                        "Type": t["type"].capitalize(),
                        "Notes": t["notes"]
                    }
                    for t in st.session_state.timesheets
                ],
                use_container_width=True
            )
        else:
            st.info("No timesheets found.")

    elif action == "Add Entry":
        st.title("➕ Add New Timesheet")
        with st.form("new_entry_form"):
            col1, col2 = st.columns(2)
            user_id = col1.number_input("User ID", min_value=1)
            jobcode_id = col1.number_input("Job Code ID", min_value=1)
            entry_type = col1.selectbox("Type", ["regular", "manual"])

            entry_date = col2.date_input("Date", value=datetime(2025, 5, 8).date())
            start_time = col2.time_input("Start Time")
            end_time = col2.time_input("End Time")

            notes = st.text_area("Notes")
            custom1 = st.text_input("Custom Field 1")
            custom2 = st.text_input("Custom Field 2")

            if st.form_submit_button("Create Entry"):
                start = datetime.combine(entry_date, start_time).isoformat()
                end = datetime.combine(entry_date, end_time).isoformat()
                new_entry = {
                    "user_id": user_id,
                    "jobcode_id": jobcode_id,
                    "type": entry_type,
                    "start": start,
                    "end": end,
                    "notes": notes,
                    "customfields": {
                        "19142": custom1,
                        "19144": custom2
                    }
                }
                if create_timesheet(new_entry):
                    st.success("Entry created successfully.")
                    get_timesheets()

    elif action == "Edit Entry":
        st.title("✏️ Edit Timesheet")
        if st.session_state.timesheets:
            selected_id = st.selectbox("Choose Entry ID", [t["id"] for t in st.session_state.timesheets])
            entry = next(t for t in st.session_state.timesheets if t["id"] == selected_id)

            with st.form("edit_entry_form"):
                col1, col2 = st.columns(2)
                user_id = col1.number_input("User ID", value=entry["user_id"])
                jobcode_id = col1.number_input("Job Code ID", value=entry["jobcode_id"])
                entry_type = col1.selectbox("Type", ["regular", "manual"], index=0 if entry["type"] == "regular" else 1)

                start_str = col2.text_input("Start Time", value=entry["start"])
                end_str = col2.text_input("End Time", value=entry["end"])

                notes = st.text_area("Notes", value=entry["notes"])
                custom1 = st.text_input("Custom Field 1", value=entry.get("customfields", {}).get("19142", ""))
                custom2 = st.text_input("Custom Field 2", value=entry.get("customfields", {}).get("19144", ""))

                if st.form_submit_button("Update Entry"):
                    updates = {
                        "user_id": user_id,
                        "jobcode_id": jobcode_id,
                        "type": entry_type,
                        "start": start_str,
                        "end": end_str,
                        "notes": notes,
                        "customfields": {
                            "19142": custom1,
                            "19144": custom2
                        }
                    }
                    if update_timesheet(selected_id, updates):
                        st.success("Entry updated successfully.")
                        get_timesheets()
        else:
            st.warning("No entries to edit.")
else:
    st.info("Please log in to manage timesheets.")
