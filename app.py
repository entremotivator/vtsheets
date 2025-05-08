import streamlit as st
import requests
from datetime import datetime, timedelta
import json

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
    except requests.exceptions.HTTPError as err:
        st.error(f"API Error: {err}")
        return None

def get_timesheets():
    params = {
        "start_date": "2024-01-01",
        "end_date": datetime.now().date().isoformat(),
        "supplemental_data": "yes"
    }
    data = api_request("GET", TIMESHEETS_ENDPOINT, params=params)
    if data:
        st.session_state.timesheets = list(data.get('results', {}).get('timesheets', {}).values())

def create_timesheet(new_entry):
    payload = {
        "data": [{
            "user_id": new_entry['user_id'],
            "jobcode_id": new_entry['jobcode_id'],
            "type": new_entry['type'],
            "start": new_entry['start'],
            "end": new_entry['end'],
            "notes": new_entry['notes'],
            "customfields": new_entry['customfields']
        }]
    }
    return api_request("POST", TIMESHEETS_ENDPOINT, data=payload)

def update_timesheet(entry_id, updates):
    payload = {
        "data": [{
            "id": entry_id,
            **updates
        }]
    }
    return api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)

# Authentication Sidebar
with st.sidebar:
    st.title("🔐 TSheets Manager")
    auth_action = st.radio("Auth", ["Login", "Logout"])
   
    if auth_action == "Login":
        auth_token = st.text_input("API Token", type="password")
        if st.button("Authenticate"):
            st.session_state.auth_token = auth_token
            try:
                test_response = api_request("GET", f"{BASE_URL}/current_user")
                if test_response:
                    st.success("Authenticated successfully!")
                    get_timesheets()
            except:
                st.error("Invalid API token")

    else:
        st.session_state.auth_token = None
        st.warning("Logged out")

# Main App Logic
if st.session_state.auth_token:
    action = st.sidebar.selectbox("Action", ["View Timesheets", "Add Entry", "Edit Entry"])
   
    # View Timesheets
    if action == "View Timesheets":
        st.title("📋 Timesheet Overview")
        if st.button("Refresh Data"):
            get_timesheets()
       
        if st.session_state.timesheets:
            display_data = []
            for entry in st.session_state.timesheets:
                display_entry = {
                    "ID": entry['id'],
                    "User": entry['user_id'],
                    "Job Code": entry['jobcode_id'],
                    "Date": entry['date'],
                    "Duration": str(timedelta(seconds=entry['duration'])),
                    "Type": entry['type'].capitalize(),
                    "Notes": entry['notes']
                }
                display_data.append(display_entry)
           
            st.dataframe(
                data=display_data,
                use_container_width=True,
                column_config={
                    "Duration": st.column_config.TextColumn("Duration", help="HH:MM:SS format"),
                    "Notes": st.column_config.TextColumn("Notes", width="large")
                }
            )
        else:
            st.info("No timesheets found")

    # Add Timesheet
    elif action == "Add Entry":
        st.title("➕ Add New Entry")
        with st.form("new_entry"):
            col1, col2 = st.columns(2)
            with col1:
                user_id = st.number_input("User ID", min_value=1)
                jobcode_id = st.number_input("Job Code ID", min_value=1)
                entry_type = st.selectbox("Entry Type", ["regular", "manual"])
           
            with col2:
                start_date = st.date_input("Date")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")
           
            notes = st.text_area("Notes")
            custom1 = st.text_input("Custom Field 1")
            custom2 = st.text_input("Custom Field 2")
           
            if st.form_submit_button("Submit Entry"):
                start_dt = datetime.combine(start_date, start_time).isoformat()
                end_dt = datetime.combine(start_date, end_time).isoformat()
               
                new_entry = {
                    "user_id": user_id,
                    "jobcode_id": jobcode_id,
                    "type": entry_type,
                    "start": start_dt,
                    "end": end_dt,
                    "notes": notes,
                    "customfields": {
                        "19142": custom1,
                        "19144": custom2
                    }
                }
               
                response = create_timesheet(new_entry)
                if response:
                    st.success("Entry created successfully!")
                    get_timesheets()

    # Edit Timesheet
    elif action == "Edit Entry":
        st.title("✏️ Edit Entry")
        if st.session_state.timesheets:
            selected_id = st.selectbox("Select Entry", [t['id'] for t in st.session_state.timesheets])
            selected_entry = next(t for t in st.session_state.timesheets if t['id'] == selected_id)
           
            with st.form("edit_entry"):
                col1, col2 = st.columns(2)
                with col1:
                    new_user = st.number_input("User ID", value=selected_entry['user_id'])
                    new_jobcode = st.number_input("Job Code ID", value=selected_entry['jobcode_id'])
                    new_type = st.selectbox("Type", ["regular", "manual"],
                                         index=0 if selected_entry['type'] == "regular" else 1)
               
                with col2:
                    new_start = st.text_input("Start Time", value=selected_entry['start'])
                    new_end = st.text_input("End Time", value=selected_entry['end'])
               
                new_notes = st.text_area("Notes", value=selected_entry['notes'])
                new_custom1 = st.text_input("Custom Field 1",
                                          value=selected_entry['customfields'].get("19142", ""))
                new_custom2 = st.text_input("Custom Field 2",
                                          value=selected_entry['customfields'].get("19144", ""))
               
                if st.form_submit_button("Update Entry"):
                    updates = {
                        "user_id": new_user,
                        "jobcode_id": new_jobcode,
                        "type": new_type,
                        "start": new_start,
                        "end": new_end,
                        "notes": new_notes,
                        "customfields": {
                            "19142": new_custom1,
                            "19144": new_custom2
                        }
                    }
                   
                    response = update_timesheet(selected_id, updates)
                    if response:
                        st.success("Entry updated successfully!")
                        get_timesheets()
        else:
            st.warning("No entries available for editing")

else:
    st.info("Please authenticate using the sidebar to access timesheet management")
