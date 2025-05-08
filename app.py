import streamlit as st
import requests
from datetime import datetime, timedelta
import json

# Set page config for full-width display
st.set_page_config(page_title="TSheets Manager", layout="wide")

# API Configuration
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBS_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"

# Session State Initialization
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
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=data
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        st.error(f"API Error: {err}")
        return None

# Get all timesheets
def get_timesheets():
    params = {
        "start_date": "2024-01-01",
        "end_date": datetime.now().date().isoformat(),
        "supplemental_data": "yes"
    }
    data = api_request("GET", TIMESHEETS_ENDPOINT, params=params)
    if data:
        sheets = list(data.get('results', {}).get('timesheets', {}).values())
        # Sort most recent first
        st.session_state.timesheets = sorted(sheets, key=lambda x: x.get('start', ''), reverse=True)

# Create a timesheet entry
def create_timesheet(new_entry):
    payload = {
        "data": [new_entry]
    }
    return api_request("POST", TIMESHEETS_ENDPOINT, data=payload)

# Update a timesheet entry
def update_timesheet(entry_id, updates):
    payload = {
        "data": [{
            "id": entry_id,
            **updates
        }]
    }
    return api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)

# ------------------- Sidebar: Authentication -------------------
with st.sidebar:
    st.title("🔐 TSheets Manager")
    auth_action = st.radio("Session", ["Login", "Logout"])

    if auth_action == "Login":
        auth_token = st.text_input("API Token", type="password")
        if st.button("Authenticate"):
            st.session_state.auth_token = auth_token
            user = api_request("GET", f"{BASE_URL}/current_user")
            if user:
                st.success("Authentication successful!")
                get_timesheets()
            else:
                st.error("Invalid API token")
    else:
        st.session_state.auth_token = None
        st.session_state.timesheets = []
        st.warning("You have been logged out.")

# ------------------- Main App -------------------
if st.session_state.auth_token:
    st.markdown("# 🕓 TSheets Dashboard")
    action = st.sidebar.radio("Choose Action", ["📋 View Timesheets", "➕ Add Entry", "✏️ Edit Entry"])

    # View Timesheets
    if action == "📋 View Timesheets":
        st.subheader("Recent Timesheets")
        if st.button("🔄 Refresh"):
            get_timesheets()

        if st.session_state.timesheets:
            display_data = []
            for entry in st.session_state.timesheets:
                display_data.append({
                    "ID": entry['id'],
                    "User ID": entry['user_id'],
                    "Job Code ID": entry['jobcode_id'],
                    "Date": entry.get('date'),
                    "Start": entry.get('start'),
                    "End": entry.get('end'),
                    "Duration": str(timedelta(seconds=entry.get('duration', 0))),
                    "Type": entry.get('type', '').capitalize(),
                    "Notes": entry.get('notes', '')
                })

            st.dataframe(display_data, use_container_width=True)
        else:
            st.info("No timesheet data available.")

    # Add Entry
    elif action == "➕ Add Entry":
        st.subheader("Add New Timesheet Entry")
        with st.form("add_form"):
            col1, col2 = st.columns(2)
            with col1:
                user_id = st.number_input("User ID", min_value=1)
                jobcode_id = st.number_input("Job Code ID", min_value=1)
                entry_type = st.selectbox("Type", ["regular", "manual"])
            with col2:
                date = st.date_input("Date")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")

            notes = st.text_area("Notes")
            custom1 = st.text_input("Custom Field 1")
            custom2 = st.text_input("Custom Field 2")

            if st.form_submit_button("Submit Entry"):
                new_entry = {
                    "user_id": user_id,
                    "jobcode_id": jobcode_id,
                    "type": entry_type,
                    "start": datetime.combine(date, start_time).isoformat(),
                    "end": datetime.combine(date, end_time).isoformat(),
                    "notes": notes,
                    "customfields": {
                        "19142": custom1,
                        "19144": custom2
                    }
                }
                response = create_timesheet(new_entry)
                if response:
                    st.success("New entry added!")
                    get_timesheets()

    # Edit Entry
    elif action == "✏️ Edit Entry":
        st.subheader("Edit Existing Entry")

        if st.session_state.timesheets:
            entry_ids = [entry['id'] for entry in st.session_state.timesheets]
            selected_id = st.selectbox("Select Entry by ID", entry_ids)
            entry = next((e for e in st.session_state.timesheets if e['id'] == selected_id), None)

            if entry:
                with st.form("edit_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        user_id = st.number_input("User ID", value=entry['user_id'])
                        jobcode_id = st.number_input("Job Code ID", value=entry['jobcode_id'])
                        entry_type = st.selectbox("Type", ["regular", "manual"],
                                                  index=0 if entry['type'] == "regular" else 1)
                    with col2:
                        start = st.text_input("Start", value=entry['start'])
                        end = st.text_input("End", value=entry['end'])

                    notes = st.text_area("Notes", value=entry.get('notes', ''))
                    custom1 = st.text_input("Custom Field 1", value=entry.get('customfields', {}).get("19142", ""))
                    custom2 = st.text_input("Custom Field 2", value=entry.get('customfields', {}).get("19144", ""))

                    if st.form_submit_button("Update Entry"):
                        updates = {
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
                        response = update_timesheet(selected_id, updates)
                        if response:
                            st.success("Entry updated!")
                            get_timesheets()
        else:
            st.warning("No timesheets available to edit.")
else:
    st.info("🔑 Please authenticate in the sidebar to begin.")

