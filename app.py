import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

# Set page configuration
st.set_page_config(
    page_title="TSheets Manager",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .info-text {
        font-size: 1rem;
        color: #555;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    .stButton button {
        width: 100%;
    }
    .user-info {
        background-color: #e9ecef;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Constants
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBCODES_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"
CURRENT_USER_ENDPOINT = f"{BASE_URL}/current_user"

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_token' not in st.session_state:
    st.session_state.api_token = ""
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'jobcodes' not in st.session_state:
    st.session_state.jobcodes = {}
if 'timesheets' not in st.session_state:
    st.session_state.timesheets = []
if 'user_map' not in st.session_state:
    st.session_state.user_map = {}  # Map of user IDs to full names

# Helper Functions
def make_api_request(endpoint, method="GET", params=None, data=None):
    """Make an API request to TSheets"""
    headers = {
        "Authorization": f"Bearer {st.session_state.api_token}",
        "Content-Type": "application/json"
    }
    
    try:
        if method == "GET":
            response = requests.get(endpoint, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(endpoint, headers=headers, json=data)
        elif method == "PUT":
            response = requests.put(endpoint, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(endpoint, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.error(f"Request Error: {str(e)}")
        return None

def authenticate():
    """Authenticate with TSheets API"""
    response = make_api_request(CURRENT_USER_ENDPOINT)
    
    if response:
        st.session_state.authenticated = True
        # Extract current user info
        user_data = list(response['results']['users'].values())[0]
        st.session_state.current_user = user_data
        
        # Load initial data
        load_users()
        load_jobcodes()
        load_timesheets()
        return True
    else:
        st.session_state.authenticated = False
        return False

def load_users():
    """Load users from TSheets API"""
    response = make_api_request(USERS_ENDPOINT, params={"active": "yes"})
    
    if response:
        st.session_state.users = response['results']['users']
        
        # Create a mapping of user IDs to full names
        user_map = {}
        for user_id, user_data in st.session_state.users.items():
            full_name = f"{user_data['first_name']} {user_data['last_name']}"
            user_map[int(user_id)] = full_name
        
        st.session_state.user_map = user_map

def load_jobcodes():
    """Load jobcodes from TSheets API"""
    response = make_api_request(JOBCODES_ENDPOINT, params={"active": "yes"})
    
    if response:
        st.session_state.jobcodes = response['results']['jobcodes']

def load_timesheets():
    """Load timesheets from TSheets API"""
    # Get timesheets for the current user only
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    
    params = {
        "start_date": start_date,
        "end_date": end_date,
        "user_ids": st.session_state.current_user['id'],
        "supplemental_data": "yes"
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, params=params)
    
    if response and 'results' in response and 'timesheets' in response['results']:
        # Convert to list and sort by date (most recent first)
        timesheets = list(response['results']['timesheets'].values())
        timesheets.sort(key=lambda x: x['date'], reverse=True)
        st.session_state.timesheets = timesheets

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_jobcode_name(jobcode_id):
    """Get jobcode name from jobcode ID"""
    jobcode_id = int(jobcode_id)
    if str(jobcode_id) in st.session_state.jobcodes:
        return st.session_state.jobcodes[str(jobcode_id)]['name']
    return f"Job {jobcode_id}"

def get_user_name(user_id):
    """Get user full name from user ID"""
    user_id = int(user_id)
    if user_id in st.session_state.user_map:
        return st.session_state.user_map[user_id]
    return f"User {user_id}"

def create_timesheet(data):
    """Create a new timesheet entry"""
    payload = {
        "data": [data]
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="POST", data=payload)
    
    if response and 'results' in response:
        st.success("Timesheet entry created successfully!")
        # Reload timesheets to show the new entry
        load_timesheets()
        return True
    return False

def update_timesheet(timesheet_id, data):
    """Update an existing timesheet entry"""
    payload = {
        "data": [{
            "id": timesheet_id,
            **data
        }]
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="PUT", data=payload)
    
    if response and 'results' in response:
        st.success("Timesheet entry updated successfully!")
        # Reload timesheets to show the updated entry
        load_timesheets()
        return True
    return False

def delete_timesheet(timesheet_id):
    """Delete a timesheet entry"""
    payload = {
        "data": [{
            "id": timesheet_id
        }]
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="DELETE", data=payload)
    
    if response and 'results' in response:
        st.success("Timesheet entry deleted successfully!")
        # Reload timesheets to show the changes
        load_timesheets()
        return True
    return False

# Sidebar - Authentication
with st.sidebar:
    st.title("TSheets Manager")
    
    if not st.session_state.authenticated:
        st.subheader("Authentication")
        api_token = st.text_input("API Token", type="password")
        
        if st.button("Login"):
            if api_token:
                st.session_state.api_token = api_token
                with st.spinner("Authenticating..."):
                    if authenticate():
                        st.success("Authentication successful!")
                        st.experimental_rerun()
                    else:
                        st.error("Authentication failed. Please check your API token.")
            else:
                st.error("Please enter an API token.")
    else:
        # Display current user info
        st.subheader("User Information")
        user_info = st.session_state.current_user
        st.markdown(f"""
        <div class="user-info">
            <p><strong>Name:</strong> {user_info['first_name']} {user_info['last_name']}</p>
            <p><strong>Email:</strong> {user_info['email'] or 'N/A'}</p>
            <p><strong>Company:</strong> {user_info['company_name']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.subheader("Navigation")
        action = st.radio("Select Action", ["View Timesheets", "Add Entry", "Edit Entry"])
        
        # Logout button
        if st.button("Logout"):
            for key in st.session_state.keys():
                del st.session_state[key]
            st.experimental_rerun()
        
        # Refresh button
        if st.button("Refresh Data"):
            with st.spinner("Refreshing data..."):
                load_users()
                load_jobcodes()
                load_timesheets()
                st.success("Data refreshed!")

# Main content
if not st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Welcome to TSheets Manager</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p class="info-text">Please login using your TSheets API token to access the application.</p>
    <p class="info-text">You can find your API token in your TSheets account settings.</p>
    """, unsafe_allow_html=True)
    
    # Sample image or logo
    st.image("https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=200", width=200)
else:
    # Get the selected action from the sidebar
    action = st.session_state.get("action", "View Timesheets")
    
    # View Timesheets
    if action == "View Timesheets":
        st.markdown('<h1 class="main-header">Your Timesheets</h1>', unsafe_allow_html=True)
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        with col1:
            search_term = st.text_input("Search by notes", "")
        with col2:
            job_filter = st.selectbox(
                "Filter by Job",
                ["All"] + [job['name'] for job in st.session_state.jobcodes.values()]
            )
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(
                    datetime.now() - timedelta(days=30),
                    datetime.now()
                )
            )
        
        # Apply filters
        filtered_timesheets = st.session_state.timesheets
        
        # Search filter
        if search_term:
            filtered_timesheets = [
                ts for ts in filtered_timesheets
                if search_term.lower() in (ts.get('notes', '') or '').lower()
            ]
        
        # Job filter
        if job_filter != "All":
            job_id = None
            for jid, job in st.session_state.jobcodes.items():
                if job['name'] == job_filter:
                    job_id = int(jid)
                    break
            
            if job_id:
                filtered_timesheets = [
                    ts for ts in filtered_timesheets
                    if ts['jobcode_id'] == job_id
                ]
        
        # Date filter
        if len(date_range) == 2:
            start_date, end_date = date_range
            filtered_timesheets = [
                ts for ts in filtered_timesheets
                if start_date <= datetime.strptime(ts['date'], "%Y-%m-%d").date() <= end_date
            ]
        
        # Display timesheets
        if filtered_timesheets:
            # Calculate total hours
            total_seconds = sum(ts['duration'] for ts in filtered_timesheets)
            st.markdown(f"**Total Hours:** {format_duration(total_seconds)}")
            
            # Create a DataFrame for better display
            timesheet_data = []
            for ts in filtered_timesheets:
                # Format dates and times
                date = datetime.strptime(ts['date'], "%Y-%m-%d").strftime("%b %d, %Y")
                start_time = datetime.fromisoformat(ts['start'].replace('Z', '+00:00')).strftime("%H:%M:%S")
                end_time = datetime.fromisoformat(ts['end'].replace('Z', '+00:00')).strftime("%H:%M:%S")
                
                timesheet_data.append({
                    "ID": ts['id'],
                    "Date": date,
                    "User": get_user_name(ts['user_id']),
                    "Job": get_jobcode_name(ts['jobcode_id']),
                    "Start": start_time,
                    "End": end_time,
                    "Duration": format_duration(ts['duration']),
                    "Type": ts['type'].capitalize(),
                    "Notes": ts.get('notes', '')
                })
            
            df = pd.DataFrame(timesheet_data)
            st.dataframe(df, use_container_width=True)
            
            # Allow deletion of timesheet entries
            with st.expander("Delete Timesheet Entry"):
                timesheet_id = st.selectbox(
                    "Select Timesheet Entry to Delete",
                    options=[ts['id'] for ts in filtered_timesheets],
                    format_func=lambda x: f"ID: {x} - {get_jobcode_name(next(ts['jobcode_id'] for ts in filtered_timesheets if ts['id'] == x))} ({next(datetime.strptime(ts['date'], '%Y-%m-%d').strftime('%b %d, %Y') for ts in filtered_timesheets if ts['id'] == x)})"
                )
                
                if st.button("Delete Selected Entry", key="delete_button"):
                    if st.session_state.current_user:
                        with st.spinner("Deleting timesheet entry..."):
                            if delete_timesheet(timesheet_id):
                                st.success("Timesheet entry deleted successfully!")
                                time.sleep(1)
                                st.experimental_rerun()
        else:
            st.info("No timesheet entries found for the selected filters.")
    
    # Add Entry
    elif action == "Add Entry":
        st.markdown('<h1 class="main-header">Add Timesheet Entry</h1>', unsafe_allow_html=True)
        
        with st.form("add_timesheet_form"):
            # User is fixed to current user
            st.markdown(f"**User:** {st.session_state.current_user['first_name']} {st.session_state.current_user['last_name']}")
            
            # Job selection
            jobcode_options = {jid: job['name'] for jid, job in st.session_state.jobcodes.items()}
            jobcode_id = st.selectbox(
                "Job Code",
                options=list(jobcode_options.keys()),
                format_func=lambda x: jobcode_options[x]
            )
            
            # Date and time inputs
            col1, col2 = st.columns(2)
            with col1:
                date = st.date_input("Date", value=datetime.now())
            
            with col2:
                entry_type = st.selectbox("Entry Type", ["regular", "manual"])
            
            col3, col4 = st.columns(2)
            with col3:
                start_time = st.time_input("Start Time", value=datetime.now().replace(hour=9, minute=0, second=0))
            
            with col4:
                end_time = st.time_input("End Time", value=datetime.now().replace(hour=17, minute=0, second=0))
            
            # Notes and custom fields
            notes = st.text_area("Notes", "")
            
            col5, col6 = st.columns(2)
            with col5:
                custom_field1 = st.text_input("Custom Field 1", "")
            
            with col6:
                custom_field2 = st.text_input("Custom Field 2", "")
            
            # Submit button
            submit_button = st.form_submit_button("Submit")
            
            if submit_button:
                # Validate inputs
                if not jobcode_id:
                    st.error("Please select a job code.")
                elif start_time >= end_time:
                    st.error("End time must be after start time.")
                else:
                    # Format date and times for API
                    date_str = date.strftime("%Y-%m-%d")
                    start_datetime = datetime.combine(date, start_time).isoformat()
                    end_datetime = datetime.combine(date, end_time).isoformat()
                    
                    # Calculate duration in seconds
                    duration = int((datetime.combine(date, end_time) - datetime.combine(date, start_time)).total_seconds())
                    
                    # Prepare data for API
                    timesheet_data = {
                        "user_id": st.session_state.current_user['id'],
                        "jobcode_id": int(jobcode_id),
                        "type": entry_type,
                        "date": date_str,
                        "start": start_datetime,
                        "end": end_datetime,
                        "duration": duration,
                        "notes": notes,
                        "customfields": {
                            "19142": custom_field1,
                            "19144": custom_field2
                        }
                    }
                    
                    with st.spinner("Creating timesheet entry..."):
                        if create_timesheet(timesheet_data):
                            st.success("Timesheet entry created successfully!")
                            time.sleep(1)
                            st.experimental_rerun()
    
    # Edit Entry
    elif action == "Edit Entry":
        st.markdown('<h1 class="main-header">Edit Timesheet Entry</h1>', unsafe_allow_html=True)
        
        # Select timesheet entry to edit
        timesheet_options = {
            ts['id']: f"{datetime.strptime(ts['date'], '%Y-%m-%d').strftime('%b %d, %Y')} - {get_jobcode_name(ts['jobcode_id'])}"
            for ts in st.session_state.timesheets
        }
        
        if timesheet_options:
            selected_timesheet_id = st.selectbox(
                "Select Timesheet Entry to Edit",
                options=list(timesheet_options.keys()),
                format_func=lambda x: timesheet_options[x]
            )
            
            # Get the selected timesheet
            selected_timesheet = next((ts for ts in st.session_state.timesheets if ts['id'] == selected_timesheet_id), None)
            
            if selected_timesheet:
                with st.form("edit_timesheet_form"):
                    # User is fixed to current user
                    st.markdown(f"**User:** {st.session_state.current_user['first_name']} {st.session_state.current_user['last_name']}")
                    
                    # Job selection
                    jobcode_options = {jid: job['name'] for jid, job in st.session_state.jobcodes.items()}
                    jobcode_id = st.selectbox(
                        "Job Code",
                        options=list(jobcode_options.keys()),
                        format_func=lambda x: jobcode_options[x],
                        index=list(jobcode_options.keys()).index(str(selected_timesheet['jobcode_id'])) if str(selected_timesheet['jobcode_id']) in jobcode_options else 0
                    )
                    
                    # Date and time inputs
                    col1, col2 = st.columns(2)
                    with col1:
                        date = st.date_input(
                            "Date",
                            value=datetime.strptime(selected_timesheet['date'], "%Y-%m-%d")
                        )
                    
                    with col2:
                        entry_type = st.selectbox(
                            "Entry Type",
                            ["regular", "manual"],
                            index=0 if selected_timesheet['type'] == "regular" else 1
                        )
                    
                    # Parse start and end times
                    start_datetime = datetime.fromisoformat(selected_timesheet['start'].replace('Z', '+00:00'))
                    end_datetime = datetime.fromisoformat(selected_timesheet['end'].replace('Z', '+00:00'))
                    
                    col3, col4 = st.columns(2)
                    with col3:
                        start_time = st.time_input("Start Time", value=start_datetime.time())
                    
                    with col4:
                        end_time = st.time_input("End Time", value=end_datetime.time())
                    
                    # Notes and custom fields
                    notes = st.text_area("Notes", selected_timesheet.get('notes', ''))
                    
                    # Get custom fields if they exist
                    custom_fields = selected_timesheet.get('customfields', {})
                    
                    col5, col6 = st.columns(2)
                    with col5:
                        custom_field1 = st.text_input("Custom Field 1", custom_fields.get('19142', ''))
                    
                    with col6:
                        custom_field2 = st.text_input("Custom Field 2", custom_fields.get('19144', ''))
                    
                    # Submit button
                    submit_button = st.form_submit_button("Update")
                    
                    if submit_button:
                        # Validate inputs
                        if not jobcode_id:
                            st.error("Please select a job code.")
                        elif start_time >= end_time:
                            st.error("End time must be after start time.")
                        else:
                            # Format date and times for API
                            date_str = date.strftime("%Y-%m-%d")
                            start_datetime = datetime.combine(date, start_time).isoformat()
                            end_datetime = datetime.combine(date, end_time).isoformat()
                            
                            # Calculate duration in seconds
                            duration = int((datetime.combine(date, end_time) - datetime.combine(date, start_time)).total_seconds())
                            
                            # Prepare data for API
                            timesheet_data = {
                                "user_id": st.session_state.current_user['id'],
                                "jobcode_id": int(jobcode_id),
                                "type": entry_type,
                                "date": date_str,
                                "start": start_datetime,
                                "end": end_datetime,
                                "duration": duration,
                                "notes": notes,
                                "customfields": {
                                    "19142": custom_field1,
                                    "19144": custom_field2
                                }
                            }
                            
                            with st.spinner("Updating timesheet entry..."):
                                if update_timesheet(selected_timesheet_id, timesheet_data):
                                    st.success("Timesheet entry updated successfully!")
                                    time.sleep(1)
                                    st.experimental_rerun()
            else:
                st.error("Selected timesheet entry not found.")
        else:
            st.info("No timesheet entries available to edit.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        <p>TSheets Manager v2.0 | Developed with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
