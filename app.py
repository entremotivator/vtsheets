import streamlit as st

# Set page configuration - MUST be the first Streamlit command
st.set_page_config(
    page_title="TSheets CRM Manager Pro",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import calendar
import base64
import io
import json
import os
import time
import requests
from requests.exceptions import RequestException
import hashlib
import hmac
import re
import urllib.parse
from PIL import Image
import altair as alt
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu
from streamlit_lottie import st_lottie
from streamlit_extras.colored_header import colored_header
from streamlit_extras.metric_cards import style_metric_cards
from streamlit_extras.chart_container import chart_container
from streamlit_extras.stateful_button import button
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.add_vertical_space import add_vertical_space
from streamlit_extras.customize_running import center_running

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        max-width: 95%;
    }
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e6f3ff;
        border-bottom: 2px solid #4e89ae;
    }
    div.stButton > button:first-child {
        background-color: #4e89ae;
        color: white;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #2e5984;
        color: white;
        border: none;
    }
    .download-link {
        background-color: #4e89ae;
        color: white !important;
        padding: 0.5rem 1rem;
        text-decoration: none;
        border-radius: 4px;
        margin: 0.5rem 0;
        display: inline-block;
    }
    .download-link:hover {
        background-color: #2e5984;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .metric-value {
        font-size: 1.5rem;
        font-weight: bold;
        color: #4e89ae;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5a5c69;
    }
    .client-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .client-card:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
        box-shadow: 0 0.5rem 2rem 0 rgba(58, 59, 69, 0.2);
    }
    .client-name {
        font-size: 1.2rem;
        font-weight: bold;
        color: #4e89ae;
    }
    .client-info {
        font-size: 0.9rem;
        color: #5a5c69;
    }
    .timesheet-entry {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 0.5rem;
        transition: transform 0.2s ease;
    }
    .timesheet-entry:hover {
        background-color: #e9ecef;
        transform: translateY(-2px);
    }
    .timesheet-date {
        font-size: 1rem;
        font-weight: bold;
        color: #4e89ae;
    }
    .timesheet-client {
        font-size: 0.9rem;
        font-weight: bold;
    }
    .timesheet-description {
        font-size: 0.9rem;
    }
    .timesheet-duration {
        font-size: 0.9rem;
        font-weight: bold;
        color: #4e89ae;
    }
    .stDataFrame {
        font-size: 0.8rem;
    }
    .floating-card {
        background-color: white;
        border-radius: 1rem;
        padding: 1.5rem;
        box-shadow: 0 0.25rem 1.5rem rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    .info-card {
        background-color: #e6f3ff;
        border-left: 4px solid #4e89ae;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .warning-card {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .error-card {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .success-card {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 0 0.5rem 0.5rem 0;
    }
    .nav-link {
        color: #5a5c69;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        display: block;
        margin-bottom: 0.25rem;
    }
    .nav-link:hover {
        background-color: #f8f9fa;
    }
    .nav-link.active {
        background-color: #4e89ae;
        color: white;
    }
    .stApp a:not(.download-link):not(.nav-link) {
        color: #4e89ae;
    }
    .stApp a:not(.download-link):not(.nav-link):hover {
        color: #2e5984;
        text-decoration: underline;
    }
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    .stat-card {
        background-color: white;
        border-radius: 0.5rem;
        padding: 1.5rem;
        box-shadow: 0 0.25rem 1rem rgba(0, 0, 0, 0.08);
        text-align: center;
        transition: transform 0.2s ease;
    }
    .stat-card:hover {
        transform: translateY(-5px);
    }
    .stat-card .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #4e89ae;
        margin-bottom: 0.5rem;
    }
    .stat-card .stat-label {
        font-size: 1rem;
        color: #5a5c69;
    }
    .stat-card .stat-icon {
        font-size: 1.5rem;
        color: #4e89ae;
        margin-bottom: 0.5rem;
    }
    .filter-section {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
    }
    .spinner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    .spinner {
        border: 4px solid rgba(0, 0, 0, 0.1);
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border-left-color: #4e89ae;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    .page-title {
        color: #2c3e50;
        font-weight: 600;
        border-bottom: 2px solid #4e89ae;
        padding-bottom: 0.5rem;
        margin-bottom: 1.5rem;
    }
    .section-title {
        color: #34495e;
        font-weight: 500;
        margin: 1.5rem 0 1rem 0;
    }
    .data-label {
        font-weight: 500;
        color: #7f8c8d;
        margin-bottom: 0.25rem;
    }
    .data-value {
        font-weight: 400;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .empty-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .empty-state-icon {
        font-size: 3rem;
        color: #ced4da;
        margin-bottom: 1rem;
    }
    .empty-state-text {
        font-size: 1.2rem;
        color: #6c757d;
        text-align: center;
        margin-bottom: 1rem;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 700;
        line-height: 1;
        text-align: center;
        white-space: nowrap;
        vertical-align: baseline;
        border-radius: 0.25rem;
        margin-right: 0.25rem;
    }
    .badge-primary {
        color: #fff;
        background-color: #4e89ae;
    }
    .badge-success {
        color: #fff;
        background-color: #28a745;
    }
    .badge-warning {
        color: #212529;
        background-color: #ffc107;
    }
    .badge-danger {
        color: #fff;
        background-color: #dc3545;
    }
    .badge-info {
        color: #fff;
        background-color: #17a2b8;
    }
    .badge-secondary {
        color: #fff;
        background-color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# Setup custom spinner
center_running()

# Load lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None

# Load lottie animations
auth_lottie = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_v7gj8hk3.json")
dashboard_lottie = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_dzxg3wqv.json")
loading_lottie = load_lottieurl("https://assets4.lottiefiles.com/packages/lf20_usmfx6bp.json")
empty_lottie = load_lottieurl("https://assets9.lottiefiles.com/packages/lf20_hl5n0bwb.json")
error_lottie = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_qguxhcqq.json")
success_lottie = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_t9gkkhz4.json")

# API Integration Constants and Helper Functions
TSHEETS_API_BASE_URL = "https://rest.tsheets.com/api/v1"
TSHEETS_OAUTH_URL = "https://rest.tsheets.com/api/v1/grant"

class TsheetsApiException(Exception):
    """Exception raised for TSheets API errors."""
    pass

class TsheetsApi:
    def __init__(self, api_token=None):
        self.api_token = api_token
        self.base_url = TSHEETS_API_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else "",
            "Content-Type": "application/json"
        }
    
    def set_token(self, token):
        self.api_token = token
        self.headers["Authorization"] = f"Bearer {token}"
    
    def make_request(self, endpoint, method="GET", params=None, data=None, retry_count=0):
        """
        Make a request to the TSheets API
        
        Args:
            endpoint (str): API endpoint (without base URL)
            method (str): HTTP method (GET, POST, PUT, DELETE)
            params (dict): Query parameters
            data (dict): Request body data for POST/PUT requests
            retry_count (int): Number of retries performed
            
        Returns:
            dict: API response data
            
        Raises:
            TsheetsApiException: If the API request fails
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=self.headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=self.headers, params=params, json=data)
            elif method == "PUT":
                response = requests.put(url, headers=self.headers, params=params, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=self.headers, params=params)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            # Handle rate limiting
            if response.status_code == 429 and retry_count < 3:
                # Get retry-after header or default to exponential backoff
                retry_after = int(response.headers.get("Retry-After", 2 ** retry_count))
                time.sleep(retry_after)
                return self.make_request(endpoint, method, params, data, retry_count + 1)
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise TsheetsApiException("Authentication failed. Please check your API token.")
            elif response.status_code == 403:
                raise TsheetsApiException("You don't have permission to access this resource.")
            elif response.status_code == 404:
                raise TsheetsApiException(f"Resource not found: {endpoint}")
            elif response.status_code == 429:
                raise TsheetsApiException("Rate limit exceeded. Please try again later.")
            else:
                try:
                    error_data = response.json()
                    error_message = error_data.get("error", {}).get("message", str(e))
                    raise TsheetsApiException(f"API Error: {error_message}")
                except ValueError:
                    raise TsheetsApiException(f"API Error: {str(e)}")
        
        except requests.exceptions.RequestException as e:
            raise TsheetsApiException(f"Request failed: {str(e)}")
    
    def get_current_user(self):
        """Get the current user information"""
        return self.make_request("current_user")
    
    def get_users(self, params=None):
        """Get all users"""
        return self.make_request("users", params=params)
    
    def get_jobcodes(self, params=None):
        """Get all jobcodes (projects/tasks)"""
        return self.make_request("jobcodes", params=params)
    
    def get_timesheets(self, params=None):
        """Get timesheet entries"""
        return self.make_request("timesheets", params=params)
    
    def add_timesheet(self, data):
        """Add a new timesheet entry"""
        return self.make_request("timesheets", method="POST", data=data)
    
    def edit_timesheet(self, data):
        """Edit an existing timesheet entry"""
        return self.make_request("timesheets", method="PUT", data=data)
    
    def delete_timesheet(self, timesheet_id):
        """Delete a timesheet entry"""
        return self.make_request(f"timesheets/{timesheet_id}", method="DELETE")
    
    def get_reports(self, report_type, params=None):
        """Get various reports"""
        return self.make_request(f"reports/{report_type}", params=params)
    
    def get_groups(self, params=None):
        """Get all groups"""
        return self.make_request("groups", params=params)
    
    def get_custom_fields(self, params=None):
        """Get custom fields"""
        return self.make_request("customfields", params=params)
    
    def get_custom_field_items(self, params=None):
        """Get custom field items"""
        return self.make_request("customfielditems", params=params)
    
    def get_locations(self, params=None):
        """Get locations"""
        return self.make_request("locations", params=params)
    
    def get_geolocation(self, params=None):
        """Get geolocation data"""
        return self.make_request("geolocations", params=params)
    
    def get_effective_settings(self):
        """Get effective settings for the current user"""
        return self.make_request("effective_settings")
    
    def on_the_clock(self, user_id=None):
        """Check if user is currently clocked in"""
        params = {"user_ids": user_id} if user_id else None
        return self.make_request("timesheets/on_the_clock", params=params)

# Data Processing Functions
def process_timesheets_data(timesheets_data, jobcodes_data, users_data):
    """
    Process timesheet data from TSheets API into a pandas DataFrame
    
    Args:
        timesheets_data (dict): Raw timesheet data from API
        jobcodes_data (dict): Raw jobcode data from API
        users_data (dict): Raw user data from API
        
    Returns:
        pd.DataFrame: Processed timesheet data
    """
    if not timesheets_data.get('results', {}).get('timesheets'):
        return pd.DataFrame()
    
    timesheets = timesheets_data['results']['timesheets']
    
    # Create a mapping of jobcode IDs to names
    jobcode_map = {}
    if jobcodes_data and 'results' in jobcodes_data and 'jobcodes' in jobcodes_data['results']:
        for jc_id, jc in jobcodes_data['results']['jobcodes'].items():
            jobcode_map[jc_id] = jc['name']
    
    # Create a mapping of user IDs to names
    user_map = {}
    if users_data and 'results' in users_data and 'users' in users_data['results']:
        for user_id, user in users_data['results']['users'].items():
            user_map[user_id] = f"{user['first_name']} {user['last_name']}"
    
    # Process timesheet entries
    processed_data = []
    for ts_id, ts in timesheets.items():
        entry = {
            'id': ts_id,
            'user_id': ts['user_id'],
            'user': user_map.get(str(ts['user_id']), f"User {ts['user_id']}"),
            'jobcode_id': ts['jobcode_id'],
            'job': jobcode_map.get(str(ts['jobcode_id']), f"Job {ts['jobcode_id']}"),
            'start': datetime.fromtimestamp(ts['start']),
            'end': datetime.fromtimestamp(ts['end']) if ts['end'] else None,
            'date': datetime.fromtimestamp(ts['start']).date(),
            'duration': ts['duration'],
            'notes': ts['notes'] if 'notes' in ts else '',
            'status': ts['type'],
            'on_the_clock': ts['on_the_clock'] if 'on_the_clock' in ts else False,
            'timezone': ts.get('tz', 'UTC'),
            'location': ts.get('location', ''),
            'attached_files': len(ts.get('attached_files', [])),
            'customfields': ts.get('customfields', {})
        }
        
        # Calculate duration in hours
        entry['duration_hours'] = entry['duration'] / 3600 if entry['duration'] else 0
        
        processed_data.append(entry)
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_data)
    return df

def process_jobcodes_data(jobcodes_data):
    """Process jobcode data from TSheets API into a pandas DataFrame"""
    if not jobcodes_data.get('results', {}).get('jobcodes'):
        return pd.DataFrame()
    
    jobcodes = jobcodes_data['results']['jobcodes']
    
    # Process jobcode entries
    processed_data = []
    for jc_id, jc in jobcodes.items():
        entry = {
            'id': jc_id,
            'name': jc['name'],
            'parent_id': jc.get('parent_id', None),
            'assigned_to_all': jc.get('assigned_to_all', False),
            'type': jc.get('type', ''),
            'billable': jc.get('billable', False),
            'billable_rate': jc.get('billable_rate', 0),
            'has_children': jc.get('has_children', False),
            'last_modified': datetime.fromtimestamp(jc['last_modified']),
            'created': datetime.fromtimestamp(jc['created']),
            'active': jc.get('active', True)
        }
        processed_data.append(entry)
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_data)
    return df

def process_users_data(users_data):
    """Process user data from TSheets API into a pandas DataFrame"""
    if not users_data.get('results', {}).get('users'):
        return pd.DataFrame()
    
    users = users_data['results']['users']
    
    # Process user entries
    processed_data = []
    for user_id, user in users.items():
        entry = {
            'id': user_id,
            'first_name': user['first_name'],
            'last_name': user['last_name'],
            'full_name': f"{user['first_name']} {user['last_name']}",
            'username': user.get('username', ''),
            'email': user.get('email', ''),
            'group_id': user.get('group_id', None),
            'manager_of_group_ids': user.get('manager_of_group_ids', []),
            'employee_number': user.get('employee_number', ''),
            'hire_date': user.get('hire_date', ''),
            'terminated': user.get('terminated', False),
            'last_modified': datetime.fromtimestamp(user['last_modified']),
            'created': datetime.fromtimestamp(user['created']),
            'active': user.get('active', True)
        }
        processed_data.append(entry)
    
    # Convert to DataFrame
    df = pd.DataFrame(processed_data)
    return df

# Utility functions
def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    if not seconds:
        return "00:00:00"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_duration_hours(seconds):
    """Format duration in seconds to decimal hours"""
    if not seconds:
        return "0.00"
    
    hours = seconds / 3600
    return f"{hours:.2f}"

def get_download_link(df, filename, link_text):
    """Generate a download link for a DataFrame as CSV"""
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
        "Last Quarter": (
            datetime(today.year if today.month > 3 else today.year - 1, 
                   ((today.month-1-3)//3)*3+1 if today.month > 3 else 10, 1).date(),
            datetime(today.year, ((today.month-1)//3)*3+1, 1).date() - timedelta(days=1)
        ),
        "This Year": (
            datetime(today.year, 1, 1).date(),
            today
        ),
        "Last Year": (
            datetime(today.year - 1, 1, 1).date(),
            datetime(today.year, 1, 1).date() - timedelta(days=1)
        )
    }

def generate_calendar_events(df_timesheets):
    """Generate calendar events from timesheet data"""
    if df_timesheets.empty:
        return []
    
    events = []
    for _, row in df_timesheets.iterrows():
        start_time = row['start']
        end_time = row['end'] if row['end'] else start_time + timedelta(seconds=row['duration'])
        
        events.append({
            'id': str(row['id']),
            'title': f"{row['job']}",
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': get_jobcode_color(row['job']),
            'borderColor': get_jobcode_color(row['job']),
            'extendedProps': {
                'jobcode': row['job'],
                'notes': row['notes'],
                'duration': format_duration(row['duration']),
                'duration_hours': row['duration_hours'],
                'user': row['user']
            }
        })
    
    return events

def get_jobcode_color(jobcode_name):
    """Generate a consistent color for a jobcode based on its name"""
    # Simple hash function to generate a color
    hash_value = hash(jobcode_name) % 360
    return f"hsl({hash_value}, 70%, 60%)"

def get_month_calendar_data(year, month, df_timesheets):
    """Generate calendar data for a specific month"""
    # Get the first day of the month
    first_day = date(year, month, 1)

    # Get the number of days in the month
    _, num_days = calendar.monthrange(year, month)

    # Get the day of the week for the first day (0 = Monday, 6 = Sunday)
    first_weekday = first_day.weekday()

    # Adjust for Sunday as the first day of the week
    first_weekday = (first_weekday + 1) % 7

    # Create a list of dates for the calendar
    calendar_dates = []

    # Add days from the previous month
    if first_weekday > 0:
        prev_month = first_day - timedelta(days=1)
        prev_month_year, prev_month_num = prev_month.year, prev_month.month
        _, prev_month_days = calendar.monthrange(prev_month_year, prev_month_num)
        
        for i in range(first_weekday):
            day = prev_month_days - first_weekday + i + 1
            calendar_dates.append({
                'date': date(prev_month_year, prev_month_num, day),
                'day': day,
                'current_month': False,
                'has_entries': False,
                'hours': 0
            })

    # Add days from the current month
    for day in range(1, num_days + 1):
        current_date = date(year, month, day)
        
        # Check if there are timesheet entries for this date
        has_entries = False
        hours = 0
        
        if not df_timesheets.empty and 'date' in df_timesheets.columns:
            day_entries = df_timesheets[df_timesheets['date'] == current_date]
            has_entries = len(day_entries) > 0
            hours = day_entries['duration_hours'].sum() if has_entries else 0
        
        calendar_dates.append({
            'date': current_date,
            'day': day,
            'current_month': True,
            'has_entries': has_entries,
            'hours': hours
        })

    # Add days from the next month to complete the grid (6 rows x 7 columns = 42 cells)
    remaining_days = 42 - len(calendar_dates)
    if remaining_days > 0:
        next_month = date(year, month, num_days) + timedelta(days=1)
        next_month_year, next_month_num = next_month.year, next_month.month
        
        for day in range(1, remaining_days + 1):
            calendar_dates.append({
                'date': date(next_month_year, next_month_num, day),
                'day': day,
                'current_month': False,
                'has_entries': False,
                'hours': 0
            })

    return calendar_dates

def load_data(api, start_date, end_date):
    """
    Load data from TSheets API
    
    Args:
        api (TsheetsApi): TSheets API instance
        start_date (date): Start date for filtering
        end_date (date): End date for filtering
        
    Returns:
        tuple: (users_df, jobcodes_df, timesheets_df, error)
    """
    try:
        with st.spinner("Loading user data..."):
            users_data = api.get_users()
            users_df = process_users_data(users_data)
        
        with st.spinner("Loading jobcode data..."):
            jobcodes_data = api.get_jobcodes()
            jobcodes_df = process_jobcodes_data(jobcodes_data)
        
        with st.spinner("Loading timesheet data..."):
            # Convert dates to timestamps for API
            start_timestamp = int(datetime.combine(start_date, datetime.min.time()).timestamp())
            end_timestamp = int(datetime.combine(end_date, datetime.max.time()).timestamp())
            
            params = {
                "start_date": start_timestamp,
                "end_date": end_timestamp,
                "per_page": 1000  # Maximum allowed per page
            }
            
            timesheets_data = api.get_timesheets(params=params)
            timesheets_df = process_timesheets_data(timesheets_data, jobcodes_data, users_data)
            
            # Handle pagination if needed
            while timesheets_data.get('more', False) and timesheets_data.get('next_page', None):
                params['page'] = timesheets_data['next_page']
                timesheets_data = api.get_timesheets(params=params)
                additional_df = process_timesheets_data(timesheets_data, jobcodes_data, users_data)
                timesheets_df = pd.concat([timesheets_df, additional_df], ignore_index=True)
        
        return users_df, jobcodes_df, timesheets_df, None
    
    except TsheetsApiException as e:
        return None, None, None, str(e)
    except Exception as e:
        return None, None, None, f"Unexpected error: {str(e)}"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_token' not in st.session_state:
    st.session_state.api_token = ""
if 'api' not in st.session_state:
    st.session_state.api = None
if 'users_df' not in st.session_state:
    st.session_state.users_df = None
if 'jobcodes_df' not in st.session_state:
    st.session_state.jobcodes_df = None
if 'timesheets_df' not in st.session_state:
    st.session_state.timesheets_df = None
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Dashboard"
if 'selected_jobcode' not in st.session_state:
    st.session_state.selected_jobcode = None
if 'selected_date_range' not in st.session_state:
    st.session_state.selected_date_range = "Last 7 Days"
if 'custom_start_date' not in st.session_state:
    st.session_state.custom_start_date = datetime.now().date() - timedelta(days=7)
if 'custom_end_date' not in st.session_state:
    st.session_state.custom_end_date = datetime.now().date()
if 'calendar_date' not in st.session_state:
    st.session_state.calendar_date = datetime.now().date()
if 'calendar_view' not in st.session_state:
    st.session_state.calendar_view = "month"
if 'current_user' not in st.session_state:
    st.session_state.current_user = None
if 'error' not in st.session_state:
    st.session_state.error = None
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'last_refresh' not in st.session_state:
    st.session_state.last_refresh = None

# Sidebar for authentication
with st.sidebar:
    if not st.session_state.authenticated:
        st.image("https://www.tsheets.com/uploads/2020/06/tsheets-logo.png", width=200)
        st.title("TSheets CRM Manager Pro")
        
        st.header("Authentication")
        
        if auth_lottie:
            st_lottie(auth_lottie, height=150, key="auth_animation")
        
        st.info("Please provide your TSheets API token to continue.")
        
        with st.form("auth_form"):
            api_token = st.text_input("API Token", type="password", 
                                    help="You can generate an API token in your TSheets account under Account > API")
            submit_button = st.form_submit_button(label="Login")
            
            if submit_button:
                if api_token:
                    # Initialize API client
                    api = TsheetsApi(api_token)
                    
                    try:
                        # Test API token by getting current user
                        with st.spinner("Verifying credentials..."):
                            current_user_data = api.get_current_user()
                            
                            if 'results' in current_user_data and 'user' in current_user_data['results']:
                                user = current_user_data['results']['user']
                                st.session_state.current_user = {
                                    'id': user['id'],
                                    'first_name': user['first_name'],
                                    'last_name': user['last_name'],
                                    'email': user.get('email', ''),
                                    'company_name': user.get('company_name', '')
                                }
                                
                                st.session_state.api_token = api_token
                                st.session_state.api = api
                                st.session_state.authenticated = True
                                
                                # Load initial data
                                date_range_presets = get_date_range_presets()
                                start_date, end_date = date_range_presets[st.session_state.selected_date_range]
                                
                                users_df, jobcodes_df, timesheets_df, error = load_data(api, start_date, end_date)
                                
                                if error:
                                    st.session_state.error = error
                                else:
                                    st.session_state.users_df = users_df
                                    st.session_state.jobcodes_df = jobcodes_df
                                    st.session_state.timesheets_df = timesheets_df
                                    st.session_state.data_loaded = True
                                    st.session_state.last_refresh = datetime.now()
                                
                                st.experimental_rerun()
                            else:
                                st.error("Invalid API token. Please check your credentials.")
                    except TsheetsApiException as e:
                        st.error(f"API Error: {str(e)}")
                    except Exception as e:
                        st.error(f"Unexpected error: {str(e)}")
                else:
                    st.error("Please enter your API token.")
        
        st.markdown("---")
        st.caption("Don't have a TSheets account? [Sign up here](https://www.tsheets.com/signup)")
        st.caption("Need help? [Contact Support](https://www.tsheets.com/contact-us)")
    else:
        # Show user info
        st.image("https://www.tsheets.com/uploads/2020/06/tsheets-logo.png", width=150)
        st.title("TSheets CRM Manager Pro")
        
        if st.session_state.current_user:
            st.success(f"Welcome, {st.session_state.current_user['first_name']}!")
            if st.session_state.current_user.get('company_name'):
                st.caption(f"Company: {st.session_state.current_user['company_name']}")
        
        # Navigation
        st.header("Navigation")
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Timesheets", "Projects", "Calendar", "Reports", "Settings"],
            icons=["speedometer2", "clock", "folder", "calendar3", "file-earmark-bar-graph", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        st.session_state.current_view = selected
        
        # Date range selector
        st.header("Date Range")
        date_range_presets = get_date_range_presets()
        date_range_options = list(date_range_presets.keys()) + ["Custom"]
        selected_date_range = st.selectbox("Select Date Range", date_range_options, index=date_range_options.index(st.session_state.selected_date_range))
        
        if selected_date_range == "Custom":
            custom_start_date = st.date_input("Start Date", value=st.session_state.custom_start_date)
            custom_end_date = st.date_input("End Date", value=st.session_state.custom_end_date)
            
            if custom_start_date <= custom_end_date:
                st.session_state.custom_start_date = custom_start_date
                st.session_state.custom_end_date = custom_end_date
                start_date, end_date = custom_start_date, custom_end_date
            else:
                st.error("End date must be after start date")
                start_date, end_date = st.session_state.custom_start_date, st.session_state.custom_end_date
        else:
            start_date, end_date = date_range_presets[selected_date_range]
        
        # Update session state
        if st.session_state.selected_date_range != selected_date_range:
            st.session_state.selected_date_range = selected_date_range
            
            # Reload data if date range changed
            if st.session_state.authenticated and st.session_state.api:
                users_df, jobcodes_df, timesheets_df, error = load_data(st.session_state.api, start_date, end_date)
                
                if error:
                    st.session_state.error = error
                else:
                    st.session_state.users_df = users_df
                    st.session_state.jobcodes_df = jobcodes_df
                    st.session_state.timesheets_df = timesheets_df
                    st.session_state.data_loaded = True
                    st.session_state.last_refresh = datetime.now()
        
        # Refresh data button
        if st.button("Refresh Data"):
            if st.session_state.authenticated and st.session_state.api:
                users_df, jobcodes_df, timesheets_df, error = load_data(st.session_state.api, start_date, end_date)
                
                if error:
                    st.session_state.error = error
                else:
                    st.session_state.users_df = users_df
                    st.session_state.jobcodes_df = jobcodes_df
                    st.session_state.timesheets_df = timesheets_df
                    st.session_state.data_loaded = True
                    st.session_state.last_refresh = datetime.now()
                    st.success("Data refreshed successfully!")
        
        if st.session_state.last_refresh:
            st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Logout button
        st.markdown("---")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to TSheets CRM Manager Pro")
    st.write("Please login using your TSheets API token to access the application.")
    
    # Features
    st.header("Features")
    
    feature_col1, feature_col2, feature_col3 = st.columns(3)
    
    with feature_col1:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">📊</div>
            <div class="stat-label">Comprehensive Dashboards</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col2:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">📆</div>
            <div class="stat-label">Interactive Calendar</div>
        </div>
        """, unsafe_allow_html=True)
    
    with feature_col3:
        st.markdown("""
        <div class="stat-card">
            <div class="stat-icon">📝</div>
            <div class="stat-label">Advanced Reporting</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Show dashboard sample image
    if dashboard_lottie:
        st_lottie(dashboard_lottie, height=300, key="dashboard_animation")
else:
    # Check for errors
    if st.session_state.error:
        st.error(f"Error: {st.session_state.error}")
        if st.button("Clear Error"):
            st.session_state.error = None
            st.experimental_rerun()
    
    # Get date range
    if st.session_state.selected_date_range == "Custom":
        start_date = st.session_state.custom_start_date
        end_date = st.session_state.custom_end_date
    else:
        date_range_presets = get_date_range_presets()
        start_date, end_date = date_range_presets[st.session_state.selected_date_range]
    
    # Dashboard View
    if st.session_state.current_view == "Dashboard":
        st.title("Dashboard")
        st.write(f"Showing data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**")
        
        if not st.session_state.data_loaded:
            if loading_lottie:
                st_lottie(loading_lottie, height=200, key="loading_animation")
            st.info("Loading data from TSheets API. Please wait...")
        elif st.session_state.timesheets_df is None or st.session_state.timesheets_df.empty:
            if empty_lottie:
                st_lottie(empty_lottie, height=200, key="empty_animation")
            st.warning("No timesheet data available for the selected date range.")
        else:
            # Key metrics
            df = st.session_state.timesheets_df
            
            total_hours = df['duration_hours'].sum()
            unique_jobcodes = df['jobcode_id'].nunique()
            total_entries = len(df)
            avg_daily_hours = total_hours / max((end_date - start_date).days + 1, 1)
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_hours:.2f}</div>
                    <div class="stat-label">Total Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{unique_jobcodes}</div>
                    <div class="stat-label">Active Projects</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_entries}</div>
                    <div class="stat-label">Time Entries</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{avg_daily_hours:.2f}</div>
                    <div class="stat-label">Avg. Daily Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Charts
            colored_header(
                label="Time Distribution",
                description="Analyzing how your time is distributed",
                color_name="blue-70"
            )
            
            tab1, tab2, tab3 = st.tabs(["By Project", "By Day", "By User"])
            
            with tab1:
                # Hours by jobcode
                hours_by_jobcode = df.groupby('job')['duration_hours'].sum().reset_index()
                hours_by_jobcode = hours_by_jobcode.sort_values('duration_hours', ascending=False)
                
                with chart_container(df):
                    fig = px.bar(
                        hours_by_jobcode.head(10),
                        x='job',
                        y='duration_hours',
                        title='Top 10 Projects by Hours',
                        labels={'job': 'Project', 'duration_hours': 'Hours'},
                        color='duration_hours',
                        color_continuous_scale=px.colors.sequential.Blues
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Hours by day
                df['date_only'] = df['start'].dt.date
                hours_by_day = df.groupby('date_only')['duration_hours'].sum().reset_index()
                hours_by_day = hours_by_day.sort_values('date_only')
                
                with chart_container(df):
                    fig = px.line(
                        hours_by_day,
                        x='date_only',
                        y='duration_hours',
                        title='Hours by Day',
                        labels={'date_only': 'Date', 'duration_hours': 'Hours'},
                        markers=True
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
            
            with tab3:
                # Hours by user
                if 'user' in df.columns:
                    hours_by_user = df.groupby('user')['duration_hours'].sum().reset_index()
                    hours_by_user = hours_by_user.sort_values('duration_hours', ascending=False)
                    
                    with chart_container(df):
                        fig = px.bar(
                            hours_by_user,
                            x='user',
                            y='duration_hours',
                            title='Hours by User',
                            labels={'user': 'User', 'duration_hours': 'Hours'},
                            color='duration_hours',
                            color_continuous_scale=px.colors.sequential.Blues
                        )
                        fig.update_layout(height=400)
                        st.plotly_chart(fig, use_container_width=True)
            
            # Recent activity
            colored_header(
                label="Recent Activity",
                description="Your latest time entries",
                color_name="blue-70"
            )
            
            recent_entries = df.sort_values('start', ascending=False).head(5)
            
            if not recent_entries.empty:
                for _, entry in recent_entries.iterrows():
                    st.markdown(f"""
                    <div class="timesheet-entry">
                        <div class="timesheet-date">{entry['start'].strftime('%Y-%m-%d %H:%M')}</div>
                        <div class="timesheet-client">{entry['job']}</div>
                        <div class="timesheet-description">{entry['notes']}</div>
                        <div class="timesheet-duration">{format_duration_hours(entry['duration'])} hours</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No recent activity in the selected date range.")
            
            # Quick actions
            colored_header(
                label="Quick Actions",
                description="Common tasks and actions",
                color_name="blue-70"
            )
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("Add Timesheet Entry"):
                    st.session_state.current_view = "Timesheets"
                    st.experimental_rerun()
            
            with col2:
                if st.button("View All Projects"):
                    st.session_state.current_view = "Projects"
                    st.experimental_rerun()
            
            with col3:
                if st.button("Generate Reports"):
                    st.session_state.current_view = "Reports"
                    st.experimental_rerun()
    
    # Timesheets View
    elif st.session_state.current_view == "Timesheets":
        st.title("Timesheets")
        st.write(f"Showing data from **{start_date.strftime('%Y-%m-%d')}** to **{end_date.strftime('%Y-%m-%d')}**")
        
        if not st.session_state.data_loaded:
            if loading_lottie:
                st_lottie(loading_lottie, height=200, key="loading_animation")
            st.info("Loading data from TSheets API. Please wait...")
        elif st.session_state.timesheets_df is None or st.session_state.timesheets_df.empty:
            if empty_lottie:
                st_lottie(empty_lottie, height=200, key="empty_animation")
            st.warning("No timesheet data available for the selected date range.")
        else:
            # Add new timesheet entry
            with st.expander("Add New Timesheet Entry", expanded=False):
                col1, col2 = st.columns(2)
                
                with col1:
                    entry_date = st.date_input("Date", value=datetime.now().date())
                    entry_start_time = st.time_input("Start Time", value=datetime.now().time())
                    
                    # Combine date and time
                    entry_start_datetime = datetime.combine(entry_date, entry_start_time)
                    
                    # Duration or end time selection
                    duration_type = st.radio("Entry Type", ["Duration", "End Time"])
                
                with col2:
                    if st.session_state.users_df is not None and not st.session_state.users_df.empty:
                        users = st.session_state.users_df
                        if len(users) > 0 and 'id' in users.columns and 'full_name' in users.columns:
                            entry_user = st.selectbox("User", options=users['id'].tolist(), format_func=lambda x: users[users['id'] == x]['full_name'].iloc[0] if len(users[users['id'] == x]) > 0 else f"User {x}")
                        else:
                            entry_user = st.session_state.current_user['id'] if st.session_state.current_user else ""
                    else:
                        entry_user = st.session_state.current_user['id'] if st.session_state.current_user else ""
                    
                    if st.session_state.jobcodes_df is not None and not st.session_state.jobcodes_df.empty:
                        jobcodes = st.session_state.jobcodes_df
                        if len(jobcodes) > 0 and 'id' in jobcodes.columns and 'name' in jobcodes.columns:
                            entry_jobcode = st.selectbox("Project/Task", options=jobcodes[jobcodes['active']]['id'].tolist(), format_func=lambda x: jobcodes[jobcodes['id'] == x]['name'].iloc[0] if len(jobcodes[jobcodes['id'] == x]) > 0 else f"Jobcode {x}")
                        else:
                            entry_jobcode = ""
                    else:
                        entry_jobcode = ""
                    
                    if duration_type == "Duration":
                        entry_duration = st.number_input("Duration (hours)", min_value=0.0, max_value=24.0, value=1.0, step=0.25)
                        entry_end_datetime = entry_start_datetime + timedelta(hours=entry_duration)
                    else:
                        entry_end_time = st.time_input("End Time", value=(datetime.now() + timedelta(hours=1)).time())
                        entry_end_datetime = datetime.combine(entry_date, entry_end_time)
                        
                        # Ensure end time is after start time
                        if entry_end_datetime <= entry_start_datetime:
                            st.error("End time must be after start time")
                            entry_duration = 0
                        else:
                            entry_duration = (entry_end_datetime - entry_start_datetime).total_seconds() / 3600
                
                entry_notes = st.text_area("Notes", height=100)
                
                if st.button("Save Timesheet Entry"):
                    if entry_jobcode and entry_duration > 0:
                        try:
                            # Prepare data for API
                            timesheet_data = {
                                "data": [
                                    {
                                        "user_id": int(entry_user),
                                        "jobcode_id": int(entry_jobcode),
                                        "start": int(entry_start_datetime.timestamp()),
                                        "end": int(entry_end_datetime.timestamp()),
                                        "notes": entry_notes
                                    }
                                ]
                            }
                            
                            # Add timesheet entry
                            result = st.session_state.api.add_timesheet(timesheet_data)
                            
                            if 'results' in result and 'timesheets' in result['results']:
                                st.success("Timesheet entry saved successfully!")
                                
                                # Refresh data
                                users_df, jobcodes_df, timesheets_df, error = load_data(st.session_state.api, start_date, end_date)
                                
                                if error:
                                    st.session_state.error = error
                                else:
                                    st.session_state.users_df = users_df
                                    st.session_state.jobcodes_df = jobcodes_df
                                    st.session_state.timesheets_df = timesheets_df
                                    st.session_state.data_loaded = True
                                    st.session_state.last_refresh = datetime.now()
                            else:
                                st.error("Failed to save timesheet entry.")
                        except TsheetsApiException as e:
                            st.error(f"API Error: {str(e)}")
                        except Exception as e:
                            st.error(f"Unexpected error: {str(e)}")
                    else:
                        st.error("Please select a project and ensure duration is greater than 0.")
            
            # Filter options
            df = st.session_state.timesheets_df
            
            with st.expander("Filter Options", expanded=True):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    filter_jobcode = st.multiselect(
                        "Filter by Project",
                        options=sorted(df['job'].unique()),
                        default=[]
                    )
                
                with col2:
                    if 'user' in df.columns:
                        filter_user = st.multiselect(
                            "Filter by User",
                            options=sorted(df['user'].unique()),
                            default=[]
                        )
                    else:
                        filter_user = []
                
                with col3:
                    filter_date_sort = st.radio("Sort by Date", options=["Newest First", "Oldest First"])
            
            # Apply filters
            filtered_df = df.copy()
            
            if filter_jobcode:
                filtered_df = filtered_df[filtered_df['job'].isin(filter_jobcode)]
            
            if filter_user and 'user' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['user'].isin(filter_user)]
            
            # Sort by date
            if filter_date_sort == "Newest First":
                filtered_df = filtered_df.sort_values('start', ascending=False)
            else:
                filtered_df = filtered_df.sort_values('start', ascending=True)
            
            # Display timesheet entries
            if not filtered_df.empty:
                # Summary metrics
                total_filtered_hours = filtered_df['duration_hours'].sum()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Entries", len(filtered_df))
                
                with col2:
                    st.metric("Total Hours", f"{total_filtered_hours:.2f}")
                
                with col3:
                    avg_entry_duration = total_filtered_hours / len(filtered_df) if len(filtered_df) > 0 else 0
                    st.metric("Avg. Entry Duration", f"{avg_entry_duration:.2f} hrs")
                
                # Download links
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(get_download_link(filtered_df, "timesheet_entries.csv", "Download as CSV"), unsafe_allow_html=True)
                
                with col2:
                    st.markdown(get_excel_download_link(filtered_df, "timesheet_entries.xlsx", "Download as Excel"), unsafe_allow_html=True)
                
                # Display as table with interactive features
                st.dataframe(
                    filtered_df[['start', 'job', 'notes', 'duration_hours', 'user']].rename(columns={
                        'start': 'Date & Time',
                        'job': 'Project',
                        'notes': 'Notes',
                        'duration_hours': 'Hours',
                        'user': 'User'
                    }),
                    use_container_width=True
                )
                
                # Pagination
                if len(filtered_df) > 20:
                    st.write(f"Showing {min(20, len(filtered_df))} of {len(filtered_df)} entries")
            else:
                if empty_lottie:
                    st_lottie(empty_lottie, height=200, key="empty_results_animation")
                st.info("No timesheet entries found with the selected filters.")

# Run the app
if __name__ == "__main__":
    # This is handled by Streamlit
    pass
