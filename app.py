import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta, date
import time
import plotly.express as px
import plotly.graph_objects as go
import io
import base64
import calendar # Ensure calendar is imported
import re
import altair as alt
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns

# Set page configuration
st.set_page_config(
    page_title="TSheets CRM Manager Pro", 
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (from original)
st.markdown("""
<style>
    /* General Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        color: #2C3E50;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
        color: #34495E;
    }
    .subsection-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 0.8rem;
        margin-bottom: 0.4rem;
        color: #34495E;
    }        
    .info-text {
        font-size: 1rem;
        color: #555;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #155724;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #721c24;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #856404;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 15px;
        border-left: 5px solid #0c5460;
    }
    
    /* Button Styles */
    .stButton button {
        width: 100%;
        border-radius: 5px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    
    /* User Info */
    .user-info {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #4CAF50;
    }
    
    /* Client Card */
    .client-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 25px;
        margin-bottom: 25px;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-top: 5px solid #4CAF50;
    }
    .client-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.15);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 1px;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e9ecef;
        border-bottom: 3px solid #4CAF50;
    }
    
    /* Metric Cards */
    .metric-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 25px;
        text-align: center;
        height: 100%;
        transition: transform 0.3s ease;
        border-top: 4px solid #4CAF50;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #4CAF50;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 1.1rem;
        color: #555;
        font-weight: 500;
    }
    
    /* Download Links */
    .download-link {
        text-decoration: none;
        color: white;
        background-color: #4CAF50;
        padding: 12px 20px;
        border-radius: 5px;
        text-align: center;
        display: inline-block;
        margin-top: 15px;
        font-weight: 500;
        transition: background-color 0.3s ease, transform 0.3s ease;
    }
    .download-link:hover {
        background-color: #45a049;
        transform: translateY(-2px);
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
    
    /* Client Profile */
    .client-profile {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 25px;
        margin-bottom: 25px;
    }
    .client-profile h3 {
        color: #2C3E50;
        border-bottom: 1px solid #eee;
        padding-bottom: 15px;
        margin-bottom: 20px;
    }
    .client-profile-section {
        margin-bottom: 20px;
    }
    .client-profile-section h4 {
        color: #34495E;
        margin-bottom: 15px;
        font-weight: 600;
    }
    .client-contact {
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .client-contact-icon {
        margin-right: 15px;
        color: #3498DB;
    }
    
    /* Timesheet Detail */
    .timesheet-detail {
        background-color: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 20px;
        margin-bottom: 20px;
        border-radius: 0 10px 10px 0;
        transition: transform 0.3s ease;
    }
    .timesheet-detail:hover {
        transform: translateX(5px);
    }
    .timesheet-date {
        font-weight: bold;
        color: #2C3E50;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    .timesheet-duration {
        font-weight: bold;
        color: #4CAF50;
        margin: 5px 0;
    }
    .timesheet-job {
        color: #3498DB;
        font-weight: 500;
        margin: 5px 0;
    }
    .timesheet-notes {
        font-style: italic;
        color: #7F8C8D;
        margin-top: 10px;
        padding-top: 5px;
        border-top: 1px dashed #ddd;
    }
    
    /* Status Badges */
    .status-badge {
        display: inline-block;
        padding: 5px 12px;
        border-radius: 15px;
        font-size: 0.85rem;
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
    
    /* Avatar */
    .avatar {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 20px;
        border: 4px solid #4CAF50;
    }
    
    /* Client Stats */
    .client-stats {
        display: flex;
        justify-content: space-between;
        margin-bottom: 20px;
    }
    .client-stat {
        text-align: center;
        flex: 1;
        padding: 15px;
        background-color: #f8f9fa;
        border-radius: 10px;
        margin: 0 8px;
        transition: transform 0.3s ease;
    }
    .client-stat:hover {
        transform: translateY(-5px);
    }
    .client-stat-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .client-stat-label {
        font-size: 0.9rem;
        color: #555;
        margin-top: 5px;
    }
    
    /* Activity Timeline */
    .activity-timeline {
        position: relative;
        margin-left: 30px;
        padding-left: 20px;
    }
    .activity-timeline:before {
        content: ";
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
        margin-bottom: 25px;
    }
    .activity-item:before {
        content: ";
        position: absolute;
        left: -10px;
        top: 0;
        width: 16px;
        height: 16px;
        border-radius: 50%;
        background-color: #4CAF50;
        border: 3px solid #fff;
        box-shadow: 0 0 0 1px #4CAF50;
    }
    .activity-date {
        font-size: 0.85rem;
        color: #7F8C8D;
        margin-bottom: 5px;
    }
    .activity-content {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-top: 8px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
    }
    
    /* Calendar Styles (from original, enhanced by new features) */
    .calendar-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .calendar-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 15px;
    }
    .calendar-title {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2C3E50;
    }
    .calendar-nav {
        display: flex;
        gap: 10px;
    }
    .calendar-nav button {
        background-color: #f8f9fa;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .calendar-nav button:hover {
        background-color: #e9ecef;
    }
    .calendar-weekdays {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
        margin-bottom: 10px;
    }
    .calendar-weekday {
        text-align: center;
        font-weight: bold;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
    }
    .calendar-days {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 5px;
    }
    .calendar-day {
        text-align: center;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s ease, transform 0.3s ease;
        min-height: 80px; /* Increased min-height for better clickability and content */
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Align day number to top */
        align-items: center;
        position: relative;
        border: 1px solid #eee; /* Add a light border to each day cell */
    }
    .calendar-day:hover {
        background-color: #e9ecef;
        transform: scale(1.02);
    }
    .calendar-day.today {
        background-color: #d4edda;
        color: #155724;
        font-weight: bold;
        border: 1px solid #155724;
    }
    .calendar-day.has-entries {
        background-color: #d1ecf1; /* Light blue for days with entries */
        color: #0c5460;
    }
    .calendar-day.has-entries.selected {
        background-color: #4CAF50; /* Green when selected and has entries */
        color: white;
        border: 1px solid #3e8e41;
    }
    .calendar-day.selected {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
        border: 1px solid #3e8e41;
    }
    .calendar-day.other-month {
        color: #aaa;
        background-color: #fdfdfd; /* Slightly different for other month days */
        cursor: default;
    }
    .day-number {
        font-size: 0.9rem; /* Slightly smaller day number */
        margin-bottom: 3px;
        display: block;
        width: 100%;
        text-align: left;
        padding-left: 5px;
    }
    .day-entry-indicator {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: #3498DB; /* Blue dot for entries */
        position: absolute;
        top: 8px; /* Position dot near day number */
        right: 8px;
    }
    .day-entry-summary {
        font-size: 0.75rem;
        color: #555;
        margin-top: auto; /* Push summary to bottom if space allows */
        padding-bottom: 5px;
    }
    .calendar-day.has-entries .day-entry-summary {
        color: #0c5460;
    }
    .calendar-day.selected .day-entry-summary {
        color: white;
    }

    /* Day View for Calendar */
    .day-view {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-top: 20px;
    }
    .day-view-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    .day-view-entry {
        background-color: #f8f9fa;
        border-left: 4px solid #4CAF50;
        padding: 15px;
        margin-bottom: 15px;
        border-radius: 0 5px 5px 0;
    }
    .day-view-time {
        font-weight: bold;
        color: #2C3E50;
    }
    .day-view-job {
        color: #3498DB;
        font-weight: 500;
        margin: 5px 0;
    }
    .day-view-duration {
        font-weight: bold;
        color: #4CAF50;
    }
    .day-view-notes {
        font-style: italic;
        color: #7F8C8D;
        margin-top: 5px;
    }
    
    /* Heat Map Calendar (from original) */
    .heatmap-container {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
    }
    .heatmap-legend {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 10px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        margin: 0 10px;
    }
    .legend-color {
        width: 20px;
        height: 20px;
        margin-right: 5px;
        border-radius: 3px;
    }
    .legend-label {
        font-size: 0.9rem;
        color: #555;
    }
    
    /* Analytics Dashboard (from original) */
    .analytics-card {
        background-color: white;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
        padding: 20px;
        margin-bottom: 20px;
        height: 100%;
    }
    .analytics-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2C3E50;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #eee;
    }
    
    /* Productivity Score (from original) */
    .productivity-score {
        text-align: center;
        padding: 20px;
    }
    .score-value {
        font-size: 3rem;
        font-weight: bold;
        color: #4CAF50;
    }
    .score-label {
        font-size: 1.2rem;
        color: #555;
        margin-top: 10px;
    }
    
    /* Progress Bar (from original) */
    .progress-container {
        margin: 15px 0;
    }
    .progress-label {
        display: flex;
        justify-content: space-between;
        margin-bottom: 5px;
    }
    .progress-bar {
        height: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        overflow: hidden;
    }
    .progress-fill {
        height: 100%;
        background-color: #4CAF50;
        border-radius: 5px;
    }
    
    /* Notification Badge (from original) */
    .notification-badge {
        display: inline-block;
        background-color: #dc3545;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        text-align: center;
        line-height: 20px;
        font-size: 0.8rem;
        margin-left: 5px;
    }
    
    /* Search Bar (from original) */
    .search-container {
        position: relative;
        margin-bottom: 20px;
    }
    .search-icon {
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: #aaa;
    }
    .search-input {
        width: 100%;
        padding: 10px 10px 10px 35px;
        border: 1px solid #ddd;
        border-radius: 5px;
        font-size: 1rem;
    }
    .search-input:focus {
        border-color: #4CAF50;
        outline: none;
    }
    
    /* Footer (from original) */
    .footer {
        text-align: center;
        padding: 20px;
        color: #666;
        border-top: 1px solid #eee;
        margin-top: 40px;
    }
    .footer-logo {
        max-width: 100px;
        margin-bottom: 10px;
    }
    .footer-links {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 10px 0;
    }
    .footer-link {
        color: #4CAF50;
        text-decoration: none;
    }
    .footer-link:hover {
        text-decoration: underline;
    }
    
    /* Responsive Adjustments (from original) */
    @media (max-width: 768px) {
        .client-stats {
            flex-direction: column;
        }
        .client-stat {
            margin: 5px 0;
        }
        .calendar-weekday, .calendar-day {
            padding: 5px;
            font-size: 0.8rem; /* Adjusted for smaller screens */
            min-height: 60px;
        }
        .day-number {
            font-size: 0.8rem;
        }
        .day-entry-indicator {
            width: 5px;
            height: 5px;
            top: 5px;
            right: 5px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 10px; /* Adjust tab padding for smaller screens */
            font-size: 0.85rem;
        }
        .main-header {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.5rem;
        }
        .subsection-header {
            font-size: 1.3rem;
        }
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
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "api_token" not in st.session_state:
    st.session_state.api_token = ""
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "users" not in st.session_state: # Will be populated by cached function
    st.session_state.users = {}
if "jobcodes" not in st.session_state: # Will be populated by cached function
    st.session_state.jobcodes = {}
if "timesheets" not in st.session_state:
    st.session_state.timesheets = []
if "clients" not in st.session_state:
    st.session_state.clients = [] # Mock data, no API call
if "user_map" not in st.session_state: # Will be populated by cached function
    st.session_state.user_map = {}
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Dashboard"
if "date_range" not in st.session_state:
    today = datetime.now().date()
    st.session_state.date_range = (today - timedelta(days=30), today)
if "error_message" not in st.session_state:
    st.session_state.error_message = None
if "success_message" not in st.session_state:
    st.session_state.success_message = None
if "debug_info" not in st.session_state:
    st.session_state.debug_info = None
if "selected_client" not in st.session_state:
    st.session_state.selected_client = None
if "client_search" not in st.session_state:
    st.session_state.client_search = ""
# New session state variables for Calendar Tab
if "calendar_current_month_view" not in st.session_state:
    st.session_state.calendar_current_month_view = datetime.now().date().replace(day=1)
if "calendar_selected_day_entries" not in st.session_state:
    st.session_state.calendar_selected_day_entries = None
if "calendar_selected_date_for_details" not in st.session_state:
    st.session_state.calendar_selected_date_for_details = None
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        {"id": 1, "message": "New client added: Acme Corporation", "date": "2023-05-08", "read": False},
        {"id": 2, "message": "Timesheet approval pending", "date": "2023-05-07", "read": False},
        {"id": 3, "message": "Weekly report generated", "date": "2023-05-06", "read": True}
    ]

# --- Enhanced API Request Function with Retries ---
def make_api_request(endpoint, method="GET", params=None, data=None, timeout=30, max_retries=3, backoff_factor=0.5):
    """Make an API request to TSheets with retries, enhanced error handling, and timeout."""
    headers = {
        "Authorization": f"Bearer {st.session_state.api_token}",
        "Content-Type": "application/json"
    }
    
    st.session_state.error_message = None # Clear previous error for this attempt

    for attempt in range(max_retries):
        try:
            if method == "GET":
                response = requests.get(endpoint, headers=headers, params=params, timeout=timeout)
            elif method == "POST":
                response = requests.post(endpoint, headers=headers, json=data, timeout=timeout)
            elif method == "PUT":
                response = requests.put(endpoint, headers=headers, json=data, timeout=timeout)
            elif method == "DELETE":
                response = requests.delete(endpoint, headers=headers, params=params, timeout=timeout)
            else:
                st.session_state.error_message = f"Unsupported HTTP method: {method}"
                # No st.error here, let the main loop handle display
                return None

            # Store debug info for GET timesheets (can be expanded)
            if endpoint == TIMESHEETS_ENDPOINT and method == "GET":
                st.session_state.debug_info = {
                    "endpoint": endpoint,
                    "params": params,
                    "status_code": response.status_code,
                    "response_text": response.text[:500] 
                }
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 204: # Successful request with no content to return
                return {} # Return an empty dict (consistent for CRUD operations)
            elif response.status_code in [429, 500, 502, 503, 504]: # Retryable errors
                st.session_state.error_message = f"API Error: {response.status_code} - {response.text[:200]}. Retrying ({attempt + 1}/{max_retries})..."
                # st.warning(st.session_state.error_message) # Can show warning during retries
                time.sleep(backoff_factor * (2 ** attempt)) # Exponential backoff
                continue # Go to next attempt
            else: # Non-retryable client or server error
                error_details = response.text
                try:
                    json_error = response.json()
                    if isinstance(json_error, dict):
                        if "error" in json_error and "message" in json_error["error"]:
                            error_details = json_error["error"]["message"]
                        elif "message" in json_error:
                            error_details = json_error["message"]
                except ValueError:
                    pass # Keep response.text if not JSON
                st.session_state.error_message = f"API Error: {response.status_code} - {error_details}"
                return None # Failed after non-retryable error
            
        except requests.exceptions.Timeout:
            st.session_state.error_message = f"Request timed out after {timeout} seconds for {method} {endpoint}. Retrying ({attempt + 1}/{max_retries})..."
            # st.warning(st.session_state.error_message)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
        except requests.exceptions.RequestException as e:
            st.session_state.error_message = f"Request Error: {str(e)}. Retrying ({attempt + 1}/{max_retries})..."
            # st.warning(st.session_state.error_message)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
        except Exception as e:
            st.session_state.error_message = f"An unexpected error occurred: {str(e)}. Retrying ({attempt + 1}/{max_retries})..."
            # st.warning(st.session_state.error_message)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
    
    # If all retries fail
    if not st.session_state.error_message: # If loop finished without setting a specific final error
        st.session_state.error_message = f"Failed to connect to API after {max_retries} retries."
    return None

# --- Helper Functions with Caching ---
@st.cache_data(ttl=3600) # Cache for 1 hour
def fetch_users_data(_api_token_dependency): # Add dummy arg to make it refresh if token changes
    """Cached function to load users from TSheets API."""
    response = make_api_request(USERS_ENDPOINT, params={"active": "yes"})
    if response and "results" in response and "users" in response["results"]:
        users = response["results"]["users"]
        user_map = {}
        for user_id, user_data in users.items():
            full_name = f"{user_data.get("first_name", "")} {user_data.get("last_name", "").strip()}"
            user_map[int(user_id)] = full_name if full_name else f"User {user_id}"
        return users, user_map
    return {}, {}

@st.cache_data(ttl=3600) # Cache for 1 hour
def fetch_jobcodes_data(_api_token_dependency):
    """Cached function to load jobcodes from TSheets API."""
    response = make_api_request(JOBCODES_ENDPOINT, params={"active": "yes"})
    if response and "results" in response and "jobcodes" in response["results"]:
        return response["results"]["jobcodes"]
    return {}

def load_users():
    """Load users using cached function and update session state."""
    users_data, user_map_data = fetch_users_data(st.session_state.api_token)
    st.session_state.users = users_data
    st.session_state.user_map = user_map_data
    if not users_data and st.session_state.error_message:
        st.warning(f"Could not load users: {st.session_state.error_message}")
        st.session_state.error_message = None # Clear after showing warning

def load_jobcodes():
    """Load jobcodes using cached function and update session state."""
    jobcodes_data = fetch_jobcodes_data(st.session_state.api_token)
    st.session_state.jobcodes = jobcodes_data
    if not jobcodes_data and st.session_state.error_message:
        st.warning(f"Could not load job codes: {st.session_state.error_message}")
        st.session_state.error_message = None # Clear after showing warning

def authenticate():
    """Authenticate with TSheets API"""
    response = make_api_request(CURRENT_USER_ENDPOINT)
    if response and "results" in response and "users" in response["results"]:
        st.session_state.authenticated = True
        user_data = list(response["results"]["users"].values())[0]
        st.session_state.current_user = user_data
        # Clear caches on new authentication to ensure fresh data for new token/user
        fetch_users_data.clear()
        fetch_jobcodes_data.clear()
        load_initial_data() # Combined data loading
        st.session_state.last_refresh = datetime.now()
        return True
    else:
        st.session_state.authenticated = False
        if not st.session_state.error_message:
             st.session_state.error_message = "Authentication failed. Please check your API token and connection."
        return False

def load_initial_data():
    """Load all necessary initial data after authentication."""
    load_users()
    load_jobcodes()
    load_timesheets() # Loads for current user and date range
    load_clients() # Loads mock client data

def load_timesheets():
    """Load timesheets from TSheets API for the current user and date range."""
    if not st.session_state.current_user or "id" not in st.session_state.current_user:
        st.session_state.timesheets = []
        return

    today = datetime.now().date()
    end_date = min(st.session_state.date_range[1], today)
    start_date = min(st.session_state.date_range[0], end_date)
    
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    params = {
        "start_date": start_date_str,
        "end_date": end_date_str,
        "user_ids": st.session_state.current_user["id"],
        "supplemental_data": "yes" # To get jobcode info, etc.
    }
    response = make_api_request(TIMESHEETS_ENDPOINT, params=params)
    if response and "results" in response and "timesheets" in response["results"]:
        timesheets_dict = response["results"]["timesheets"]
        timesheets_list = list(timesheets_dict.values())
        timesheets_list.sort(key=lambda x: x.get("date", "1900-01-01"), reverse=True)
        st.session_state.timesheets = timesheets_list
    else:
        st.session_state.timesheets = []
        if not st.session_state.error_message:
             st.warning("Could not load timesheets or no timesheets found for the period.")
        # Error message is already set by make_api_request if it failed

# @st.cache_data # Clients are mock, no need to cache API call
def load_clients():
    """Load clients (mock data as per original)."""
    clients_data = [
        {
            "id": 1001, "name": "Acme Corporation", "contact": "John Doe", "email": "john.doe@acme.com", 
            "phone": "555-123-4567", "address": "123 Main St, Anytown, USA", "status": "active", 
            "industry": "Technology", "notes": "Key client for software development projects", 
            "created_date": "2023-01-15", "last_contact": "2023-04-28", 
            "projects": ["Website Redesign", "Mobile App Development"], "total_hours": 245.5, "billing_rate": 150,
            "avatar": "https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp&f=y"
        },
        {
            "id": 1002, "name": "Globex Industries", "contact": "Jane Smith", "email": "jane.smith@globex.com", 
            "phone": "555-987-6543", "address": "456 Oak Ave, Somewhere, USA", "status": "active", 
            "industry": "Manufacturing", "notes": "Ongoing maintenance contract", 
            "created_date": "2022-11-03", "last_contact": "2023-05-02", 
            "projects": ["Inventory System", "Quality Control App"], "total_hours": 187.25, "billing_rate": 125,
            "avatar": "https://www.gravatar.com/avatar/11111111111111111111111111111111?d=mp&f=y"
        },
        {
            "id": 1007,
            "name": "Oscorp Industries",
            "contact": "Norman Osborn",
            "email": "norman@oscorp.com",
            "phone": "555-GOBLIN",
            "address": "Oscorp Tower, New York, USA",
            "status": "active",
            "industry": "Research",
            "notes": "Military and scientific research",
            "created_date": "2022-10-20",
            "last_contact": "2023-04-15",
            "projects": ["Advanced Materials", "Bioengineering"],
            "total_hours": 198.25,
            "billing_rate": 225,
            "avatar": "https://www.gravatar.com/avatar/66666666666666666666666666666666?d=mp&f=y"
        }
    ]
    st.session_state.clients = clients_data

def format_duration(seconds):
    """Format duration in seconds to HH:MM:SS"""
    if pd.isna(seconds) or not isinstance(seconds, (int, float)) or seconds < 0:
        return "00:00:00"
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def format_duration_hours(seconds):
    """Format duration in seconds to decimal hours"""
    if pd.isna(seconds) or not isinstance(seconds, (int, float)) or seconds < 0:
        return "0.00"
    hours = seconds / 3600
    return f"{hours:.2f}"

def get_jobcode_name(jobcode_id):
    """Get jobcode name from jobcode ID using cached data."""
    if jobcode_id is None or pd.isna(jobcode_id): return "N/A"
    jobcode_id_str = str(int(jobcode_id))
    # Ensure jobcodes are loaded into session state if needed, or rely on initial load
    if not st.session_state.jobcodes: load_jobcodes() # Defensive load if empty
    if jobcode_id_str in st.session_state.jobcodes:
        return st.session_state.jobcodes[jobcode_id_str].get("name", f"Job {jobcode_id_str}")
    return f"Job {jobcode_id_str}"

def get_user_name(user_id):
    """Get user full name from user ID using cached data."""
    if user_id is None or pd.isna(user_id): return "N/A"
    user_id_int = int(user_id)
    if not st.session_state.user_map: load_users() # Defensive load if empty
    return st.session_state.user_map.get(user_id_int, f"User {user_id_int}")

def create_timesheet(data):
    """Create a new timesheet entry"""
    payload = {"data": [data]}
    response = make_api_request(TIMESHEETS_ENDPOINT, method="POST", data=payload)
    if response: 
        st.session_state.success_message = "Timesheet entry created successfully!"
        load_timesheets() # Refresh data
        return True
    # Error message set by make_api_request and displayed in main loop
    return False

def update_timesheet(timesheet_id, data):
    """Update an existing timesheet entry"""
    payload = {"data": [{"id": timesheet_id, **data}]}
    response = make_api_request(TIMESHEETS_ENDPOINT, method="PUT", data=payload)
    if response:
        st.session_state.success_message = "Timesheet entry updated successfully!"
        load_timesheets()
        return True
    return False

def delete_timesheet(timesheet_id):
    """Delete a timesheet entry"""
    response = make_api_request(f"{TIMESHEETS_ENDPOINT}", method="DELETE", params={"ids": timesheet_id})
    if response is not None: 
        st.session_state.success_message = "Timesheet entry deleted successfully!"
        load_timesheets()
        return True
    return False

@st.cache_data(max_entries=10, ttl=600) # Cache DataFrame conversion for 10 mins
def get_timesheet_dataframe(timesheets_list_tuple): # Use tuple for hashability
    """Convert timesheet data to a DataFrame for analysis and display. Cached."""
    timesheets_list = list(timesheets_list_tuple)
    if not timesheets_list:
        return pd.DataFrame()
    
    data = []
    for ts in timesheets_list:
        try:
            entry_date = datetime.strptime(ts["date"], "%Y-%m-%d").date() if isinstance(ts.get("date"), str) else ts.get("date")
            
            start_time, end_time = None, None
            if ts.get("type") == "regular" and ts.get("start") and ts.get("end"):
                try:
                    start_time = datetime.fromisoformat(ts["start"].replace("Z", "+00:00"))
                    end_time = datetime.fromisoformat(ts["end"].replace("Z", "+00:00"))
                except ValueError:
                    pass 
            
            duration_seconds = int(ts.get("duration", 0))

            data.append({
                "id": ts["id"],
                "date": entry_date,
                "date_str": entry_date.strftime("%Y-%m-%d") if entry_date else "N/A",
                "user_id": ts["user_id"],
                "user_name": get_user_name(ts["user_id"]),
                "jobcode_id": ts.get("jobcode_id"),
                "job_name": get_jobcode_name(ts.get("jobcode_id")),
                "type": ts["type"],
                "duration_seconds": duration_seconds,
                "duration_formatted": format_duration(duration_seconds),
                "duration_hours_decimal": format_duration_hours(duration_seconds),
                "start_time": start_time,
                "end_time": end_time,
                "notes": ts.get("notes", ""),
                "billable": ts.get("billable", False),
                "on_the_clock": ts.get("on_the_clock", False)
            })
        except Exception as e:
            # st.warning(f"Error processing timesheet entry ID {ts.get("id", "Unknown")}: {e}") # Avoid too many warnings
            print(f"Error processing timesheet entry ID {ts.get("id", "Unknown")}: {e}")
            continue 
            
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        if "week_number" not in df.columns:
            df["week_number"] = df["date"].dt.isocalendar().week
        if "year" not in df.columns:
            df["year"] = df["date"].dt.isocalendar().year
    return df

# --- NEW Performance Analytics Functions (from code_enhancements.py) ---
@st.cache_data(ttl=600)
def calculate_employee_performance_metrics(df_tuple, standard_workday_hours: float = 8.0, standard_workweek_hours: float = 40.0) -> dict:
    """Calculates detailed employee performance metrics from the timesheet DataFrame. Cached."""
    df = pd.DataFrame(list(df_tuple), columns=get_timesheet_dataframe(tuple([])).columns if not get_timesheet_dataframe(tuple([])).empty else None)
    if df.empty or "duration_seconds" not in df.columns or "date" not in df.columns:
        return {
            "total_hours_logged_seconds": 0, "total_hours_logged_formatted": "00:00:00", "total_hours_logged_decimal": "0.00",
            "num_days_worked": 0, "num_weeks_worked": 0, "avg_daily_hours_decimal": "0.00", "avg_weekly_hours_decimal": "0.00",
            "billable_hours_seconds": 0, "billable_hours_decimal": "0.00", "non_billable_hours_seconds": 0, "non_billable_hours_decimal": "0.00",
            "billable_percentage": 0, "daily_overtime_hours_decimal": "0.00", "weekly_overtime_hours_decimal": "0.00",
            "job_code_distribution_percent": {}, "job_code_distribution_hours": {},
            "avg_entries_per_day": "0.00", "avg_entries_per_week": "0.00",
            "utilization_rate_vs_logged": 0, "utilization_rate_vs_standard": 0,
        }

    df_copy = df.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy["duration_seconds"] = pd.to_numeric(df_copy["duration_seconds"], errors="coerce").fillna(0)
    
    if "billable" not in df_copy.columns:
         df_copy["billable"] = df_copy["job_name"].astype(str).str.contains("Development|Consulting|Billable Project", case=False, na=False)

    total_seconds = df_copy["duration_seconds"].sum()
    num_days_worked = df_copy["date"].nunique()

    if "week_number" not in df_copy.columns:
        df_copy["week_number"] = df_copy["date"].dt.isocalendar().week
    if "year" not in df_copy.columns:
        df_copy["year"] = df_copy["date"].dt.isocalendar().year
        
    num_weeks_worked = df_copy[["year", "week_number"]].drop_duplicates().shape[0]

    avg_daily_seconds = total_seconds / num_days_worked if num_days_worked > 0 else 0
    avg_weekly_seconds = total_seconds / num_weeks_worked if num_weeks_worked > 0 else 0

    billable_seconds = df_copy[df_copy["billable"] == True]["duration_seconds"].sum()
    non_billable_seconds = total_seconds - billable_seconds
    billable_percentage = (billable_seconds / total_seconds * 100) if total_seconds > 0 else 0

    daily_total_seconds = df_copy.groupby(df_copy["date"].dt.date)["duration_seconds"].sum()
    daily_hours = daily_total_seconds / 3600
    daily_overtime_hours = daily_hours[daily_hours > standard_workday_hours].apply(lambda x: x - standard_workday_hours).sum()

    weekly_total_seconds = df_copy.groupby(["year", "week_number"])["duration_seconds"].sum()
    weekly_hours = weekly_total_seconds / 3600
    weekly_overtime_hours = weekly_hours[weekly_hours > standard_workweek_hours].apply(lambda x: x - standard_workweek_hours).sum()

    job_distribution_seconds = df_copy.groupby("job_name")["duration_seconds"].sum()
    job_code_distribution_percent = (job_distribution_seconds / total_seconds * 100).round(2).to_dict() if total_seconds > 0 else {}
    job_code_distribution_hours = (job_distribution_seconds / 3600).round(2).to_dict()

    total_entries = len(df_copy)
    avg_entries_per_day = total_entries / num_days_worked if num_days_worked > 0 else 0
    avg_entries_per_week = total_entries / num_weeks_worked if num_weeks_worked > 0 else 0

    utilization_rate_vs_logged = billable_percentage
    standard_hours_for_period = num_days_worked * standard_workday_hours
    utilization_rate_vs_standard = (billable_seconds / 3600 / standard_hours_for_period * 100) if standard_hours_for_period > 0 else 0

    return {
        "total_hours_logged_seconds": total_seconds,
        "total_hours_logged_formatted": format_duration(total_seconds),
        "total_hours_logged_decimal": format_duration_hours(total_seconds),
        "num_days_worked": num_days_worked,
        "num_weeks_worked": num_weeks_worked,
        "avg_daily_hours_decimal": format_duration_hours(avg_daily_seconds),
        "avg_weekly_hours_decimal": format_duration_hours(avg_weekly_seconds),
        "billable_hours_seconds": billable_seconds,
        "billable_hours_decimal": format_duration_hours(billable_seconds),
        "non_billable_hours_seconds": non_billable_seconds,
        "non_billable_hours_decimal": format_duration_hours(non_billable_seconds),
        "billable_percentage": round(billable_percentage, 2),
        "daily_overtime_hours_decimal": f"{daily_overtime_hours:.2f}",
        "weekly_overtime_hours_decimal": f"{weekly_overtime_hours:.2f}",
        "job_code_distribution_percent": job_code_distribution_percent,
        "job_code_distribution_hours": job_code_distribution_hours,
        "avg_entries_per_day": f"{avg_entries_per_day:.2f}",
        "avg_entries_per_week": f"{avg_entries_per_week:.2f}",
        "utilization_rate_vs_logged": round(utilization_rate_vs_logged, 2),
        "utilization_rate_vs_standard": round(utilization_rate_vs_standard, 2),
    }

def display_performance_analytics_tab(df_timesheets: pd.DataFrame):
    """Displays the employee performance analytics tab with KPIs and charts."""
    st.markdown("<h2 class=\'section-header\'>Employee Performance Analytics</h2>", unsafe_allow_html=True)

    if df_timesheets.empty:
        st.warning("No timesheet data available for the selected period to calculate performance metrics.")
        return

    col1, col2 = st.columns(2)
    with col1:
        standard_workday = st.number_input("Standard Workday Hours", min_value=1.0, max_value=24.0, value=8.0, step=0.5, key="perf_workday_hours")
    with col2:
        standard_workweek = st.number_input("Standard Workweek Hours", min_value=1.0, max_value=168.0, value=40.0, step=1.0, key="perf_workweek_hours")

    # Convert DataFrame to tuple of tuples for caching `calculate_employee_performance_metrics`
    # This is a common pattern for caching functions that take DataFrames.
    # Ensure the order of columns is consistent if that matters for the function.
    # Here, we assume the function can handle a list of dicts or similar structure if direct tuple conversion is tricky.
    # For simplicity, if df_timesheets is already processed, we might not need deep conversion.
    # However, to be safe with caching, making it a hashable type is good.
    # One way: tuple(df_timesheets.itertuples(index=False, name=None))
    # Or, if the function is robust: just pass df_timesheets and rely on Streamlit's hashing.
    # Let's try passing the DataFrame directly and see if Streamlit handles it. If not, convert to tuple.
    metrics = calculate_employee_performance_metrics(tuple(map(tuple, df_timesheets.values)), standard_workday_hours=standard_workday, standard_workweek_hours=standard_workweek)

    st.markdown("---_</h3_><h3 class=\'subsection-header\'>Key Performance Indicators (KPIs)</h3>", unsafe_allow_html=True)
    cols_kpi1 = st.columns(3)
    cols_kpi1[0].metric("Total Hours Logged", metrics["total_hours_logged_decimal"] + " hrs", delta=metrics["total_hours_logged_formatted"])
    cols_kpi1[1].metric("Avg Daily Hours", metrics["avg_daily_hours_decimal"] + " hrs", help=f"{metrics["num_days_worked"]} days worked")
    cols_kpi1[2].metric("Avg Weekly Hours", metrics["avg_weekly_hours_decimal"] + " hrs", help=f"{metrics["num_weeks_worked"]} weeks worked")

    cols_kpi2 = st.columns(3)
    cols_kpi2[0].metric("Billable Hours", metrics["billable_hours_decimal"] + " hrs", delta=f"{metrics["billable_percentage"]} % of Total")
    cols_kpi2[1].metric("Non-Billable Hours", metrics["non_billable_hours_decimal"] + " hrs")
    cols_kpi2[2].metric("Utilization (vs Logged)", f"{metrics["utilization_rate_vs_logged"]} %", help="Billable Hours / Total Logged Hours")

    cols_kpi3 = st.columns(3)
    cols_kpi3[0].metric("Daily Overtime", metrics["daily_overtime_hours_decimal"] + " hrs")
    cols_kpi3[1].metric("Weekly Overtime", metrics["weekly_overtime_hours_decimal"] + " hrs")
    cols_kpi3[2].metric("Utilization (vs Standard)", f"{metrics["utilization_rate_vs_standard"]} %", help=f"Billable Hours / ({metrics["num_days_worked"]} days * {standard_workday} hrs/day)")

    st.markdown("---_</h3_><h3 class=\'subsection-header\'>Work Distribution & Patterns</h3>", unsafe_allow_html=True)
    col_dist1, col_dist2 = st.columns([2,1]) 
    with col_dist1:
        st.markdown("<h4>Hours per Job Code</h4>", unsafe_allow_html=True)
        if metrics["job_code_distribution_hours"]:
            job_df_data = ([{"Job Code": k, "Hours": v, "Percentage": metrics["job_code_distribution_percent"].get(k,0)} 
                           for k,v in metrics["job_code_distribution_hours"].items() if v > 0])
            if job_df_data:
                job_df = pd.DataFrame(job_df_data).sort_values("Hours", ascending=False)
                st.dataframe(job_df, height=min(300, len(job_df)*40 + 40), use_container_width=True)
                fig_job_pie = px.pie(job_df, values="Hours", names="Job Code", title="Job Code Hours Distribution")
                fig_job_pie.update_layout(legend_orientation="h")
                st.plotly_chart(fig_job_pie, use_container_width=True)
            else:
                st.info("No job code data with hours to display.")
        else:
            st.info("No job code data to display.")

    with col_dist2:
        st.metric("Avg. Entries per Day", metrics["avg_entries_per_day"])
        st.metric("Avg. Entries per Week", metrics["avg_entries_per_week"])
        st.markdown("<h4>Billable vs. Non-Billable</h4>", unsafe_allow_html=True)
        billable_data = pd.DataFrame({
            "Category": ["Billable", "Non-Billable"],
            "Hours": [float(metrics["billable_hours_decimal"]), float(metrics["non_billable_hours_decimal"])]
        })
        if billable_data["Hours"].sum() > 0:
            fig_billable_bar = px.bar(billable_data, x="Category", y="Hours", color="Category", title="Billable vs. Non-Billable Hours", text_auto=True)
            fig_billable_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_billable_bar, use_container_width=True)
        else:
            st.info("No billable/non-billable data.")

    st.markdown("---_</h3_><h3 class=\'subsection-header\'>Trends Over Time (Last 12 Weeks)</h3>", unsafe_allow_html=True)
    if not df_timesheets.empty and "week_number" in df_timesheets.columns and "year" in df_timesheets.columns:
        df_copy = df_timesheets.copy()
        df_copy["date"] = pd.to_datetime(df_copy["date"])
        if "week_number" not in df_copy.columns:
            df_copy["week_number"] = df_copy["date"].dt.isocalendar().week
        if "year" not in df_copy.columns:
            df_copy["year"] = df_copy["date"].dt.isocalendar().year
            
        weekly_summary = df_copy.groupby(["year", "week_number"])["duration_seconds"].sum().reset_index()
        weekly_summary["hours"] = weekly_summary["duration_seconds"] / 3600
        weekly_summary["week_label"] = weekly_summary["year"].astype(str) + "-W" + weekly_summary["week_number"].astype(str).str.zfill(2)
        weekly_summary = weekly_summary.sort_values(by="week_label", ascending=True).tail(12)

        if not weekly_summary.empty:
            fig_weekly_trend = px.line(weekly_summary, x="week_label", y="hours", title="Weekly Hours Logged (Last 12 Weeks)", markers=True)
            fig_weekly_trend.update_layout(xaxis_title="Week", yaxis_title="Total Hours")
            st.plotly_chart(fig_weekly_trend, use_container_width=True)
        else:
            st.info("Not enough data for weekly trend chart.")
    else:
        st.info("Weekly trend data requires \'week_number\' and \'year\' in timesheet details.")

# --- NEW Calendar View Functions (from code_enhancements.py) ---
@st.cache_data(ttl=600)
def get_timesheets_for_month_display(df_timesheets_tuple, year: int, month: int) -> dict:
    """Processes timesheets for a given month and groups them by day for calendar display. Cached."""
    df_timesheets = pd.DataFrame(list(df_timesheets_tuple), columns=get_timesheet_dataframe(tuple([])).columns if not get_timesheet_dataframe(tuple([])).empty else None)
    if df_timesheets.empty or "date" not in df_timesheets.columns:
        return {}
    
    df_copy = df_timesheets.copy()
    df_copy["date"] = pd.to_datetime(df_copy["date"])

    month_timesheets = df_copy[
        (df_copy["date"].dt.year == year) & (df_copy["date"].dt.month == month)
    ]

    entries_by_day = {}
    for index, ts_row in month_timesheets.iterrows():
        day = ts_row["date"].day
        if day not in entries_by_day:
            entries_by_day[day] = []
        
        notes_preview = str(ts_row.get("notes", ""))
        if len(notes_preview) > 25:
            notes_preview = notes_preview[:22] + "..."
        
        start_time_obj = ts_row.get("start_time")
        end_time_obj = ts_row.get("end_time")

        start_time_str = start_time_obj.strftime("%H:%M") if pd.notnull(start_time_obj) and hasattr(start_time_obj, "strftime") else ""
        end_time_str = end_time_obj.strftime("%H:%M") if pd.notnull(end_time_obj) and hasattr(end_time_obj, "strftime") else ""
        time_range = f"{start_time_str}-{end_time_str}" if start_time_str and end_time_str else "(Manual)"

        entries_by_day[day].append({
            "id": ts_row["id"],
            "job_name": ts_row.get("job_name", "N/A"),
            "duration_formatted": ts_row.get("duration_formatted", format_duration(ts_row.get("duration_seconds",0))),
            "notes_preview": notes_preview,
            "time_range": time_range,
            "duration_hours_decimal": float(ts_row.get("duration_hours_decimal", 0.0))
        })
    return entries_by_day

def display_timesheet_calendar_tab(df_timesheets: pd.DataFrame):
    """Displays an interactive monthly calendar with timesheet entries."""
    st.markdown("<h2 class=\'section-header\'>Timesheet Calendar</h2>", unsafe_allow_html=True)

    current_month_view = st.session_state.calendar_current_month_view
    
    cal_col1, cal_col2, cal_col3 = st.columns([1,2,1])
    with cal_col1:
        if st.button("⬅️ Previous Month", key="cal_prev_month_btn", use_container_width=True):
            st.session_state.calendar_current_month_view = (current_month_view - timedelta(days=1)).replace(day=1)
            st.session_state.calendar_selected_day_entries = None
            st.session_state.calendar_selected_date_for_details = None
            st.experimental_rerun()
    with cal_col2:
        st.markdown(f"<h3 style=\'text-align: center; margin-top:10px; margin-bottom:10px;\'>{current_month_view.strftime("%B %Y")}</h3>", unsafe_allow_html=True)
    with cal_col3:
        if st.button("Next Month ➡️", key="cal_next_month_btn", use_container_width=True):
            next_m = current_month_view.month + 1
            next_y = current_month_view.year
            if next_m > 12:
                next_m = 1
                next_y += 1
            st.session_state.calendar_current_month_view = date(next_y, next_m, 1)
            st.session_state.calendar_selected_day_entries = None
            st.session_state.calendar_selected_date_for_details = None
            st.experimental_rerun()

    df_timesheets_tuple = tuple(map(tuple, df_timesheets.values)) if not df_timesheets.empty else tuple()
    entries_this_month = get_timesheets_for_month_display(df_timesheets_tuple, current_month_view.year, current_month_view.month)

    month_calendar = calendar.monthcalendar(current_month_view.year, current_month_view.month)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    cols_weekdays = st.columns(7)
    for i, day_name in enumerate(weekdays):
        cols_weekdays[i].markdown(f"<div class=\'calendar-weekday\'>{day_name}</div>", unsafe_allow_html=True)

    for week in month_calendar:
        cols_days = st.columns(7)
        for i, day_num in enumerate(week):
            with cols_days[i]:
                if day_num == 0:
                    st.markdown("<div class=\'calendar-day other-month\'></div>", unsafe_allow_html=True)
                else:
                    current_day_date = date(current_month_view.year, current_month_view.month, day_num)
                    day_class = "calendar-day"
                    day_html_content = f"<span class=\'day-number\'>{day_num}</span>"
                    
                    if current_day_date == datetime.now().date(): day_class += " today"
                    if st.session_state.calendar_selected_date_for_details == current_day_date: day_class += " selected"
                    
                    total_hours_today = 0
                    entry_count = 0
                    if day_num in entries_this_month and entries_this_month[day_num]:
                        day_class += " has-entries"
                        day_html_content += "<span class=\'day-entry-indicator\'></span>"
                        entry_count = len(entries_this_month[day_num])
                        total_hours_today = sum(e.get("duration_hours_decimal", 0) for e in entries_this_month[day_num])
                        day_html_content += f"<span class=\'day-entry-summary\'>{entry_count} entr{ "y" if entry_count == 1 else "ies"}<br>{total_hours_today:.2f}h</span>"
                    
                    button_key = f"day_btn_{current_month_view.year}_{current_month_view.month}_{day_num}"
                    # Using st.markdown to create a clickable div as st.button styling is limited
                    # This is a more complex way but allows for full CSS control.
                    # However, Streamlit doesn\'t directly support JS onclick in markdown to trigger Python callbacks easily.
                    # A simpler approach is to use st.container() and then put a button inside it, or just use st.button and accept its limitations.
                    # Let\'s use a placeholder for the complex HTML button and then use a simple st.button for interaction.
                    # The provided CSS will style the div if we use markdown, but the click needs st.button.
                    
                    # We will use a simpler st.button and style it as best as possible with CSS for stButton
                    # The class application will be via a wrapper div if needed, but st.button itself is hard to style dynamically with many classes.
                    
                    # Create a container for each day to apply custom class for background
                    # This is a workaround to apply dynamic styling based on day state
                    container_html = f"<div class=\'{day_class}\'>"
                    container_html += f"  <span class=\'day-number\'>{day_num}</span>"
                    if day_num in entries_this_month and entries_this_month[day_num]:
                        container_html += "  <span class=\'day-entry-indicator\'></span>"
                        entry_count = len(entries_this_month[day_num])
                        total_hours_today = sum(e.get("duration_hours_decimal", 0) for e in entries_this_month[day_num])
                        container_html += f"  <span class=\'day-entry-summary\'>{entry_count} entr{ "y" if entry_count == 1 else "ies"}<br>{total_hours_today:.2f}h</span>"
                    container_html += "</div>"
                    
                    # Display the styled container as markdown (not clickable)
                    # st.markdown(container_html, unsafe_allow_html=True)
                    # Add an invisible button over it or a small visible button for interaction
                    # This is still not ideal. The best is a custom component.

                    # Simpler: Use st.button and rely on its state for selection visual cue, plus limited CSS.
                    # The CSS above has .calendar-day, .has-entries, .selected. These won\'t directly apply to st.button.
                    # The button label will be the day number. Help text can show details.
                    button_label = f"{day_num}"
                    if day_num in entries_this_month and entries_this_month[day_num]:
                        entry_count = len(entries_this_month[day_num])
                        total_hours_today = sum(e.get("duration_hours_decimal", 0) for e in entries_this_month[day_num])
                        button_label += f"\n{entry_count} entr{'y' if entry_count == 1 else 'ies'}\n{total_hours_today:.2f}h"

                    if st.button(label=button_label, key=button_key, help=f"View entries for {current_day_date.strftime("%b %d")}", use_container_width=True):
                        st.session_state.calendar_selected_date_for_details = current_day_date
                        st.session_state.calendar_selected_day_entries = entries_this_month.get(day_num, [])
                        st.experimental_rerun() 

    if st.session_state.calendar_selected_day_entries is not None and st.session_state.calendar_selected_date_for_details:
        st.markdown("---_</h3_><h3 class=\'subsection-header\'>Entries for " + st.session_state.calendar_selected_date_for_details.strftime("%B %d, %Y") + "</h3>", unsafe_allow_html=True)
        if not st.session_state.calendar_selected_day_entries:
            st.info("No entries for this day.")
        else:
            for entry in st.session_state.calendar_selected_day_entries:
                with st.container():
                    st.markdown(f"""
                    <div class=\'day-view-entry\'>
                        <div class=\'day-view-time\'><strong>Time:</strong> {entry["time_range"]}</div>
                        <div class=\'day-view-job\'><strong>Job:</strong> {entry["job_name"]}</div>
                        <div class=\'day-view-duration\'><strong>Duration:</strong> {entry["duration_formatted"]}</div>
                        <div class=\'day-view-notes\'><em>Notes:</em> {entry["notes_preview"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View Full Timesheet ##{entry["id"]}", key=f"view_cal_entry_{entry["id"]}", help="Navigate to Timesheets tab to view/edit this entry"):
                        st.session_state.active_tab = "⏰ Timesheets" # Switch tab
                        # How to pre-select or filter in timesheets tab is an advanced feature not yet built
                        st.info(f"Navigating to Timesheets. Full details for ID {entry["id"]} can be searched or managed there.")
                        st.experimental_rerun()

# --- Original Tab Display Functions (ensure they exist and are compatible) ---
def display_dashboard_tab(): 
    st.markdown("<h2 class=\'section-header\'>Dashboard</h2>", unsafe_allow_html=True)
    df_timesheets = get_timesheet_dataframe(tuple(st.session_state.timesheets))

    if df_timesheets.empty:
        st.info("No timesheet data to display on dashboard. Try adjusting the date range or refreshing.")
        return

    total_hours = df_timesheets["duration_seconds"].sum() / 3600
    total_entries = len(df_timesheets)
    avg_hours_entry = total_hours / total_entries if total_entries > 0 else 0
    num_active_jobs = df_timesheets["job_name"].nunique()

    st.markdown("<h3 class=\'subsection-header\'>Overview</h3>", unsafe_allow_html=True)
    cols_overview = st.columns(4)
    cols_overview[0].metric("Total Hours Logged", f"{total_hours:.2f} hrs")
    cols_overview[1].metric("Total Timesheet Entries", f"{total_entries}")
    cols_overview[2].metric("Avg Hours per Entry", f"{avg_hours_entry:.2f} hrs")
    cols_overview[3].metric("Active Job Codes", f"{num_active_jobs}")

    st.markdown("---_</h3_><h3 class=\'subsection-header\'>Recent Activity & Trends</h3>", unsafe_allow_html=True)
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("<h4>Hours by Job Code (Top 5)</h4>", unsafe_allow_html=True)
        job_hours = df_timesheets.groupby("job_name")["duration_seconds"].sum().div(3600).nlargest(5)
        if not job_hours.empty:
            fig_job_hours = px.bar(job_hours, x=job_hours.index, y=job_hours.values, labels={"y":"Total Hours", "x":"Job Code"}, text_auto=True)
            fig_job_hours.update_layout(showlegend=False)
            st.plotly_chart(fig_job_hours, use_container_width=True)
        else:
            st.info("No job code data for chart.")

    with row1_col2:
        st.markdown("<h4>Daily Hours Trend (Last 7 Displayed Days)</h4>", unsafe_allow_html=True)
        # Ensure date is datetime for Grouper
        df_timesheets_sorted = df_timesheets.copy()
        df_timesheets_sorted["date"] = pd.to_datetime(df_timesheets_sorted["date"])
        daily_hours = df_timesheets_sorted.set_index("date").groupby(pd.Grouper(freq="D"))["duration_seconds"].sum().div(3600)
        daily_hours = daily_hours[daily_hours > 0].nlargest(7) # Get 7 days with actual hours
        if not daily_hours.empty:
            fig_daily_trend = px.line(daily_hours.sort_index(), x=daily_hours.index, y=daily_hours.values, markers=True, labels={"y":"Total Hours", "x":"Date"})
            st.plotly_chart(fig_daily_trend, use_container_width=True)
        else:
            st.info("No daily trend data for chart.")

    st.markdown("<h4>Recent Timesheet Entries (Top 5)</h4>", unsafe_allow_html=True)
    st.dataframe(df_timesheets[["date_str", "job_name", "duration_formatted", "notes"]].head(), use_container_width=True)

def display_timesheets_tab():
    st.markdown("<h2 class=\'section-header\'>Manage Timesheets</h2>", unsafe_allow_html=True)
    action = st.selectbox("Choose action:", ["View Timesheets", "Create New Timesheet", "Edit Timesheet", "Delete Timesheet"], key="ts_action")

    if action == "View Timesheets":
        st.markdown("<h3 class=\'subsection-header\'>Your Timesheets</h3>", unsafe_allow_html=True)
        if not st.session_state.timesheets:
            st.info("No timesheets found for the selected period. Try adjusting date range or refreshing.")
        else:
            df_display = get_timesheet_dataframe(tuple(st.session_state.timesheets))
            if not df_display.empty:
                st.dataframe(df_display[["id", "date_str", "job_name", "duration_formatted", "notes", "billable"]], use_container_width=True)
            else:
                st.info("No timesheets to display after processing.")

    elif action == "Create New Timesheet":
        st.markdown("<h3 class=\'subsection-header\'>Create New Timesheet Entry</h3>", unsafe_allow_html=True)
        with st.form("create_ts_form", clear_on_submit=True):
            ts_date = st.date_input("Date", value=datetime.now().date(), key="create_ts_date")
            job_options = {v["name"]: k for k, v in st.session_state.jobcodes.items()} if st.session_state.jobcodes else {}
            if not job_options:
                st.warning("No job codes loaded. Please check API connection or refresh.")
                selected_job_name = st.text_input("Job Code (Enter ID if names not loaded)", key="create_ts_job_fallback")
                job_id = selected_job_name # User must enter ID
            else:
                selected_job_name = st.selectbox("Job Code", options=list(job_options.keys()), key="create_ts_job")
                job_id = job_options.get(selected_job_name)
            
            ts_type = st.selectbox("Type", ["regular", "manual"], key="create_ts_type")
            start_time_input, end_time_input, duration_seconds = None, None, None
            if ts_type == "regular":
                start_time_input = st.time_input("Start Time", key="create_ts_start", value=None)
                end_time_input = st.time_input("End Time", key="create_ts_end", value=None)
            else: # manual
                duration_hours_input = st.number_input("Duration (hours)", min_value=0.0, step=0.25, key="create_ts_duration_manual")
                duration_seconds = int(duration_hours_input * 3600)

            notes = st.text_area("Notes", key="create_ts_notes")
            billable_input = st.checkbox("Billable", value=True, key="create_ts_billable")
            
            submitted = st.form_submit_button("Create Timesheet")
            if submitted:
                if not job_id:
                    st.error("Job Code is required.")
                    return
                new_ts_data = {
                    "type": ts_type,
                    "date": ts_date.strftime("%Y-%m-%d"),
                    "user_id": st.session_state.current_user["id"],
                    "jobcode_id": job_id,
                    "notes": notes,
                    "billable": billable_input
                }
                if ts_type == "regular":
                    if start_time_input and end_time_input:
                        start_dt = datetime.combine(ts_date, start_time_input)
                        end_dt = datetime.combine(ts_date, end_time_input)
                        if end_dt <= start_dt:
                            st.error("End time must be after start time.")
                            return
                        new_ts_data["start"] = start_dt.isoformat() + "Z" # TSheets expects Zulu time usually
                        new_ts_data["end"] = end_dt.isoformat() + "Z"
                    else:
                        st.error("Start and End times are required for regular entries.")
                        return
                elif ts_type == "manual":
                    if duration_seconds is not None and duration_seconds > 0:
                        new_ts_data["duration"] = duration_seconds
                    else:
                        st.error("Duration must be greater than 0 for manual entries.")
                        return
                
                if create_timesheet(new_ts_data):
                    st.success("Timesheet creation initiated!") # Message set by create_timesheet on success
                else:
                    st.error(f"Failed to create timesheet. {st.session_state.error_message or 'Unknown error.'}")
    
    elif action == "Edit Timesheet":
        st.markdown("<h3 class=\'subsection-header\'>Edit Timesheet Entry</h3>", unsafe_allow_html=True)
        df_display = get_timesheet_dataframe(tuple(st.session_state.timesheets))
        if df_display.empty:
            st.info("No timesheets to edit.")
            return
        
        timesheet_options = {f"{row.date_str} - {row.job_name} ({row.duration_formatted})": row.id for index, row in df_display.iterrows()}
        if not timesheet_options:
            st.info("No timesheets available to select for editing.")
            return
            
        selected_ts_display = st.selectbox("Select Timesheet to Edit", options=list(timesheet_options.keys()), key="edit_ts_select")
        timesheet_id_to_edit = timesheet_options.get(selected_ts_display)

        if timesheet_id_to_edit:
            original_ts = next((ts for ts in st.session_state.timesheets if ts["id"] == timesheet_id_to_edit), None)
            if not original_ts:
                st.error("Selected timesheet not found.")
                return

            with st.form("edit_ts_form"): 
                edit_date = st.date_input("Date", value=datetime.strptime(original_ts["date"], "%Y-%m-%d").date(), key=f"edit_ts_date_{timesheet_id_to_edit}")
                
                job_options_edit = {v["name"]: k for k, v in st.session_state.jobcodes.items()} if st.session_state.jobcodes else {}
                job_names_edit = list(job_options_edit.keys())
                current_job_name_edit = get_jobcode_name(original_ts.get("jobcode_id"))
                try:
                    current_job_index_edit = job_names_edit.index(current_job_name_edit) if current_job_name_edit in job_names_edit else 0
                except ValueError:
                    current_job_index_edit = 0
                
                selected_job_name_edit = st.selectbox("Job Code", options=job_names_edit, index=current_job_index_edit, key=f"edit_ts_job_{timesheet_id_to_edit}")
                job_id_edit = job_options_edit.get(selected_job_name_edit)

                edit_notes = st.text_area("Notes", value=original_ts.get("notes", ""), key=f"edit_ts_notes_{timesheet_id_to_edit}")
                edit_billable = st.checkbox("Billable", value=original_ts.get("billable", False), key=f"edit_ts_billable_{timesheet_id_to_edit}")
                
                # Duration/Start/End editing (simplified - assumes manual type for edit simplicity here)
                # A full implementation would handle regular vs manual type changes and respective fields.
                original_duration_hours = original_ts.get("duration", 0) / 3600
                edit_duration_hours = st.number_input("Duration (hours) - for manual type", value=original_duration_hours, min_value=0.0, step=0.25, key=f"edit_ts_duration_{timesheet_id_to_edit}")
                
                submitted_edit = st.form_submit_button("Update Timesheet")
                if submitted_edit:
                    updated_data = {
                        "date": edit_date.strftime("%Y-%m-%d"),
                        "jobcode_id": job_id_edit,
                        "notes": edit_notes,
                        "billable": edit_billable,
                        "type": "manual", # Simplification: forcing update as manual type
                        "duration": int(edit_duration_hours * 3600)
                        # Add start/end if type regular is maintained and edited
                    }
                    if update_timesheet(timesheet_id_to_edit, updated_data):
                        st.success("Timesheet updated!")
                        # No st.experimental_rerun() here, success message will show, data reloads in update_timesheet
                    else:
                        st.error(f"Failed to update timesheet. {st.session_state.error_message or 'Unknown error.'}")
    
    elif action == "Delete Timesheet":
        st.markdown("<h3 class=\'subsection-header\'>Delete Timesheet Entry</h3>", unsafe_allow_html=True)
        df_display_del = get_timesheet_dataframe(tuple(st.session_state.timesheets))
        if df_display_del.empty:
            st.info("No timesheets to delete.")
            return

        timesheet_options_del = {f"{row.date_str} - {row.job_name} ({row.duration_formatted})": row.id for index, row in df_display_del.iterrows()}
        if not timesheet_options_del:
            st.info("No timesheets available to select for deletion.")
            return

        selected_ts_display_del = st.selectbox("Select Timesheet to Delete", options=list(timesheet_options_del.keys()), key="delete_ts_select")
        timesheet_id_to_delete = timesheet_options_del.get(selected_ts_display_del)

        if timesheet_id_to_delete:
            if st.button("Confirm Delete Timesheet", key=f"confirm_delete_ts_{timesheet_id_to_delete}"):
                if delete_timesheet(timesheet_id_to_delete):
                    st.success("Timesheet deleted!")
                    # No st.experimental_rerun() here, success message will show, data reloads in delete_timesheet
                else:
                    st.error(f'Failed to delete timesheet. {st.session_state.error_message or "Unknown error."}')

def display_reports_tab():
    st.markdown("<h2 class=\'section-header\'>Reports & Analytics</h2>", unsafe_allow_html=True)
    df_reports = get_timesheet_dataframe(tuple(st.session_state.timesheets))
    if df_reports.empty:
        st.info("No data for reports. Please check date range or refresh.")
        return

    st.markdown("<h3 class=\'subsection-header\'>Timesheet Summary Report</h3>", unsafe_allow_html=True)
    report_type = st.selectbox("Group By", ["Job Code", "User", "Day", "Week"], key="report_group_by")

    if report_type == "Job Code":
        summary_df = df_reports.groupby("job_name")["duration_seconds"].sum().div(3600).reset_index()
        summary_df.columns = ["Job Code", "Total Hours"]
    elif report_type == "User": # Only current user in this version, but for future expansion
        summary_df = df_reports.groupby("user_name")["duration_seconds"].sum().div(3600).reset_index()
        summary_df.columns = ["User", "Total Hours"]
    elif report_type == "Day":
        summary_df = df_reports.groupby("date_str")["duration_seconds"].sum().div(3600).reset_index()
        summary_df.columns = ["Date", "Total Hours"]
        summary_df = summary_df.sort_values(by="Date", ascending=False)
    elif report_type == "Week":
        df_reports["week_label"] = df_reports["year"].astype(str) + "-W" + df_reports["week_number"].astype(str).str.zfill(2)
        summary_df = df_reports.groupby("week_label")["duration_seconds"].sum().div(3600).reset_index()
        summary_df.columns = ["Week", "Total Hours"]
        summary_df = summary_df.sort_values(by="Week", ascending=False)
    else:
        summary_df = pd.DataFrame()

    if not summary_df.empty:
        st.dataframe(summary_df.sort_values(by="Total Hours", ascending=False), use_container_width=True)
        csv = summary_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label=f"Download {report_type} Summary as CSV",
            data=csv,
            file_name=f"timesheet_summary_by_{report_type.lower().replace(\" \", \"_\")}.csv",
            mime="text/csv",
            key=f"download_{report_type}_csv"
        )
    else:
        st.info("No data to display for this grouping.")

def display_clients_tab():
    st.markdown("<h2 class=\'section-header\'>Client Management (Mock)</h2>", unsafe_allow_html=True)
    if not st.session_state.clients:
        st.info("No client data available.")
        load_clients() # Ensure mock clients are loaded if empty
        if not st.session_state.clients: # Still no clients after attempt
             st.warning("Failed to load mock client data.")
             return

    for client in st.session_state.clients:
        with st.expander(f"{client["name"]} ({client["status"]})"):
            st.markdown(f"**Contact:** {client["contact"]} ({client["email"]})")
            st.markdown(f"**Industry:** {client["industry"]}")
            st.markdown(f"**Total Hours Logged (Example):** {client["total_hours"]}")
            st.markdown(f"**Notes:** {client["notes"]}")

def display_settings_tab():
    st.markdown("<h2 class=\'section-header\'>Settings</h2>", unsafe_allow_html=True)
    st.markdown("<h3 class=\'subsection-header\'>API Token</h3>", unsafe_allow_html=True)
    st.text_input("Current API Token (hidden)", value="*" * len(st.session_state.api_token) if st.session_state.api_token else "Not Set", type="password", disabled=True)
    new_token = st.text_input("Enter New API Token (Optional)", type="password", key="new_api_token_input")
    if st.button("Update Token & Re-authenticate", key="update_token_btn"):
        if new_token:
            st.session_state.api_token = new_token
            st.session_state.authenticated = False 
            fetch_users_data.clear() # Clear cache on token change
            fetch_jobcodes_data.clear()
            get_timesheet_dataframe.clear() # Clear timesheet processing cache
            calculate_employee_performance_metrics.clear()
            get_timesheets_for_month_display.clear()
            if authenticate():
                st.success("API Token updated and re-authenticated successfully!")
            else:
                st.error(f"Failed to re-authenticate with new token. {st.session_state.error_message or \"Check token and connection.\"}")
            st.experimental_rerun()
        else:
            st.warning("Please enter a new API token to update.")

    st.markdown("<h3 class=\'subsection-header\'>Date Range for Data</h3>", unsafe_allow_html=True)
    current_start_date, current_end_date = st.session_state.date_range
    new_date_range = st.date_input(
        "Select Date Range",
        value=(current_start_date, current_end_date),
        max_value=datetime.now().date(),
        key="settings_date_range"
    )
    if (new_date_range[0], new_date_range[1]) != (current_start_date, current_end_date):
        st.session_state.date_range = (new_date_range[0], new_date_range[1])
        st.info("Date range updated. Refresh data or navigate to see changes.")
        if st.session_state.authenticated:
            with st.spinner("Reloading timesheets for new date range..."):
                load_timesheets() 
            get_timesheet_dataframe.clear() # Clear relevant caches
            calculate_employee_performance_metrics.clear()
            get_timesheets_for_month_display.clear()
            st.experimental_rerun()
    
    st.markdown("<h3 class=\'subsection-header\'>Cache Management</h3>", unsafe_allow_html=True)
    if st.button("Clear All App Caches", key="clear_all_caches_btn"):
        fetch_users_data.clear()
        fetch_jobcodes_data.clear()
        get_timesheet_dataframe.clear()
        calculate_employee_performance_metrics.clear()
        get_timesheets_for_month_display.clear()
        st.success("All application data caches have been cleared. Data will be re-fetched on next load.")
        st.experimental_rerun()

# --- Main Application Logic ---
def main():
    st.markdown("<h1 class=\'main-header\'>TSheets CRM Manager Pro ⏱️</h1>", unsafe_allow_html=True)

    with st.sidebar:
        # Using a publicly accessible, generic logo URL for placeholder
        try:
            # Attempt to load a local logo if available, otherwise use URL
            # For this example, we will stick to a URL to avoid file path issues in deployment
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Google_Clock_Icon.svg/1024px-Google_Clock_Icon.svg.png", width=150, caption="App Logo")
        except Exception as e:
            st.error(f"Logo Error: {e}") # Should not happen with URL
            st.write("App Logo") # Fallback text

        st.markdown("## Authentication")
        if not st.session_state.authenticated:
            api_token_input = st.text_input("Enter your TSheets API Token", type="password", key="api_token_input_sidebar", help="Your personal TSheets API access token.")
            if st.button("Login", key="login_button_sidebar", use_container_width=True):
                if api_token_input:
                    st.session_state.api_token = api_token_input
                    with st.spinner("Authenticating..."):
                        if authenticate():
                            st.success("Authentication successful!")
                            st.experimental_rerun()
                        else:
                            # Error message is set in authenticate() or make_api_request()
                            st.error(f"{st.session_state.error_message or \"Authentication failed. Check token and connection.\"}")
                else:
                    st.warning("Please enter an API token.")
        else:
            if st.session_state.current_user:
                st.markdown(f"Logged in as: **{st.session_state.current_user.get("first_name", "")} {st.session_state.current_user.get("last_name", "")}**")
                st.caption(f"User ID: {st.session_state.current_user.get("id")}")
            if st.button("Logout", key="logout_button_sidebar", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.api_token = ""
                st.session_state.current_user = None
                st.session_state.timesheets = [] 
                st.session_state.users = {}
                st.session_state.jobcodes = {}
                st.session_state.clients = []
                # Clear all caches on logout
                fetch_users_data.clear()
                fetch_jobcodes_data.clear()
                get_timesheet_dataframe.clear()
                calculate_employee_performance_metrics.clear()
                get_timesheets_for_month_display.clear()
                st.success("Logged out successfully.")
                st.experimental_rerun()
            
            st.markdown("---_</h3_>")
            st.markdown("## Data Refresh")
            if st.button("Refresh All Data", key="refresh_data_sidebar", use_container_width=True):
                with st.spinner("Refreshing all data..."):
                    fetch_users_data.clear() 
                    fetch_jobcodes_data.clear()
                    # Timesheets are not globally cached by a decorator, load_timesheets fetches fresh
                    load_initial_data() # This will call load_users, load_jobcodes, load_timesheets
                    st.session_state.last_refresh = datetime.now()
                    # Clear specific data processing caches that depend on timesheets
                    get_timesheet_dataframe.clear()
                    calculate_employee_performance_metrics.clear()
                    get_timesheets_for_month_display.clear()
                st.success("All data refreshed!")
                st.experimental_rerun()
            if st.session_state.last_refresh:
                st.caption(f"Last refresh: {st.session_state.last_refresh.strftime("%Y-%m-%d %H:%M:%S")}")

    # Display messages (success/error/warning) centrally
    if st.session_state.success_message:
        st.markdown(f"<div class=\'success-message\'>{st.session_state.success_message}</div>", unsafe_allow_html=True)
        st.session_state.success_message = None 
    if st.session_state.error_message:
        # Check if it\'s a warning-level message from retries
        if "Retrying" in st.session_state.error_message:
            st.markdown(f"<div class=\'warning-message\'>{st.session_state.error_message}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class=\'error-message\'>{st.session_state.error_message}</div>", unsafe_allow_html=True)
        # Do not clear error_message here, let it persist until next successful action or explicit clear
        # st.session_state.error_message = None 

    if st.session_state.authenticated:
        df_for_tabs = get_timesheet_dataframe(tuple(st.session_state.timesheets))

        tab_titles = [
            "📊 Dashboard", "⏰ Timesheets", "📈 Reports", 
            "💡 Performance Analytics", "📅 Timesheet Calendar", 
            "👥 Clients (Mock)", "⚙️ Settings"
        ]
        
        # If active_tab from session state is valid, use it, else default to first tab
        try:
            default_tab_index = tab_titles.index(st.session_state.active_tab)
        except ValueError:
            default_tab_index = 0
            st.session_state.active_tab = tab_titles[0]

        # The st.tabs function does not have a direct way to set the default selected tab via an argument.
        # It always defaults to the first tab upon initial rendering or full rerun if state isn\'t managed.
        # To control the active tab, one would typically manage this with query parameters or more complex state handling.
        # For this structure, we rely on Streamlit\'s default behavior for tabs.
        # The st.session_state.active_tab is more for internal logic if we were to build custom tab-like navigation.

        tabs = st.tabs(tab_titles)
        
        with tabs[0]: # Dashboard
            display_dashboard_tab() 
        with tabs[1]: # Timesheets
            display_timesheets_tab()
        with tabs[2]: # Reports
            display_reports_tab()
        with tabs[3]: # Performance Analytics
            display_performance_analytics_tab(df_for_tabs)
        with tabs[4]: # Timesheet Calendar
            display_timesheet_calendar_tab(df_for_tabs)
        with tabs[5]: # Clients
            display_clients_tab()
        with tabs[6]: # Settings
            display_settings_tab()

    elif not st.session_state.api_token and not st.session_state.error_message:
        st.info("Please enter your TSheets API Token in the sidebar to login and use the application.")
    elif st.session_state.error_message and "Authentication failed" in st.session_state.error_message:
        pass # Error is already displayed above
    
    st.markdown("---_</h3_>")
    st.markdown("<div class=\'footer\'>TSheets CRM Manager Pro © 2024-2025 | Enhanced Features by Manus</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
