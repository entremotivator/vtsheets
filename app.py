import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime, timedelta, date
import time
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import calendar
import re

# Set page configuration
st.set_page_config(
    page_title="TSheets CRM Manager",
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
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
    }
    .client-card {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }
    .client-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e9ecef;
        border-bottom: 2px solid #4CAF50;
    }
    .metric-card {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        text-align: center;
        height: 100%;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .metric-label {
        font-size: 1rem;
        color: #555;
    }
    .download-link {
        text-decoration: none;
        color: white;
        background-color: #4CAF50;
        padding: 10px 15px;
        border-radius: 5px;
        text-align: center;
        display: inline-block;
        margin-top: 10px;
    }
    .download-link:hover {
        background-color: #45a049;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    .client-profile {
        background-color: white;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .client-profile h3 {
        color: #2C3E50;
        border-bottom: 1px solid #eee;
        padding-bottom: 10px;
        margin-bottom: 15px;
    }
    .client-profile-section {
        margin-bottom: 15px;
    }
    .client-profile-section h4 {
        color: #34495E;
        margin-bottom: 10px;
    }
    .client-contact {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
    }
    .client-contact-icon {
        margin-right: 10px;
        color: #3498DB;
    }
    .timesheet-detail {
        background-color: #f8f9fa;
        border-left: 3px solid #4CAF50;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 5px 5px 0;
    }
    .timesheet-date {
        font-weight: bold;
        color: #2C3E50;
    }
    .timesheet-duration {
        font-weight: bold;
        color: #4CAF50;
    }
    .timesheet-job {
        color: #3498DB;
    }
    .timesheet-notes {
        font-style: italic;
        color: #7F8C8D;
        margin-top: 5px;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .status-active {
        background-color: #d4edda;
        color: #155724;
    }
    .status-inactive {
        background-color: #f8d7da;
        color: #721c24;
    }
    .status-pending {
        background-color: #fff3cd;
        color: #856404;
    }
    .avatar {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 15px;
    }
    .client-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 15px;
    }
    .client-stat {
        text-align: center;
        flex: 1;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin: 0 5px;
    }
    .client-stat-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .client-stat-label {
        font-size: 0.8rem;
        color: #555;
    }
    .activity-timeline {
        position: relative;
        margin-left: 20px;
    }
    .activity-timeline:before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        width: 2px;
        height: 100%;
        background-color: #e9ecef;
    }
    .activity-item {
        position: relative;
        padding-left: 30px;
        margin-bottom: 20px;
    }
    .activity-item:before {
        content: '';
        position: absolute;
        left: -5px;
        top: 0;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        background-color: #4CAF50;
    }
    .activity-date {
        font-size: 0.8rem;
        color: #7F8C8D;
    }
    .activity-content {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        margin-top: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Constants
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBCODES_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"
CURRENT_USER_ENDPOINT = f"{BASE_URL}/current_user"
CLIENTS_ENDPOINT = f"{BASE_URL}/customfields"  # Using customfields for client data

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
if 'clients' not in st.session_state:
    st.session_state.clients = []
if 'user_map' not in st.session_state:
    st.session_state.user_map = {}  # Map of user IDs to full names
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if 'date_range' not in st.session_state:
    # Default to last 30 days from current date
    today = datetime.now().date()
    st.session_state.date_range = (
        today - timedelta(days=30),
        today
    )
if 'error_message' not in st.session_state:
    st.session_state.error_message = None
if 'success_message' not in st.session_state:
    st.session_state.success_message = None
if 'debug_info' not in st.session_state:
    st.session_state.debug_info = None
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None
if 'client_search' not in st.session_state:
    st.session_state.client_search = ""

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
        
        # Store debug info for troubleshooting
        if endpoint == TIMESHEETS_ENDPOINT and method == "GET":
            st.session_state.debug_info = {
                "endpoint": endpoint,
                "params": params,
                "status_code": response.status_code
            }
            
        if response.status_code == 200:
            return response.json()
        else:
            st.session_state.error_message = f"API Error: {response.status_code} - {response.text}"
            return None
    except Exception as e:
        st.session_state.error_message = f"Request Error: {str(e)}"
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
        load_clients()
        st.session_state.last_refresh = datetime.now()
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
    # Ensure dates are in the correct format and not in the future
    today = datetime.now().date()
    
    # Make sure end date is not in the future
    end_date = min(st.session_state.date_range[1], today)
    
    # Make sure start date is not after end date
    start_date = min(st.session_state.date_range[0], end_date)
    
    # Format dates for API
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    params = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "user_ids": st.session_state.current_user['id'],
        "supplemental_data": "yes"
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, params=params)
    
    if response and 'results' in response and 'timesheets' in response['results']:
        # Convert to list and sort by date (most recent first)
        timesheets = list(response['results']['timesheets'].values())
        timesheets.sort(key=lambda x: x['date'], reverse=True)
        st.session_state.timesheets = timesheets
    else:
        # If no timesheets found or error, set to empty list
        st.session_state.timesheets = []

def load_clients():
    """Load clients from TSheets API (using customfields as a proxy)"""
    # In a real implementation, you would fetch clients from your CRM system
    # For this example, we'll create mock client data
    
    # Mock client data
    clients = [
        {
            "id": 1001,
            "name": "Acme Corporation",
            "contact": "John Doe",
            "email": "john.doe@acme.com",
            "phone": "555-123-4567",
            "address": "123 Main St, Anytown, USA",
            "status": "active",
            "industry": "Technology",
            "notes": "Key client for software development projects",
            "created_date": "2023-01-15",
            "last_contact": "2023-04-28",
            "projects": ["Website Redesign", "Mobile App Development"],
            "total_hours": 245.5,
            "billing_rate": 150,
            "avatar": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        },
        {
            "id": 1002,
            "name": "Globex Industries",
            "contact": "Jane Smith",
            "email": "jane.smith@globex.com",
            "phone": "555-987-6543",
            "address": "456 Oak Ave, Somewhere, USA",
            "status": "active",
            "industry": "Manufacturing",
            "notes": "Ongoing maintenance contract",
            "created_date": "2022-11-03",
            "last_contact": "2023-05-02",
            "projects": ["Inventory System", "Quality Control App"],
            "total_hours": 187.25,
            "billing_rate": 125,
            "avatar": "https://www.gravatar.com/avatar/11111111111111111111111111111111?d=mp&f=y"
        },
        {
            "id": 1003,
            "name": "Initech LLC",
            "contact": "Michael Bolton",
            "email": "michael.bolton@initech.com",
            "phone": "555-555-5555",
            "address": "789 Pine St, Elsewhere, USA",
            "status": "inactive",
            "industry": "Finance",
            "notes": "Contract on hold pending budget approval",
            "created_date": "2022-08-22",
            "last_contact": "2023-03-15",
            "projects": ["Financial Dashboard", "Reporting Tool"],
            "total_hours": 92.75,
            "billing_rate": 175,
            "avatar": "https://www.gravatar.com/avatar/22222222222222222222222222222222?d=mp&f=y"
        },
        {
            "id": 1004,
            "name": "Stark Industries",
            "contact": "Tony Stark",
            "email": "tony@stark.com",
            "phone": "555-IRON-MAN",
            "address": "Stark Tower, New York, USA",
            "status": "active",
            "industry": "Technology",
            "notes": "High-priority client with multiple ongoing projects",
            "created_date": "2022-05-10",
            "last_contact": "2023-05-07",
            "projects": ["Clean Energy", "Advanced Robotics", "AI Development"],
            "total_hours": 412.5,
            "billing_rate": 250,
            "avatar": "https://www.gravatar.com/avatar/33333333333333333333333333333333?d=mp&f=y"
        },
        {
            "id": 1005,
            "name": "Wayne Enterprises",
            "contact": "Bruce Wayne",
            "email": "bruce@wayne.com",
            "phone": "555-BAT-CAVE",
            "address": "Wayne Tower, Gotham City, USA",
            "status": "active",
            "industry": "Defense",
            "notes": "Requires strict confidentiality",
            "created_date": "2022-07-18",
            "last_contact": "2023-04-30",
            "projects": ["Security Systems", "Urban Development"],
            "total_hours": 287.75,
            "billing_rate": 200,
            "avatar": "https://www.gravatar.com/avatar/44444444444444444444444444444444?d=mp&f=y"
        }
    ]
    
    st.session_state.clients = clients

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_duration_hours(seconds):
    """Format duration in seconds to decimal hours"""
    hours = seconds / 3600
    return f"{hours:.2f}"

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
        st.session_state.success_message = "Timesheet entry created successfully!"
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
        st.session_state.success_message = "Timesheet entry updated successfully!"
        # Reload timesheets to show the updated entry
        load_timesheets()
        return True
    return False

def delete_timesheet(timesheet_id):
    """Delete a timesheet entry"""
    response = make_api_request(f"{TIMESHEETS_ENDPOINT}?ids={timesheet_id}", method="DELETE")
    
    if response and 'results' in response:
        st.session_state.success_message = "Timesheet entry deleted successfully!"
        # Reload timesheets to show the changes
        load_timesheets()
        return True
    return False

def get_timesheet_dataframe(timesheets):
    """Convert timesheet data to a DataFrame for analysis"""
    if not timesheets:
        return pd.DataFrame()
    
    data = []
    for ts in timesheets:
        try:
            # Format dates and times
            entry_date = datetime.strptime(ts['date'], "%Y-%m-%d")
            
            # Handle different timesheet types
            if ts['type'] == 'regular':
                start_time = datetime.fromisoformat(ts['start'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(ts['end'].replace('Z', '+00:00')) if ts['end'] else None
            else:  # manual timesheet
                start_time = None
                end_time = None
            
            data.append({
                "id": ts['id'],
                "date": entry_date,
                "date_str": entry_date.strftime("%b %d, %Y"),
                "day_of_week": entry_date.strftime("%A"),
                "week_number": entry_date.isocalendar()[1],
                "month": entry_date.strftime("%B"),
                "year": entry_date.year,
                "user_id": ts['user_id'],
                "user_name": get_user_name(ts['user_id']),
                "jobcode_id": ts['jobcode_id'],
                "job_name": get_jobcode_name(ts['jobcode_id']),
                "start_time": start_time,
                "end_time": end_time,
                "duration_seconds": ts['duration'],
                "duration_hours": ts['duration'] / 3600,
                "duration_formatted": format_duration(ts['duration']),
                "type": ts['type'].capitalize(),
                "notes": ts.get('notes', ''),
                "on_the_clock": ts.get('on_the_clock', False)
            })
        except Exception as e:
            # Skip entries with invalid data
            st.session_state.error_message = f"Error processing timesheet entry: {str(e)}"
            continue
    
    return pd.DataFrame(data)

def generate_dashboard_metrics(df):
    """Generate metrics for the dashboard"""
    if df.empty:
        return {
            "total_hours": "0:00:00",
            "total_hours_decimal": "0.00",
            "avg_daily_hours": "0.00",
            "days_worked": 0,
            "most_common_job": "N/A",
            "billable_hours": "0.00",
            "non_billable_hours": "0.00"
        }
    
    total_seconds = df['duration_seconds'].sum()
    days_worked = df['date'].nunique()
    
    # Calculate average daily hours (only for days worked)
    avg_daily_seconds = total_seconds / days_worked if days_worked > 0 else 0
    
    # Get most common job
    if not df.empty:
        job_counts = df['job_name'].value_counts()
        most_common_job = job_counts.index[0] if not job_counts.empty else "N/A"
    else:
        most_common_job = "N/A"
    
    # Calculate billable vs non-billable hours (mock data for this example)
    billable_seconds = total_seconds * 0.75  # Assuming 75% billable for this example
    non_billable_seconds = total_seconds * 0.25
    
    return {
        "total_hours": format_duration(total_seconds),
        "total_hours_decimal": format_duration_hours(total_seconds),
        "avg_daily_hours": format_duration_hours(avg_daily_seconds),
        "days_worked": days_worked,
        "most_common_job": most_common_job,
        "billable_hours": format_duration_hours(billable_seconds),
        "non_billable_hours": format_duration_hours(non_billable_seconds)
    }

def generate_weekly_report(df):
    """Generate weekly report data"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by week and calculate total hours
    weekly_data = df.groupby(['year', 'week_number']).agg({
        'duration_seconds': 'sum',
        'date': 'min'  # Get the first day of each week
    }).reset_index()
    
    # Format the data
    weekly_data['week_ending'] = weekly_data['date'].apply(
        lambda x: (x + timedelta(days=6 - x.weekday())).strftime("%b %d, %Y")
    )
    weekly_data['week_starting'] = weekly_data['date'].apply(
        lambda x: x.strftime("%b %d, %Y")
    )
    weekly_data['week_label'] = weekly_data.apply(
        lambda x: f"Week {x['week_number']} ({x['week_starting']} - {x['week_ending']})",
        axis=1
    )
    weekly_data['hours'] = weekly_data['duration_seconds'] / 3600
    weekly_data['hours_formatted'] = weekly_data['duration_seconds'].apply(format_duration)
    
    return weekly_data.sort_values(by=['year', 'week_number'], ascending=False)

def generate_job_summary(df):
    """Generate job summary data"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by job and calculate total hours
    job_data = df.groupby('job_name').agg({
        'duration_seconds': 'sum',
        'id': 'count'
    }).reset_index()
    
    # Rename columns
    job_data.columns = ['Job', 'Total Seconds', 'Entry Count']
    
    # Add formatted hours
    job_data['Hours'] = job_data['Total Seconds'] / 3600
    job_data['Hours Formatted'] = job_data['Total Seconds'].apply(format_duration)
    
    # Calculate percentage
    total_seconds = job_data['Total Seconds'].sum()
    job_data['Percentage'] = (job_data['Total Seconds'] / total_seconds * 100).round(2)
    
    return job_data.sort_values(by='Total Seconds', ascending=False)

def generate_daily_summary(df):
    """Generate daily summary data"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by date and calculate total hours
    daily_data = df.groupby(['date', 'date_str', 'day_of_week']).agg({
        'duration_seconds': 'sum',
        'id': 'count'
    }).reset_index()
    
    # Rename columns
    daily_data.columns = ['Date', 'Date String', 'Day of Week', 'Total Seconds', 'Entry Count']
    
    # Add formatted hours
    daily_data['Hours'] = daily_data['Total Seconds'] / 3600
    daily_data['Hours Formatted'] = daily_data['Total Seconds'].apply(format_duration)
    
    return daily_data.sort_values(by='Date', ascending=False)

def generate_client_timesheet_summary(df, client_id=None):
    """Generate timesheet summary for a specific client"""
    if df.empty:
        return pd.DataFrame()
    
    # In a real implementation, you would filter by client ID
    # For this example, we'll just return the data as is
    return df

def get_download_link(df, filename, link_text):
    """Generate a download link for a DataFrame"""
    if df.empty:
        return "No data to download"
    
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
    return href

def get_excel_download_link(df, filename, link_text):
    """Generate a download link for a DataFrame as Excel"""
    if df.empty:
        return "No data to download"
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    
    excel_data = output.getvalue()
    b64 = base64.b64encode(excel_data).decode()
    href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
    return href

def get_date_range_presets():
      class="download-link">{link_text}</a>'
    return href

def get_date_range_presets():
    """Get predefined date range options"""
    today = datetime.now().date()
    
    return {
        "Today": (today, today),
        "Yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "Last 7 Days": (today - timedelta(days=6), today),
        "Last 14 Days": (today - timedelta(days=13), today),
        "Last 30 Days": (today - timedelta(days=29), today),
        "This Week": (today - timedelta(days=today.weekday()), today),
        "Last Week": (
            today - timedelta(days=today.weekday() + 7),
            today - timedelta(days=today.weekday() + 1)
        ),
        "This Month": (today.replace(day=1), today),
        "Last Month": (
            (today.replace(day=1) - timedelta(days=1)).replace(day=1),
            today.replace(day=1) - timedelta(days=1)
        ),
        "This Quarter": (
            datetime(today.year, ((today.month-1)//3)*3+1, 1).date(),
            today
        ),
    }

def search_clients(query, clients):
    """Search clients by name, contact, or email"""
    if not query:
        return clients
    
    query = query.lower()
    results = []
    
    for client in clients:
        if (query in client['name'].lower() or 
            query in client['contact'].lower() or 
            query in client['email'].lower()):
            results.append(client)
    
    return results

def get_client_by_id(client_id):
    """Get client by ID"""
    for client in st.session_state.clients:
        if client['id'] == client_id:
            return client
    return None

def get_client_timesheets(client_id):
    """Get timesheets for a specific client"""
    # In a real implementation, you would filter timesheets by client ID
    # For this example, we'll just return a subset of timesheets as a mock
    if not st.session_state.timesheets:
        return []
    
    # Mock implementation - return a subset of timesheets based on client ID
    # In a real app, you would filter by a client_id field in the timesheet
    client_index = client_id % 5  # Use modulo to distribute timesheets
    return [ts for i, ts in enumerate(st.session_state.timesheets) if i % 5 == client_index]

# Sidebar - Authentication
with st.sidebar:
    st.title("TSheets CRM Manager")
    
    if not st.session_state.authenticated:
        st.subheader("Authentication")
        api_token = st.text_input("API Token", type="password")
        
        if st.button("Login"):
            if api_token:
                st.session_state.api_token = api_token
                with st.spinner("Authenticating..."):
                    if authenticate():
                        st.success("Authentication successful!")
                        st.session_state.active_tab = "Dashboard"
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
            <p><strong>Company:</strong> {user_info.get('company_name', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Date range selector
        st.subheader("Date Range")
        
        # Preset date ranges
        date_presets = get_date_range_presets()
        preset_options = list(date_presets.keys())
        preset_options.append("Custom")
        
        selected_preset = st.selectbox("Select Date Range", preset_options)
        
        if selected_preset == "Custom":
            # Custom date range picker
            date_range = st.date_input(
                "Custom Date Range",
                value=st.session_state.date_range,
                min_value=date(2000, 1, 1),
                max_value=datetime.now().date()
            )
            
            if len(date_range) == 2 and date_range != st.session_state.date_range:
                st.session_state.date_range = date_range
                # Reload timesheets with new date range
                load_timesheets()
        else:
            # Use preset date range
            if date_presets[selected_preset] != st.session_state.date_range:
                st.session_state.date_range = date_presets[selected_preset]
                # Reload timesheets with new date range
                load_timesheets()
        
        # Show current date range
        st.caption(f"Current range: {st.session_state.date_range[0]} to {st.session_state.date_range[1]}")
        
        # Navigation
        st.subheader("Navigation")
        tabs = ["Dashboard", "Timesheets", "Clients", "Reports", "Settings"]
        selected_tab = st.radio("Select Section", tabs, index=tabs.index(st.session_state.active_tab))
        
        if selected_tab != st.session_state.active_tab:
            st.session_state.active_tab = selected_tab
            # Reset selected client when changing tabs
            if selected_tab != "Clients":
                st.session_state.selected_client = None
        
        # Refresh button
        if st.button("Refresh Data"):
            with st.spinner("Refreshing data..."):
                load_users()
                load_jobcodes()
                load_timesheets()
                load_clients()
                st.session_state.last_refresh = datetime.now()
                st.session_state.success_message = "Data refreshed successfully!"
        
        # Last refresh time
        if st.session_state.last_refresh:
            st.caption(f"Last refreshed: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Logout button
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.session_state.authenticated = False
            st.session_state.api_token = ""

# Display messages
if st.session_state.error_message:
    st.error(st.session_state.error_message)
    st.session_state.error_message = None

if st.session_state.success_message:
    st.success(st.session_state.success_message)
    st.session_state.success_message = None

# Main content
if not st.session_state.authenticated:
    st.markdown('<h1 class="main-header">Welcome to TSheets CRM Manager</h1>', unsafe_allow_html=True)
    st.markdown("""
    <p class="info-text">Please login using your TSheets API token to access the application.</p>
    <p class="info-text">You can find your API token in your TSheets account settings.</p>
    """, unsafe_allow_html=True)
    
    # Sample image or logo
    st.image("https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=200", width=200)
else:
    # Get the selected tab from the sidebar
    active_tab = st.session_state.active_tab
    
    # Convert timesheets to DataFrame for analysis
    df_timesheets = get_timesheet_dataframe(st.session_state.timesheets)
    
    # Dashboard
    if active_tab == "Dashboard":
        st.markdown('<h1 class="main-header">Dashboard</h1>', unsafe_allow_html=True)
        
        # Show date range in the main content area
        st.caption(f"Showing data for: {st.session_state.date_range[0]} to {st.session_state.date_range[1]}")
        
        if df_timesheets.empty:
            st.info(f"No timesheet data available for the selected date range. Try selecting a different date range or adding new entries.")
            
            # Debug info for troubleshooting
            if st.session_state.debug_info:
                with st.expander("Debug Information"):
                    st.json(st.session_state.debug_info)
        else:
            # Generate metrics
            metrics = generate_dashboard_metrics(df_timesheets)
            
            # Display metrics in cards
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['total_hours_decimal']}</div>
                    <div class="metric-label">Total Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['avg_daily_hours']}</div>
                    <div class="metric-label">Avg. Daily Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['days_worked']}</div>
                    <div class="metric-label">Days Worked</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['most_common_job']}</div>
                    <div class="metric-label">Most Common Job</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Second row of metrics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['billable_hours']}</div>
                    <div class="metric-label">Billable Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{metrics['non_billable_hours']}</div>
                    <div class="metric-label">Non-Billable Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Charts
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Hours by Job")
                
                # Create job summary data
                job_summary = generate_job_summary(df_timesheets)
                
                if not job_summary.empty:
                    fig = px.pie(
                        job_summary,
                        values='Hours',
                        names='Job',
                        title='Distribution of Hours by Job',
                        hover_data=['Hours Formatted', 'Entry Count', 'Percentage'],
                        labels={'Hours Formatted': 'Total Time', 'Entry Count': 'Number of Entries', 'Percentage': '% of Total'}
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No job data available")
            
            with col2:
                st.subheader("Hours by Day of Week")
                
                # Group by day of week
                if not df_timesheets.empty:
                    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                    day_data = df_timesheets.groupby('day_of_week').agg({
                        'duration_hours': 'sum',
                        'id': 'count'
                    }).reset_index()
                    
                    # Ensure all days are included
                    all_days = pd.DataFrame({'day_of_week': day_order})
                    day_data = pd.merge(all_days, day_data, on='day_of_week', how='left').fillna(0)
                    
                    # Sort by day order
                    day_data['day_order'] = day_data['day_of_week'].apply(lambda x: day_order.index(x))
                    day_data = day_data.sort_values('day_order')
                    
                    fig = px.bar(
                        day_data,
                        x='day_of_week',
                        y='duration_hours',
                        title='Hours by Day of Week',
                        labels={'day_of_week': 'Day', 'duration_hours': 'Hours', 'id': 'Entries'},
                        hover_data=['id'],
                        category_orders={"day_of_week": day_order}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No day data available")
            
            # Weekly trend
            st.subheader("Weekly Hours Trend")
            
            if not df_timesheets.empty:
                weekly_data = generate_weekly_report(df_timesheets)
                
                if not weekly_data.empty:
                    # Sort by year and week
                    weekly_data = weekly_data.sort_values(by=['year', 'week_number'])
                    
                    fig = px.line(
                        weekly_data,
                        x='week_label',
                        y='hours',
                        markers=True,
                        title='Weekly Hours Trend',
                        labels={'week_label': 'Week', 'hours': 'Hours'}
                    )
                    fig.update_layout(xaxis_title="Week", yaxis_title="Hours")
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No weekly data available")
            else:
                st.info("No timesheet data available")
            
            # Recent activity
            st.subheader("Recent Activity")
            
            if not df_timesheets.empty:
                recent_entries = df_timesheets.head(5)
                
                for _, entry in recent_entries.iterrows():
                    st.markdown(f"""
                    <div class="timesheet-detail">
                        <div class="timesheet-date">{entry['date_str']} ({entry['day_of_week']})</div>
                        <div class="timesheet-job">{entry['job_name']}</div>
                        <div class="timesheet-duration">Duration: {entry['duration_formatted']} ({entry['duration_hours']:.2f} hours)</div>
                        <div class="timesheet-notes">{entry['notes'] if entry['notes'] else 'No notes'}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity to display")
    
    # Timesheets
    elif active_tab == "Timesheets":
        st.markdown('<h1 class="main-header">Timesheet Management</h1>', unsafe_allow_html=True)
        
        # Create tabs for different timesheet functions
        timesheet_tabs = st.tabs(["View Timesheets", "Add Entry", "Edit Entry"])
        
        # View Timesheets
        with timesheet_tabs[0]:
            st.subheader("Your Timesheets")
            
            # Show date range in the main content area
            st.caption(f"Showing data for: {st.session_state.date_range[0]} to {st.session_state.date_range[1]}")
            
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
                sort_by = st.selectbox(
                    "Sort by",
                    ["Date (newest first)", "Date (oldest first)", "Duration (highest first)", "Duration (lowest first)"]
                )
            
            if df_timesheets.empty:
                st.info(f"No timesheet data available for the selected date range. Try selecting a different date range or adding new entries.")
                
                # Debug info for troubleshooting
                if st.session_state.debug_info:
                    with st.expander("Debug Information"):
                        st.json(st.session_state.debug_info)
            else:
                # Apply filters
                filtered_df = df_timesheets.copy()
                
                # Search filter
                if search_term:
                    filtered_df = filtered_df[filtered_df['notes'].str.contains(search_term, case=False, na=False)]
                
                # Job filter
                if job_filter != "All":
                    filtered_df = filtered_df[filtered_df['job_name'] == job_filter]
                
                # Apply sorting
                if sort_by == "Date (newest first)":
                    filtered_df = filtered_df.sort_values(by='date', ascending=False)
                elif sort_by == "Date (oldest first)":
                    filtered_df = filtered_df.sort_values(by='date', ascending=True)
                elif sort_by == "Duration (highest first)":
                    filtered_df = filtered_df.sort_values(by='duration_seconds', ascending=False)
                elif sort_by == "Duration (lowest first)":
                    filtered_df = filtered_df.sort_values(by='duration_seconds', ascending=True)
                
                # Display timesheets
                if not filtered_df.empty:
                    # Calculate total hours
                    total_seconds = filtered_df['duration_seconds'].sum()
                    
                    st.markdown(f"**Total Hours:** {format_duration(total_seconds)} ({format_duration_hours(total_seconds)} hours)")
                    
                    # Create a display DataFrame with only the columns we want to show
                    display_df = filtered_df[['date_str', 'day_of_week', 'job_name', 'start_time', 'end_time', 
                                             'duration_formatted', 'type', 'notes']].copy()
                    
                    # Rename columns for display
                    display_df.columns = ['Date', 'Day', 'Job', 'Start Time', 'End Time', 'Duration', 'Type', 'Notes']
                    
                    # Format datetime columns
                    display_df['Start Time'] = filtered_df['start_time'].apply(lambda x: x.strftime('%H:%M:%S') if x else 'N/A')
                    display_df['End Time'] = filtered_df['end_time'].apply(lambda x: x.strftime('%H:%M:%S') if x else 'N/A')
                    
                    # Display the DataFrame
                    st.dataframe(display_df, use_container_width=True)
                    
                    # Export options
                    st.subheader("Export Options")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(get_download_link(display_df, "timesheets.csv", "Download as CSV"), unsafe_allow_html=True)
                    with col2:
                        st.markdown(get_excel_download_link(display_df, "timesheets.xlsx", "Download as Excel"), unsafe_allow_html=True)
                    
                    # Allow deletion of timesheet entries
                    with st.expander("Delete Timesheet Entry"):
                        timesheet_options = {row['id']: f"{row['date_str']} - {row['job_name']} ({row['duration_formatted']})" 
                                            for _, row in filtered_df.iterrows()}
                        
                        timesheet_id = st.selectbox(
                            "Select Timesheet Entry to Delete",
                            options=list(timesheet_options.keys()),
                            format_func=lambda x: timesheet_options[x]
                        )
                        
                        if st.button("Delete Selected Entry", key="delete_button"):
                            if st.session_state.current_user:
                                with st.spinner("Deleting timesheet entry..."):
                                    if delete_timesheet(timesheet_id):
                                        st.session_state.success_message = "Timesheet entry deleted successfully!"
                                        st.rerun()
                else:
                    st.info("No timesheet entries found for the selected filters.")
        
        # Add Entry
        with timesheet_tabs[1]:
            st.subheader("Add Timesheet Entry")
            
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
                    entry_date = st.date_input("Date", value=datetime.now().date())
                
                with col2:
                    entry_type = st.selectbox("Entry Type", ["regular", "manual"])
                
                if entry_type == "regular":
                    col3, col4 = st.columns(2)
                    with col3:
                        start_time = st.time_input("Start Time", value=datetime.now().replace(hour=9, minute=0, second=0).time())
                    
                    with col4:
                        end_time = st.time_input("End Time", value=datetime.now().replace(hour=17, minute=0, second=0).time())
                else:  # manual entry
                    duration_hours = st.number_input("Duration (hours)", min_value=0.0, max_value=24.0, value=8.0, step=0.25)
                    duration_seconds = int(duration_hours * 3600)
                
                # Client selection (in a real app, this would be linked to the job)
                client_options = {client['id']: client['name'] for client in st.session_state.clients}
                client_id = st.selectbox(
                    "Client",
                    options=list(client_options.keys()),
                    format_func=lambda x: client_options[x]
                )
                
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
                    elif entry_type == "regular" and start_time >= end_time:
                        st.error("End time must be after start time.")
                    else:
                        # Format date and times for API
                        date_str = entry_date.strftime("%Y-%m-%d")
                        
                        if entry_type == "regular":
                            start_datetime = datetime.combine(entry_date, start_time).isoformat()
                            end_datetime = datetime.combine(entry_date, end_time).isoformat()
                            
                            # Calculate duration in seconds
                            duration = int((datetime.combine(entry_date, end_time) - datetime.combine(entry_date, start_time)).total_seconds())
                            
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
                        else:  # manual entry
                            timesheet_data = {
                                "user_id": st.session_state.current_user['id'],
                                "jobcode_id": int(jobcode_id),
                                "type": entry_type,
                                "date": date_str,
                                "duration": duration_seconds,
                                "notes": notes,
                                "customfields": {
                                    "19142": custom_field1,
                                    "19144": custom_field2
                                }
                            }
                        
                        with st.spinner("Creating timesheet entry..."):
                            if create_timesheet(timesheet_data):
                                st.session_state.success_message = "Timesheet entry created successfully!"
                                st.rerun()
        
        # Edit Entry
        with timesheet_tabs[2]:
            st.subheader("Edit Timesheet Entry")
            
            # Show date range in the main content area
            st.caption(f"Showing data for: {st.session_state.date_range[0]} to {st.session_state.date_range[1]}")
            
            if df_timesheets.empty:
                st.info(f"No timesheet data available for the selected date range. Try selecting a different date range or adding new entries.")
                
                # Debug info for troubleshooting
                if st.session_state.debug_info:
                    with st.expander("Debug Information"):
                        st.json(st.session_state.debug_info)
            else:
                # Select timesheet entry to edit
                timesheet_options = {row['id']: f"{row['date_str']} - {row['job_name']} ({row['duration_formatted']})" 
                                    for _, row in df_timesheets.iterrows()}
                
                selected_timesheet_id = st.selectbox(
                    "Select Timesheet Entry to Edit",
                    options=list(timesheet_options.keys()),
                    format_func=lambda x: timesheet_options[x]
                )
                
                # Get the selected timesheet
                selected_timesheet = df_timesheets[df_timesheets['id'] == selected_timesheet_id].iloc[0] if selected_timesheet_id else None
                
                if selected_timesheet is not None:
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
                            entry_date = st.date_input("Date", value=selected_timesheet['date'])
                        
                        with col2:
                            entry_type = st.selectbox(
                                "Entry Type",
                                ["regular", "manual"],
                                index=0 if selected_timesheet['type'] == "Regular" else 1
                            )
                        
                        if entry_type == "regular":
                            col3, col4 = st.columns(2)
                            with col3:
                                start_time = st.time_input(
                                    "Start Time", 
                                    value=selected_timesheet['start_time'].time() if selected_timesheet['start_time'] else datetime.now().time()
                                )
                            
                            with col4:
                                end_time = st.time_input(
                                    "End Time", 
                                    value=selected_timesheet['end_time'].time() if selected_timesheet['end_time'] else (datetime.now() + timedelta(hours=1)).time()
                                )
                        else:  # manual entry
                            duration_hours = st.number_input(
                                "Duration (hours)", 
                                min_value=0.0, 
                                max_value=24.0, 
                                value=selected_timesheet['duration_hours'],
                                step=0.25
                            )
                            duration_seconds = int(duration_hours * 3600)
                        
                        # Notes and custom fields
                        notes = st.text_area("Notes", selected_timesheet['notes'])
                        
                        # Get original timesheet to extract custom fields
                        original_ts = next((ts for ts in st.session_state.timesheets if ts['id'] == selected_timesheet_id), None)
                        custom_fields = original_ts.get('customfields', {}) if original_ts else {}
                        
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
                            elif entry_type == "regular" and start_time >= end_time:
                                st.error("End time must be after start time.")
                            else:
                                # Format date and times for API
                                date_str = entry_date.strftime("%Y-%m-%d")
                                
                                if entry_type == "regular":
                                    start_datetime = datetime.combine(entry_date, start_time).isoformat()
                                    end_datetime = datetime.combine(entry_date, end_time).isoformat()
                                    
                                    # Calculate duration in seconds
                                    duration = int((datetime.combine(entry_date, end_time) - datetime.combine(entry_date, start_time)).total_seconds())
                                    
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
                                else:  # manual entry
                                    timesheet_data = {
                                        "user_id": st.session_state.current_user['id'],
                                        "jobcode_id": int(jobcode_id),
                                        "type": entry_type,
                                        "date": date_str,
                                        "duration": duration_seconds,
                                        "notes": notes,
                                        "customfields": {
                                            "19142": custom_field1,
                                            "19144": custom_field2
                                        }
                                    }
                                
                                with st.spinner("Updating timesheet entry..."):
                                    if update_timesheet(selected_timesheet_id, timesheet_data):
                                        st.session_state.success_message = "Timesheet entry updated successfully!"
                                        st.rerun()
                else:
                    st.error("Selected timesheet entry not found.")
    
    # Clients
    elif active_tab == "Clients":
        if st.session_state.selected_client is None:
            st.markdown('<h1 class="main-header">Client Management</h1>', unsafe_allow_html=True)
            
            # Search and filter
            st.session_state.client_search = st.text_input("Search Clients", st.session_state.client_search)
            
            # Filter clients based on search
            filtered_clients = search_clients(st.session_state.client_search, st.session_state.clients)
            
            if not filtered_clients:
                st.info("No clients found matching your search criteria.")
            else:
                # Display clients in a grid
                cols = st.columns(3)
                for i, client in enumerate(filtered_clients):
                    with cols[i % 3]:
                        st.markdown(f"""
                        <div class="client-card">
                            <h3>{client['name']}</h3>
                            <p><strong>Contact:</strong> {client['contact']}</p>
                            <p><strong>Email:</strong> {client['email']}</p>
                            <p><strong>Status:</strong> <span class="status-badge status-{client['status']}">{client['status'].upper()}</span></p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"View Profile", key=f"view_{client['id']}"):
                            st.session_state.selected_client = client['id']
                            st.rerun()
        else:
            # Display client profile
            client = get_client_by_id(st.session_state.selected_client)
            
            if client:
                # Back button
                if st.button("← Back to Clients"):
                    st.session_state.selected_client = None
                    st.rerun()
                
                st.markdown(f'<h1 class="main-header">Client Profile: {client["name"]}</h1>', unsafe_allow_html=True)
                
                # Client profile layout
                col1, col2 = st.columns([1, 2])
                
                with col1:
                    st.image(client['avatar'], width=150)
                    
                    st.markdown(f"""
                    <div class="client-profile-section">
                        <h4>Contact Information</h4>
                        <p><strong>Contact:</strong> {client['contact']}</p>
                        <p><strong>Email:</strong> {client['email']}</p>
                        <p><strong>Phone:</strong> {client['phone']}</p>
                    </div>
                    
                    <div class="client-profile-section">
                        <h4>Status</h4>
                        <p><span class="status-badge status-{client['status']}">{client['status'].upper()}</span></p>
                    </div>
                    
                    <div class="client-profile-section">
                        <h4>Industry</h4>
                        <p>{client['industry']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Client stats
                    st.markdown("""
                    <div class="client-profile-section">
                        <h4>Client Statistics</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    stat_cols = st.columns(3)
                    with stat_cols[0]:
                        st.markdown(f"""
                        <div class="client-stat">
                            <div class="client-stat-value">{client['total_hours']}</div>
                            <div class="client-stat-label">Total Hours</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with stat_cols[1]:
                        st.markdown(f"""
                        <div class="client-stat">
                            <div class="client-stat-value">${client['billing_rate']}</div>
                            <div class="client-stat-label">Hourly Rate</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with stat_cols[2]:
                        st.markdown(f"""
                        <div class="client-stat">
                            <div class="client-stat-value">${client['total_hours'] * client['billing_rate']:,.2f}</div>
                            <div class="client-stat-label">Total Billed</div>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Projects
                    st.markdown("""
                    <div class="client-profile-section">
                        <h4>Projects</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    for project in client['projects']:
                        st.markdown(f"- {project}")
                    
                    # Notes
                    st.markdown("""
                    <div class="client-profile-section">
                        <h4>Notes</h4>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(client['notes'])
                
                # Client timesheets
                st.markdown("""
                <div class="client-profile-section">
                    <h4>Recent Timesheets</h4>
                </div>
                """, unsafe_allow_html=True)
                
                # Get client timesheets
                client_timesheets = get_client_timesheets(client['id'])
                
                if client_timesheets:
                    # Convert to DataFrame
                    df_client_timesheets = get_timesheet_dataframe(client_timesheets)
                    
                    if not df_client_timesheets.empty:
                        # Display recent timesheets
                        for _, entry in df_client_timesheets.head(5).iterrows():
                            st.markdown(f"""
                            <div class="timesheet-detail">
                                <div class="timesheet-date">{entry['date_str']} ({entry['day_of_week']})</div>
                                <div class="timesheet-job">{entry['job_name']}</div>
                                <div class="timesheet-duration">Duration: {entry['duration_formatted']} ({entry['duration_hours']:.2f} hours)</div>
                                <div class="timesheet-notes">{entry['notes'] if entry['notes'] else 'No notes'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        # Show all button
                        if st.button("View All Timesheets"):
                            # Display all timesheets in a DataFrame
                            display_df = df_client_timesheets[['date_str', 'day_of_week', 'job_name', 'duration_formatted', 'notes']].copy()
                            display_df.columns = ['Date', 'Day', 'Job', 'Duration', 'Notes']
                            st.dataframe(display_df, use_container_width=True)
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(get_download_link(display_df, f"{client['name']}_timesheets.csv", "Download as CSV"), unsafe_allow_html=True)
                            with col2:
                                st.markdown(get_excel_download_link(display_df, f"{client['name']}_timesheets.xlsx", "Download as Excel"), unsafe_allow_html=True)
                    else:
                        st.info("No timesheet data available for this client.")
                else:
                    st.info("No timesheet data available for this client.")
            else:
                st.error("Client not found.")
                st.session_state.selected_client = None
    
    # Reports
    elif active_tab == "Reports":
        st.markdown('<h1 class="main-header">Timesheet Reports</h1>', unsafe_allow_html=True)
        
        # Show date range in the main content area
        st.caption(f"Showing data for: {st.session_state.date_range[0]} to {st.session_state.date_range[1]}")
        
        if df_timesheets.empty:
            st.info(f"No timesheet data available for the selected date range. Try selecting a different date range or adding new entries.")
            
            # Debug info for troubleshooting
            if st.session_state.debug_info:
                with st.expander("Debug Information"):
                    st.json(st.session_state.debug_info)
        else:
            # Create tabs for different reports
            report_tabs = st.tabs(["Weekly Summary", "Job Summary", "Daily Summary", "Client Summary"])
            
            # Weekly Summary Report
            with report_tabs[0]:
                st.subheader("Weekly Hours Summary")
                
                weekly_data = generate_weekly_report(df_timesheets)
                
                if not weekly_data.empty:
                    # Display weekly summary
                    weekly_display = weekly_data[['week_label', 'hours_formatted', 'hours']].copy()
                    weekly_display.columns = ['Week', 'Hours', 'Decimal Hours']
                    st.dataframe(weekly_display, use_container_width=True)
                    
                    # Chart
                    fig = px.bar(
                        weekly_data,
                        x='week_label',
                        y='hours',
                        title='Weekly Hours',
                        labels={'week_label': 'Week', 'hours': 'Hours'}
                    )
                    fig.update_layout(xaxis_title="Week", yaxis_title="Hours")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export options
                    st.markdown(get_excel_download_link(weekly_display, "weekly_summary.xlsx", "Download Weekly Summary"), unsafe_allow_html=True)
                else:
                    st.info("No weekly data available")
            
            # Job Summary Report
            with report_tabs[1]:
                st.subheader("Job Hours Summary")
                
                job_data = generate_job_summary(df_timesheets)
                
                if not job_data.empty:
                    # Display job summary
                    job_display = job_data[['Job', 'Hours Formatted', 'Hours', 'Entry Count', 'Percentage']].copy()
                    job_display.columns = ['Job', 'Hours', 'Decimal Hours', 'Number of Entries', '% of Total']
                    st.dataframe(job_display, use_container_width=True)
                    
                    # Chart
                    fig = px.pie(
                        job_data,
                        values='Hours',
                        names='Job',
                        title='Distribution of Hours by Job',
                        hover_data=['Hours Formatted', 'Entry Count', 'Percentage']
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export options
                    st.markdown(get_excel_download_link(job_display, "job_summary.xlsx", "Download Job Summary"), unsafe_allow_html=True)
                else:
                    st.info("No job data available")
            
            # Daily Summary Report
            with report_tabs[2]:
                st.subheader("Daily Hours Summary")
                
                daily_data = generate_daily_summary(df_timesheets)
                
                if not daily_data.empty:
                    # Display daily summary
                    daily_display = daily_data[['Date String', 'Day of Week', 'Hours Formatted', 'Hours', 'Entry Count']].copy()
                    daily_display.columns = ['Date', 'Day', 'Hours', 'Decimal Hours', 'Number of Entries']
                    st.dataframe(daily_display, use_container_width=True)
                    
                    # Chart
                    fig = px.bar(
                        daily_data,
                        x='Date String',
                        y='Hours',
                        title='Daily Hours',
                        labels={'Date String': 'Date', 'Hours': 'Hours'},
                        hover_data=['Day of Week', 'Entry Count']
                    )
                    fig.update_layout(xaxis_title="Date", yaxis_title="Hours")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Export options
                    st.markdown(get_excel_download_link(daily_display, "daily_summary.xlsx", "Download Daily Summary"), unsafe_allow_html=True)
                else:
                    st.info("No daily data available")
            
            # Client Summary Report
            with report_tabs[3]:
                st.subheader("Client Hours Summary")
                
                # In a real implementation, you would aggregate timesheet data by client
                # For this example, we'll create mock client summary data
                
                client_data = pd.DataFrame({
                    'Client': [client['name'] for client in st.session_state.clients],
                    'Hours': [client['total_hours'] for client in st.session_state.clients],
                    'Billing Rate': [client['billing_rate'] for client in st.session_state.clients]
                })
                
                client_data['Total Billed'] = client_data['Hours'] * client_data['Billing Rate']
                
                # Display client summary
                st.dataframe(client_data, use_container_width=True)
                
                # Chart
                fig = px.bar(
                    client_data,
                    x='Client',
                    y='Hours',
                    title='Hours by Client',
                    labels={'Client': 'Client', 'Hours': 'Hours'},
                    hover_data=['Billing Rate', 'Total Billed']
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Export options
                st.markdown(get_excel_download_link(client_data, "client_summary.xlsx", "Download Client Summary"), unsafe_allow_html=True)
    
    # Settings
    elif active_tab == "Settings":
        st.markdown('<h1 class="main-header">Settings</h1>', unsafe_allow_html=True)
        
        # Create tabs for different settings
        settings_tabs = st.tabs(["User Settings", "Application Settings", "API Settings"])
        
        # User Settings
        with settings_tabs[0]:
            st.subheader("User Profile")
            
            user_info = st.session_state.current_user
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                st.image("https://www.gravatar.com/avatar/e64c7d89f26bd1972efa854d13d7dd61?s=200", width=150)
            
            with col2:
                st.markdown(f"""
                <div class="user-info">
                    <p><strong>Name:</strong> {user_info['first_name']} {user_info['last_name']}</p>
                    <p><strong>Email:</strong> {user_info['email'] or 'N/A'}</p>
                    <p><strong>Company:</strong> {user_info.get('company_name', 'N/A')}</p>
                    <p><strong>User ID:</strong> {user_info['id']}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Notification settings
            st.subheader("Notification Settings")
            
            email_notifications = st.checkbox("Email Notifications", value=True)
            daily_summary = st.checkbox("Daily Summary", value=True)
            weekly_summary = st.checkbox("Weekly Summary", value=True)
            
            if st.button("Save Notification Settings"):
                st.success("Notification settings saved successfully!")
        
        # Application Settings
        with settings_tabs[1]:
            st.subheader("Application Settings")
            
            # Theme settings
            st.subheader("Theme Settings")
            
            theme = st.selectbox("Theme", ["Light", "Dark", "System Default"], index=0)
            accent_color = st.color_picker("Accent Color", "#4CAF50")
            
            # Date and time settings
            st.subheader("Date and Time Settings")
            
            date_format = st.selectbox("Date Format", ["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"], index=2)
            time_format = st.selectbox("Time Format", ["12-hour", "24-hour"], index=1)
            
            if st.button("Save Application Settings"):
                st.success("Application settings saved successfully!")
        
        # API Settings
        with settings_tabs[2]:
            st.subheader("API Settings")
            
            # API token
            st.text_input("API Token", value=st.session_state.api_token, type="password", disabled=True)
            
            # API endpoints
            st.subheader("API Endpoints")
            
            st.markdown(f"""
            <div class="user-info">
                <p><strong>Base URL:</strong> {BASE_URL}</p>
                <p><strong>Timesheets Endpoint:</strong> {TIMESHEETS_ENDPOINT}</p>
                <p><strong>Jobcodes Endpoint:</strong> {JOBCODES_ENDPOINT}</p>
                <p><strong>Users Endpoint:</strong> {USERS_ENDPOINT}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Test API connection
            if st.button("Test API Connection"):
                with st.spinner("Testing API connection..."):
                    response = make_api_request(CURRENT_USER_ENDPOINT)
                    
                    if response:
                        st.success("API connection successful!")
                    else:
                        st.error("API connection failed. Please check your API token.")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666;">
        <p>TSheets CRM Manager v2.0 | Developed with Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)
