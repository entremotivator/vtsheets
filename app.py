import streamlit as st
import requests
from datetime import datetime, timedelta

# --- API Configuration ---
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBS_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"

# --- Session State Initialization ---
for key in ['auth_token', 'timesheets']:
    if key not in st.session_state:
        st.session_state[key] = None if key == 'auth_token' else []

# --- Utility Functions ---
def api_request(method, url, params=None, data=None):
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }
    try:
        response = requests.request(method, url, headers=headers, params=params, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {e}")
        return None

def get_timesheets():
    params = {
        "start_date": "2024-01-01",
        "end_date": datetime.now().date().isoformat(),
        "supplemental_data": "yes"
    }
    data = api_request("GET", TIMESHEETS_ENDPOINT, params=params)
    if data:
        st.session_state.timesheets = list(data.get("results", {}).get("timesheets", {}).values())
    else:
        st.session_state.timesheets = []

def create_timesheet(entry):
    payload = {"data": [entry]}
    return api_request("POST", TIMESHEETS_ENDPOINT, data=payload)

def update_timesheet(entry_id, updates):
    payload = {"data": [{"id": entry_id, **updates}]}
    return api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)

# --- Sidebar: Authentication ---
with st.sidebar:
    st.title("🔐 TSheets Manager")
    auth_action = st.radio("Authentication", ["Login", "Logout"])

    if auth_action == "Login":
        token = st.text_input("API Token", type="password")
        if st.button("Authenticate"):
            st.session_state.auth_token = token
            user_check = api_request("GET", f"{BASE_URL}/current_user")
            if user_check:
                st.success("✅ Authentication successful!")
                get_timesheets()
            else:
                st.error("❌ Invalid API token")
    else:
        st.session_state.auth_token = None
        st.warning("Logged out successfully.")

# --- Main App Content ---
if st.session_state.auth_token:

    action = st.sidebar.selectbox("Select Action", ["View Timesheets", "Add Entry", "Edit Entry"])

    # View Timesheets
    if action == "View Timesheets":
        st.title("📋 Timesheet Overview")
        st.button("🔄 Refresh Timesheets", on_click=get_timesheets)

        if st.session_state.timesheets:
            table = []
            for t in st.session_state.timesheets:
                row = {
                    "ID": t["id"],
                    "User ID": t["user_id"],
                    "Job Code ID": t["jobcode_id"],
                    "Date": t["date"],
                    "Duration": str(timedelta(seconds=t.get("duration", 0))),
                    "Type": t["type"].capitalize(),
                    "Notes": t["notes"]
                }
                table.append(row)

            st.dataframe(table, use_container_width=True)
        else:
            st.info("No timesheet data available.")

    # Add Entry
    elif action == "Add Entry":
        st.title("➕ Add New Timesheet Entry")

        with st.form("add_entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                user_id = st.number_input("User ID", min_value=1)
                jobcode_id = st.number_input("Job Code ID", min_value=1)
                entry_type = st.selectbox("Entry Type", ["regular", "manual"])
            with col2:
                entry_date = st.date_input("Entry Date")
                start_time = st.time_input("Start Time")
                end_time = st.time_input("End Time")

            notes = st.text_area("Notes")
            custom1 = st.text_input("Custom Field 1")
            custom2 = st.text_input("Custom Field 2")

            if st.form_submit_button("Submit Entry"):
                start_dt = datetime.combine(entry_date, start_time).isoformat()
                end_dt = datetime.combine(entry_date, end_time).isoformat()
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
                    st.success("✅ Entry created successfully.")
                    get_timesheets()
                else:
                    st.error("❌ Failed to create entry.")

    # Edit Entry
    elif action == "Edit Entry":
        st.title("✏️ Edit Timesheet Entry")

        if st.session_state.timesheets:
            ids = [t['id'] for t in st.session_state.timesheets]
            selected_id = st.selectbox("Select Entry ID", ids)
            selected = next(t for t in st.session_state.timesheets if t['id'] == selected_id)

            with st.form("edit_entry_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_user_id = st.number_input("User ID", value=selected['user_id'])
                    new_jobcode_id = st.number_input("Job Code ID", value=selected['jobcode_id'])
                    new_type = st.selectbox("Type", ["regular", "manual"],
                                            index=0 if selected['type'] == "regular" else 1)
                with col2:
                    new_start = st.text_input("Start Time", value=selected['start'])
                    new_end = st.text_input("End Time", value=selected['end'])

                new_notes = st.text_area("Notes", value=selected['notes'])
                new_custom1 = st.text_input("Custom Field 1", value=selected['customfields'].get("19142", ""))
                new_custom2 = st.text_input("Custom Field 2", value=selected['customfields'].get("19144", ""))

                if st.form_submit_button("Update Entry"):
                    updated_entry = {
                        "user_id": new_user_id,
                        "jobcode_id": new_jobcode_id,
                        "type": new_type,
                        "start": new_start,
                        "end": new_end,
                        "notes": new_notes,
                        "customfields": {
                            "19142": new_custom1,
                            "19144": new_custom2
                        }
                    }
                    response = update_timesheet(selected_id, updated_entry)
                    if response:
                        st.success("✅ Entry updated successfully.")
                        get_timesheets()
                    else:
                        st.error("❌ Failed to update entry.")
        else:
            st.info("No entries available to edit.")

else:
    st.info("Please authenticate via the sidebar to manage timesheets.")
