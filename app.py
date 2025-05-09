import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta, date
import time
import plotly.express as px
import plotly.graph_objects as go
import calendar
import traceback

# Set page configuration
st.set_page_config(
    page_title="TSheets CRM Manager Pro", 
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBCODES_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"
CURRENT_USER_ENDPOINT = f"{BASE_URL}/current_user"
CLIENTS_ENDPOINT = f"{BASE_URL}/customfields"  # Using customfields for client data

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables with defaults"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "api_token" not in st.session_state:
        st.session_state.api_token = ""
    if "current_user" not in st.session_state:
        st.session_state.current_user = None
    if "users" not in st.session_state:
        st.session_state.users = {}
    if "jobcodes" not in st.session_state:
        st.session_state.jobcodes = {}
    if "timesheets" not in st.session_state:
        st.session_state.timesheets = []
    if "clients" not in st.session_state:
        st.session_state.clients = []
    if "user_map" not in st.session_state:
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
    # Calendar Tab variables
    if "calendar_current_month_view" not in st.session_state:
        st.session_state.calendar_current_month_view = datetime.now().date().replace(day=1)
    if "calendar_selected_day_entries" not in st.session_state:
        st.session_state.calendar_selected_day_entries = None
    if "calendar_selected_date_for_details" not in st.session_state:
        st.session_state.calendar_selected_date_for_details = None
    if "notifications" not in st.session_state:
        st.session_state.notifications = []
    if "api_request_count" not in st.session_state:
        st.session_state.api_request_count = 0
    if "last_api_status" not in st.session_state:
        st.session_state.last_api_status = None
    if "debug_mode" not in st.session_state:
        st.session_state.debug_mode = False
    if "api_logs" not in st.session_state:
        st.session_state.api_logs = []
    if "mock_data_mode" not in st.session_state:
        st.session_state.mock_data_mode = False
    if "deleted_timesheets" not in st.session_state:
        st.session_state.deleted_timesheets = []

# Initialize session state
init_session_state()

# --- Enhanced API Request Function with Retries, Connection Diagnostics, and Detailed Logging ---
def make_api_request(endpoint, method="GET", params=None, data=None, timeout=30, max_retries=3, backoff_factor=0.5):
    """
    Make an API request to TSheets with retries, enhanced error handling, timeout, and connection diagnostics.
    """
    # If mock data mode is enabled, return mock data instead of making real API calls
    if st.session_state.mock_data_mode:
        return get_mock_data(endpoint, method, params, data)

    headers = {
        "Authorization": f"Bearer {st.session_state.api_token}",
        "Content-Type": "application/json"
    }

    # Clear previous error for this attempt
    st.session_state.error_message = None

    # Track API request count
    st.session_state.api_request_count += 1
    request_id = f"req_{st.session_state.api_request_count}"

    # Prepare debug info
    debug_info = {
        "request_id": request_id,
        "endpoint": endpoint,
        "method": method,
        "params": params,
        "data_summary": str(data)[:100] + "..." if data and len(str(data)) > 100 else data,
        "attempts": [],
        "final_status": None,
        "timestamp": datetime.now().isoformat()
    }

    # Add to API logs
    st.session_state.api_logs.append({
        "timestamp": datetime.now().isoformat(),
        "endpoint": endpoint,
        "method": method,
        "request_id": request_id
    })

    for attempt in range(max_retries):
        attempt_start_time = time.time()
        attempt_info = {
            "attempt_number": attempt + 1,
            "timestamp": datetime.now().isoformat(),
            "status_code": None,
            "response_summary": None,
            "error": None,
            "duration_ms": None
        }
        
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
                attempt_info["error"] = st.session_state.error_message
                debug_info["attempts"].append(attempt_info)
                debug_info["final_status"] = "error"
                st.session_state.debug_info = debug_info
                st.session_state.last_api_status = "error"
                return None

            # Calculate request duration
            attempt_duration = (time.time() - attempt_start_time) * 1000  # ms
            attempt_info["duration_ms"] = round(attempt_duration, 2)
            attempt_info["status_code"] = response.status_code
            
            # Store response summary
            try:
                response_text = response.text[:500]
                attempt_info["response_summary"] = response_text
            except:
                attempt_info["response_summary"] = "Could not extract response text"
            
            # Handle response based on status code
            if response.status_code == 200:
                try:
                    json_response = response.json()
                    debug_info["attempts"].append(attempt_info)
                    debug_info["final_status"] = "success"
                    st.session_state.debug_info = debug_info
                    st.session_state.last_api_status = "success"
                    return json_response
                except json.JSONDecodeError as e:
                    error_message = f"Failed to parse JSON response: {str(e)}"
                    st.session_state.error_message = error_message
                    attempt_info["error"] = error_message
                    debug_info["attempts"].append(attempt_info)
                    debug_info["final_status"] = "error"
                    st.session_state.debug_info = debug_info
                    st.session_state.last_api_status = "error"
                    return None
            elif response.status_code == 204:  # Successful request with no content
                debug_info["attempts"].append(attempt_info)
                debug_info["final_status"] = "success"
                st.session_state.debug_info = debug_info
                st.session_state.last_api_status = "success"
                return {}  # Return an empty dict
            elif response.status_code in [429, 500, 502, 503, 504]:  # Retryable errors
                error_message = f"API Error: {response.status_code} - {response.text[:200]}. Retrying ({attempt + 1}/{max_retries})..."
                st.session_state.error_message = error_message
                attempt_info["error"] = error_message
                debug_info["attempts"].append(attempt_info)
                
                # Use exponential backoff
                wait_time = backoff_factor * (2 ** attempt)
                time.sleep(wait_time)
                continue  # Go to next attempt
            else:  # Non-retryable client or server error
                # Try to extract detailed error message from response
                error_details = response.text
                try:
                    json_error = response.json()
                    if isinstance(json_error, dict):
                        if "error" in json_error and "message" in json_error["error"]:
                            error_details = json_error["error"]["message"]
                        elif "message" in json_error:
                            error_details = json_error["message"]
                except ValueError:
                    pass  # Keep response.text if not JSON
                
                error_message = f"API Error: {response.status_code} - {error_details}"
                st.session_state.error_message = error_message
                attempt_info["error"] = error_message
                debug_info["attempts"].append(attempt_info)
                debug_info["final_status"] = "error"
                st.session_state.debug_info = debug_info
                st.session_state.last_api_status = "error"
                return None  # Failed after non-retryable error
            
        except requests.exceptions.Timeout:
            error_message = f"Request timed out after {timeout} seconds for {method} {endpoint}. Retrying ({attempt + 1}/{max_retries})..."
            st.session_state.error_message = error_message
            attempt_info["error"] = error_message
            debug_info["attempts"].append(attempt_info)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
        except requests.exceptions.ConnectionError:
            error_message = f"Connection error for {method} {endpoint}. Check network or API endpoint. Retrying ({attempt + 1}/{max_retries})..."
            st.session_state.error_message = error_message
            attempt_info["error"] = error_message
            debug_info["attempts"].append(attempt_info)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
        except requests.exceptions.RequestException as e:
            error_message = f"Request Error: {str(e)}. Retrying ({attempt + 1}/{max_retries})..."
            st.session_state.error_message = error_message
            attempt_info["error"] = error_message
            debug_info["attempts"].append(attempt_info)
            time.sleep(backoff_factor * (2 ** attempt))
            continue
        except Exception as e:
            error_message = f"An unexpected error occurred: {str(e)}. Retrying ({attempt + 1}/{max_retries})..."
            st.session_state.error_message = error_message
            attempt_info["error"] = error_message
            attempt_info["traceback"] = traceback.format_exc()
            debug_info["attempts"].append(attempt_info)
            time.sleep(backoff_factor * (2 ** attempt))
            continue

    # If all retries fail
    if not st.session_state.error_message:  # If loop finished without setting a specific final error
        st.session_state.error_message = f"Failed to connect to API after {max_retries} retries."

    debug_info["final_status"] = "failed_all_retries"
    st.session_state.debug_info = debug_info
    st.session_state.last_api_status = "failed"
    return None

# --- Mock Data Functions ---
def get_mock_data(endpoint, method, params=None, data=None):
    """Return mock data for testing when API is unavailable"""
    if endpoint == CURRENT_USER_ENDPOINT:
        return {
            "results": {
                "users": {
                    "123456": {
                        "id": 123456,
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test.user@example.com",
                        "username": "testuser",
                        "active": True,
                        "employee_number": 1001,
                        "company_id": 12345
                    }
                }
            }
        }
    elif endpoint == USERS_ENDPOINT:
        return {
            "results": {
                "users": {
                    "123456": {
                        "id": 123456,
                        "first_name": "Test",
                        "last_name": "User",
                        "email": "test.user@example.com",
                        "username": "testuser",
                        "active": True
                    },
                    "123457": {
                        "id": 123457,
                        "first_name": "Another",
                        "last_name": "User",
                        "email": "another.user@example.com",
                        "username": "anotheruser",
                        "active": True
                    }
                }
            }
        }
    elif endpoint == JOBCODES_ENDPOINT:
        return {
            "results": {
                "jobcodes": {
                    "1001": {
                        "id": 1001,
                        "name": "Development",
                        "type": "regular",
                        "active": True
                    },
                    "1002": {
                        "id": 1002,
                        "name": "Design",
                        "type": "regular",
                        "active": True
                    },
                    "1003": {
                        "id": 1003,
                        "name": "Meetings",
                        "type": "regular",
                        "active": True
                    }
                }
            }
        }
    elif endpoint == TIMESHEETS_ENDPOINT:
        if method == "GET":
            # Generate mock timesheet data for the date range in params
            mock_timesheets = {}
            if params and "start_date" in params and "end_date" in params:
                start_date = datetime.strptime(params["start_date"], "%Y-%m-%d")
                end_date = datetime.strptime(params["end_date"], "%Y-%m-%d")
                
                # Generate a timesheet entry for each day in the range
                current_date = start_date
                timesheet_id = 10001
                while current_date <= end_date:
                    # Skip weekends
                    if current_date.weekday() < 5:  # Monday to Friday
                        # Create 1-3 entries per day
                        for i in range(1, np.random.randint(1, 4)):
                            duration = np.random.randint(3600, 28800)  # 1-8 hours in seconds
                            jobcode_id = np.random.choice(["1001", "1002", "1003"])
                            
                            mock_timesheets[str(timesheet_id)] = {
                                "id": timesheet_id,
                                "user_id": 123456,
                                "jobcode_id": jobcode_id,
                                "date": current_date.strftime("%Y-%m-%d"),
                                "duration": duration,
                                "type": "manual",
                                "notes": f"Mock timesheet entry for {current_date.strftime('%Y-%m-%d')}",
                                "billable": jobcode_id in ["1001", "1002"]
                            }
                            timesheet_id += 1
                    
                    current_date += timedelta(days=1)
            
            return {
                "results": {
                    "timesheets": mock_timesheets
                }
            }
        elif method == "POST":
            # Simulate creating a new timesheet
            return {
                "results": {
                    "timesheets": {
                        "10099": {
                            "id": 10099,
                            "_status_code": 200,
                            "_status_message": "Created"
                        }
                    }
                }
            }
        elif method == "PUT":
            # Simulate updating a timesheet
            return {
                "results": {
                    "timesheets": {
                        "10001": {
                            "id": 10001,
                            "_status_code": 200,
                            "_status_message": "Updated"
                        }
                    }
                }
            }
        elif method == "DELETE":
            # Simulate deleting a timesheet
            return {
                "results": {
                    "timesheets": {
                        "10001": {
                            "id": 10001,
                            "_status_code": 200,
                            "_status_message": "Deleted"
                        }
                    }
                }
            }

    # Default mock response
    return {
        "results": {
            "message": "Mock data not implemented for this endpoint"
        }
    }

# --- Helper Functions with Caching ---
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_users_data(_api_token_dependency):
    """Cached function to load users from TSheets API."""
    response = make_api_request(USERS_ENDPOINT, params={"active": "yes"})
    if response and "results" in response and "users" in response["results"]:
        users = response["results"]["users"]
        user_map = {}
        for user_id, user_data in users.items():
            full_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '').strip()}"
            user_map[int(user_id)] = full_name if full_name else f"User {user_id}"
        return users, user_map
    return {}, {}

@st.cache_data(ttl=3600)  # Cache for 1 hour
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
        st.session_state.error_message = None  # Clear after showing warning

def load_jobcodes():
    """Load jobcodes using cached function and update session state."""
    jobcodes_data = fetch_jobcodes_data(st.session_state.api_token)
    st.session_state.jobcodes = jobcodes_data
    if not jobcodes_data and st.session_state.error_message:
        st.warning(f"Could not load job codes: {st.session_state.error_message}")
        st.session_state.error_message = None  # Clear after showing warning

def authenticate():
    """Authenticate with TSheets API and handle connection issues"""
    # First, test the connection with a simple request
    test_response = make_api_request(CURRENT_USER_ENDPOINT)

    if test_response and "results" in test_response and "users" in test_response["results"]:
        st.session_state.authenticated = True
        user_data = list(test_response["results"]["users"].values())[0]
        st.session_state.current_user = user_data
        # Clear caches on new authentication to ensure fresh data for new token/user
        fetch_users_data.clear()
        fetch_jobcodes_data.clear()
        load_initial_data()  # Combined data loading
        st.session_state.last_refresh = datetime.now()
        return True
    else:
        st.session_state.authenticated = False
        if not st.session_state.error_message:
            st.session_state.error_message = "Authentication failed. Please check your API token and connection."
        return False

def load_initial_data():
    """Load all necessary initial data after authentication."""
    with st.spinner("Loading users..."):
        load_users()
    with st.spinner("Loading job codes..."):
        load_jobcodes()
    with st.spinner("Loading timesheets..."):
        load_timesheets()  # Loads for current user and date range
    with st.spinner("Loading clients..."):
        load_clients()  # Loads mock client data
    with st.spinner("Loading deleted timesheets..."):
        load_deleted_timesheets()  # Load deleted timesheets

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
        "supplemental_data": "yes"  # To get jobcode info, etc.
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

def load_deleted_timesheets():
    """Load deleted timesheets from TSheets API."""
    if not st.session_state.current_user:
        st.session_state.deleted_timesheets = []
        return
    
    # Use the last 30 days as a default range for deleted timesheets
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    
    params = {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": today.strftime("%Y-%m-%d"),
        "user_ids": st.session_state.current_user["id"]
    }
    
    response = make_api_request(f"{TIMESHEETS_ENDPOINT}_deleted", params=params)
    if response and "results" in response and "timesheets_deleted" in response["results"]:
        deleted_timesheets_dict = response["results"]["timesheets_deleted"]
        deleted_timesheets_list = list(deleted_timesheets_dict.values())
        deleted_timesheets_list.sort(key=lambda x: x.get("last_modified", "1900-01-01"), reverse=True)
        st.session_state.deleted_timesheets = deleted_timesheets_list
    else:
        st.session_state.deleted_timesheets = []
        if st.session_state.debug_mode and st.session_state.error_message:
            st.warning(f"Could not load deleted timesheets: {st.session_state.error_message}")

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
    if jobcode_id is None or pd.isna(jobcode_id): 
        return "N/A"

    try:
        jobcode_id_str = str(int(jobcode_id))
        # Ensure jobcodes are loaded into session state if needed
        if not st.session_state.jobcodes: 
            load_jobcodes()  # Defensive load if empty
        
        if jobcode_id_str in st.session_state.jobcodes:
            return st.session_state.jobcodes[jobcode_id_str].get("name", f"Job {jobcode_id_str}")
        return f"Job {jobcode_id_str}"
    except (ValueError, TypeError):
        return f"Job {jobcode_id}"

def get_user_name(user_id):
    """Get user full name from user ID using cached data."""
    if user_id is None or pd.isna(user_id): 
        return "N/A"

    try:
        user_id_int = int(user_id)
        if not st.session_state.user_map: 
            load_users()  # Defensive load if empty
        return st.session_state.user_map.get(user_id_int, f"User {user_id_int}")
    except (ValueError, TypeError):
        return f"User {user_id}"

def create_timesheet(data):
    """Create a new timesheet entry"""
    payload = {"data": [data]}
    response = make_api_request(TIMESHEETS_ENDPOINT, method="POST", data=payload)
    if response: 
        st.session_state.success_message = "Timesheet entry created successfully!"
        load_timesheets()  # Refresh data
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
        load_deleted_timesheets()  # Refresh deleted timesheets
        return True
    return False

@st.cache_data(max_entries=10, ttl=600)  # Cache DataFrame conversion for 10 mins
def get_timesheet_dataframe(timesheets_list_tuple):
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
            if st.session_state.debug_mode:
                st.warning(f"Error processing timesheet entry ID {ts.get('id', 'Unknown')}: {e}")
            print(f"Error processing timesheet entry ID {ts.get('id', 'Unknown')}: {e}")
            continue 
            
    df = pd.DataFrame(data)
    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        if "week_number" not in df.columns:
            df["week_number"] = df["date"].dt.isocalendar().week
        if "year" not in df.columns:
            df["year"] = df["date"].dt.isocalendar().year
    return df

# --- Performance Analytics Functions ---
@st.cache_data(ttl=600)
def calculate_employee_performance_metrics(df_tuple, standard_workday_hours=8.0, standard_workweek_hours=40.0):
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

# --- Calendar View Functions ---
@st.cache_data(ttl=600)
def get_timesheets_for_month_display(df_timesheets_tuple, year, month):
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

# --- API Connection Diagnostics ---
def run_api_diagnostics():
    """Run diagnostics on the API connection and return results"""
    diagnostics = {
        "connection_status": "Unknown",
        "endpoints_tested": [],
        "issues_found": [],
        "recommendations": []
    }

    # Test basic connectivity
    try:
        response = requests.get("https://rest.tsheets.com", timeout=5)
        diagnostics["connection_status"] = "Connected to TSheets API server"
        diagnostics["endpoints_tested"].append({"endpoint": "https://rest.tsheets.com", "status": "Success"})
    except requests.exceptions.RequestException as e:
        diagnostics["connection_status"] = "Failed to connect to TSheets API server"
        diagnostics["endpoints_tested"].append({"endpoint": "https://rest.tsheets.com", "status": "Failed", "error": str(e)})
        diagnostics["issues_found"].append("Cannot reach TSheets API server")
        diagnostics["recommendations"].append("Check your internet connection")
        diagnostics["recommendations"].append("Verify that TSheets API is not down for maintenance")
        return diagnostics

    # Test authentication
    if st.session_state.api_token:
        headers = {
            "Authorization": f"Bearer {st.session_state.api_token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(CURRENT_USER_ENDPOINT, headers=headers, timeout=10)
            if response.status_code == 200:
                diagnostics["endpoints_tested"].append({"endpoint": CURRENT_USER_ENDPOINT, "status": "Success"})
            else:
                diagnostics["endpoints_tested"].append({
                    "endpoint": CURRENT_USER_ENDPOINT, 
                    "status": "Failed", 
                    "status_code": response.status_code,
                    "response": response.text[:200]
                })
                diagnostics["issues_found"].append(f"Authentication failed with status code {response.status_code}")
                
                if response.status_code == 401:
                    diagnostics["recommendations"].append("Your API token appears to be invalid or expired")
                    diagnostics["recommendations"].append("Generate a new API token from your TSheets account")
                elif response.status_code == 403:
                    diagnostics["recommendations"].append("Your API token doesn't have sufficient permissions")
                    diagnostics["recommendations"].append("Check the permissions associated with your API token")
                else:
                    diagnostics["recommendations"].append("Check the API documentation for error code details")
        except requests.exceptions.RequestException as e:
            diagnostics["endpoints_tested"].append({
                "endpoint": CURRENT_USER_ENDPOINT, 
                "status": "Failed", 
                "error": str(e)
            })
            diagnostics["issues_found"].append(f"Error during authentication request: {str(e)}")
            diagnostics["recommendations"].append("Check your network connection and try again")
    else:
        diagnostics["issues_found"].append("No API token provided")
        diagnostics["recommendations"].append("Enter your API token to authenticate")

    return diagnostics

# --- Tab Display Functions ---
def display_dashboard_tab(): 
    st.header("Dashboard")
    df_timesheets = get_timesheet_dataframe(tuple(st.session_state.timesheets))

    if df_timesheets.empty:
        st.info("No timesheet data to display on dashboard. Try adjusting the date range or refreshing.")
        return

    total_hours = df_timesheets["duration_seconds"].sum() / 3600
    total_entries = len(df_timesheets)
    avg_hours_entry = total_hours / total_entries if total_entries > 0 else 0
    num_active_jobs = df_timesheets["job_name"].nunique()

    st.subheader("Overview")
    cols_overview = st.columns(4)
    cols_overview[0].metric("Total Hours Logged", f"{total_hours:.2f} hrs")
    cols_overview[1].metric("Total Timesheet Entries", f"{total_entries}")
    cols_overview[2].metric("Avg Hours per Entry", f"{avg_hours_entry:.2f} hrs")
    cols_overview[3].metric("Active Job Codes", f"{num_active_jobs}")

    st.markdown("---")
    st.subheader("Recent Activity & Trends")
    row1_col1, row1_col2 = st.columns(2)
    with row1_col1:
        st.markdown("#### Hours by Job Code (Top 5)")
        job_hours = df_timesheets.groupby("job_name")["duration_seconds"].sum().div(3600).nlargest(5)
        if not job_hours.empty:
            fig_job_hours = px.bar(job_hours, x=job_hours.index, y=job_hours.values, labels={"y":"Total Hours", "x":"Job Code"}, text_auto=True)
            fig_job_hours.update_layout(showlegend=False)
            st.plotly_chart(fig_job_hours, use_container_width=True)
        else:
            st.info("No job code data for chart.")

    with row1_col2:
        st.markdown("#### Daily Hours Trend (Last 7 Displayed Days)")
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

    st.markdown("#### Recent Timesheet Entries (Top 5)")
    st.dataframe(df_timesheets[["date_str", "job_name", "duration_formatted", "notes"]].head(), use_container_width=True)

def display_timesheets_tab():
    st.header("Manage Timesheets")
    action = st.selectbox("Choose action:", ["View Timesheets", "Create New Timesheet", "Edit Timesheet", "Delete Timesheet", "View Deleted Timesheets"], key="ts_action")

    if action == "View Timesheets":
        st.subheader("Your Timesheets")
        if not st.session_state.timesheets:
            st.info("No timesheets found for the selected period. Try adjusting date range or refreshing.")
        else:
            df_display = get_timesheet_dataframe(tuple(st.session_state.timesheets))
            if not df_display.empty:
                st.dataframe(df_display[["id", "date_str", "job_name", "duration_formatted", "notes", "billable"]], use_container_width=True)
            else:
                st.info("No timesheets to display after processing.")

    elif action == "Create New Timesheet":
        st.subheader("Create New Timesheet Entry")
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
        st.subheader("Edit Timesheet Entry")
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
                
                # Determine if this is a regular or manual timesheet
                ts_type = original_ts.get("type", "manual")
                
                if ts_type == "regular":
                    # For regular timesheets, show start and end time fields
                    start_time_str = original_ts.get("start", "")
                    end_time_str = original_ts.get("end", "")
                    
                    try:
                        start_dt = datetime.fromisoformat(start_time_str.replace("Z", "+00:00")) if start_time_str else None
                        end_dt = datetime.fromisoformat(end_time_str.replace("Z", "+00:00")) if end_time_str else None
                        
                        start_time = start_dt.time() if start_dt else None
                        end_time = end_dt.time() if end_dt else None
                        
                        edit_start_time = st.time_input("Start Time", value=start_time, key=f"edit_ts_start_{timesheet_id_to_edit}")
                        edit_end_time = st.time_input("End Time", value=end_time, key=f"edit_ts_end_{timesheet_id_to_edit}")
                    except (ValueError, TypeError):
                        st.warning("Could not parse original start/end times. Please enter new values.")
                        edit_start_time = st.time_input("Start Time", key=f"edit_ts_start_new_{timesheet_id_to_edit}")
                        edit_end_time = st.time_input("End Time", key=f"edit_ts_end_new_{timesheet_id_to_edit}")
                else:
                    # For manual timesheets, show duration field
                    original_duration_hours = original_ts.get("duration", 0) / 3600
                    edit_duration_hours = st.number_input("Duration (hours)", value=original_duration_hours, min_value=0.0, step=0.25, key=f"edit_ts_duration_{timesheet_id_to_edit}")
                
                submitted_edit = st.form_submit_button("Update Timesheet")
                if submitted_edit:
                    updated_data = {
                        "date": edit_date.strftime("%Y-%m-%d"),
                        "jobcode_id": job_id_edit,
                        "notes": edit_notes,
                        "billable": edit_billable
                    }
                    
                    if ts_type == "regular":
                        # Update start and end times for regular timesheets
                        start_dt = datetime.combine(edit_date, edit_start_time)
                        end_dt = datetime.combine(edit_date, edit_end_time)
                        
                        if end_dt <= start_dt:
                            st.error("End time must be after start time.")
                            return
                            
                        updated_data["start"] = start_dt.isoformat() + "Z"
                        updated_data["end"] = end_dt.isoformat() + "Z"
                    else:
                        # Update duration for manual timesheets
                        updated_data["duration"] = int(edit_duration_hours * 3600)
                    
                    if update_timesheet(timesheet_id_to_edit, updated_data):
                        st.success("Timesheet updated!")
                    else:
                        st.error(f"Failed to update timesheet. {st.session_state.error_message or 'Unknown error.'}")

    elif action == "Delete Timesheet":
        st.subheader("Delete Timesheet Entry")
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
                else:
                    st.error(f"Failed to delete timesheet. {st.session_state.error_message or 'Unknown error.'}")
    
    elif action == "View Deleted Timesheets":
        st.subheader("Deleted Timesheets")
        if not st.session_state.deleted_timesheets:
            st.info("No deleted timesheets found for the last 30 days.")
            if st.button("Refresh Deleted Timesheets"):
                load_deleted_timesheets()
                st.rerun()
        else:
            # Create a DataFrame for display
            deleted_data = []
            for ts in st.session_state.deleted_timesheets:
                try:
                    entry_date = datetime.strptime(ts["date"], "%Y-%m-%d").date() if isinstance(ts.get("date"), str) else ts.get("date")
                    duration_seconds = int(ts.get("duration", 0))
                    deleted_data.append({
                        "id": ts["id"],
                        "date": entry_date.strftime("%Y-%m-%d") if entry_date else "N/A",
                        "user_name": get_user_name(ts["user_id"]),
                        "job_name": get_jobcode_name(ts.get("jobcode_id")),
                        "duration": format_duration(duration_seconds),
                        "notes": ts.get("notes", ""),
                        "deleted_on": ts.get("last_modified", "Unknown")
                    })
                except Exception as e:
                    if st.session_state.debug_mode:
                        st.warning(f"Error processing deleted timesheet: {e}")
                    continue
                    
            if deleted_data:
                df_deleted = pd.DataFrame(deleted_data)
                st.dataframe(df_deleted, use_container_width=True)
            else:
                st.info("No deleted timesheets to display after processing.")

def display_reports_tab():
    st.header("Reports & Analytics")
    df_reports = get_timesheet_dataframe(tuple(st.session_state.timesheets))
    if df_reports.empty:
        st.info("No data for reports. Please check date range or refresh.")
        return

    st.subheader("Timesheet Summary Report")
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
            file_name=f"timesheet_summary_by_{report_type.lower().replace(' ', '_')}.csv",
            mime="text/csv",
            key=f"download_{report_type}_csv"
        )
    else:
        st.info("No data to display for this grouping.")

def display_performance_analytics_tab(df_timesheets):
    """Displays the employee performance analytics tab with KPIs and charts."""
    st.header("Employee Performance Analytics")

    if df_timesheets.empty:
        st.warning("No timesheet data available for the selected period to calculate performance metrics.")
        return

    col1, col2 = st.columns(2)
    with col1:
        standard_workday = st.number_input("Standard Workday Hours", min_value=1.0, max_value=24.0, value=8.0, step=0.5, key="perf_workday_hours")
    with col2:
        standard_workweek = st.number_input("Standard Workweek Hours", min_value=1.0, max_value=168.0, value=40.0, step=1.0, key="perf_workweek_hours")

    # Convert DataFrame to tuple for caching
    metrics = calculate_employee_performance_metrics(tuple(map(tuple, df_timesheets.values)), standard_workday_hours=standard_workday, standard_workweek_hours=standard_workweek)

    st.markdown("---")
    st.subheader("Key Performance Indicators (KPIs)")
    cols_kpi1 = st.columns(3)
    cols_kpi1[0].metric("Total Hours Logged", metrics["total_hours_logged_decimal"] + " hrs", delta=metrics["total_hours_logged_formatted"])
    cols_kpi1[1].metric("Avg Daily Hours", metrics["avg_daily_hours_decimal"] + " hrs", help=f"{metrics['num_days_worked']} days worked")
    cols_kpi1[2].metric("Avg Weekly Hours", metrics["avg_weekly_hours_decimal"] + " hrs", help=f"{metrics['num_weeks_worked']} weeks worked")

    cols_kpi2 = st.columns(3)
    cols_kpi2[0].metric("Billable Hours", metrics["billable_hours_decimal"] + " hrs", delta=f"{metrics['billable_percentage']} % of Total")
    cols_kpi2[1].metric("Non-Billable Hours", metrics["non_billable_hours_decimal"] + " hrs")
    cols_kpi2[2].metric("Utilization (vs Logged)", f"{metrics['utilization_rate_vs_logged']} %", help="Billable Hours / Total Logged Hours")

    cols_kpi3 = st.columns(3)
    cols_kpi3[0].metric("Daily Overtime", metrics["daily_overtime_hours_decimal"] + " hrs")
    cols_kpi3[1].metric("Weekly Overtime", metrics["weekly_overtime_hours_decimal"] + " hrs")
    cols_kpi3[2].metric("Utilization (vs Standard)", f"{metrics['utilization_rate_vs_standard']} %", help=f"Billable Hours / ({metrics['num_days_worked']} days * {standard_workday} hrs/day)")

    st.markdown("---")
    st.subheader("Work Distribution & Patterns")
    col_dist1, col_dist2 = st.columns([2,1]) 
    with col_dist1:
        st.markdown("#### Hours per Job Code")
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
        st.markdown("#### Billable vs. Non-Billable")
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

    st.markdown("---")
    st.subheader("Trends Over Time (Last 12 Weeks)")
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
        st.info("Weekly trend data requires 'week_number' and 'year' in timesheet details.")

def display_timesheet_calendar_tab(df_timesheets):
    """Displays an interactive monthly calendar with timesheet entries."""
    st.header("Timesheet Calendar")

    current_month_view = st.session_state.calendar_current_month_view

    cal_col1, cal_col2, cal_col3 = st.columns([1,2,1])
    with cal_col1:
        if st.button("⬅️ Previous Month", key="cal_prev_month_btn", use_container_width=True):
            st.session_state.calendar_current_month_view = (current_month_view - timedelta(days=1)).replace(day=1)
            st.session_state.calendar_selected_day_entries = None
            st.session_state.calendar_selected_date_for_details = None
            st.rerun()
    with cal_col2:
        st.markdown(f"<h3 style='text-align: center; margin-top:10px; margin-bottom:10px;'>{current_month_view.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
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
            st.rerun()

    df_timesheets_tuple = tuple(map(tuple, df_timesheets.values)) if not df_timesheets.empty else tuple()
    entries_this_month = get_timesheets_for_month_display(df_timesheets_tuple, current_month_view.year, current_month_view.month)

    month_calendar = calendar.monthcalendar(current_month_view.year, current_month_view.month)
    weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    cols_weekdays = st.columns(7)
    for i, day_name in enumerate(weekdays):
        cols_weekdays[i].markdown(f"<div style='text-align:center; font-weight:bold;'>{day_name}</div>", unsafe_allow_html=True)

    for week in month_calendar:
        cols_days = st.columns(7)
        for i, day_num in enumerate(week):
            with cols_days[i]:
                if day_num == 0:
                    st.markdown("<div style='height:80px;'></div>", unsafe_allow_html=True)
                else:
                    current_day_date = date(current_month_view.year, current_month_view.month, day_num)
                    
                    button_label = f"{day_num}"
                    if day_num in entries_this_month and entries_this_month[day_num]:
                        entry_count = len(entries_this_month[day_num])
                        total_hours_today = sum(e.get("duration_hours_decimal", 0) for e in entries_this_month[day_num])
                        button_label += f"\n{entry_count} entr{'y' if entry_count == 1 else 'ies'}\n{total_hours_today:.2f}h"

                    button_key = f"day_btn_{current_month_view.year}_{current_month_view.month}_{day_num}"
                    if st.button(label=button_label, key=button_key, help=f"View entries for {current_day_date.strftime('%b %d')}", use_container_width=True):
                        st.session_state.calendar_selected_date_for_details = current_day_date
                        st.session_state.calendar_selected_day_entries = entries_this_month.get(day_num, [])
                        st.rerun() 

    if st.session_state.calendar_selected_day_entries is not None and st.session_state.calendar_selected_date_for_details:
        st.markdown("---")
        st.subheader(f"Entries for {st.session_state.calendar_selected_date_for_details.strftime('%B %d, %Y')}")
        if not st.session_state.calendar_selected_day_entries:
            st.info("No entries for this day.")
        else:
            for entry in st.session_state.calendar_selected_day_entries:
                with st.container():
                    st.markdown(f"""
                    <div style='background-color:#f8f9fa; border-left:4px solid #4CAF50; padding:15px; margin-bottom:15px; border-radius:0 5px 5px 0;'>
                        <div><strong>Time:</strong> {entry["time_range"]}</div>
                        <div><strong>Job:</strong> {entry["job_name"]}</div>
                        <div><strong>Duration:</strong> {entry["duration_formatted"]}</div>
                        <div><em>Notes:</em> {entry["notes_preview"]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"View Full Timesheet #{entry['id']}", key=f"view_cal_entry_{entry['id']}", help="Navigate to Timesheets tab to view/edit this entry"):
                        st.session_state.active_tab = "⏰ Timesheets" # Switch tab
                        st.info(f"Navigating to Timesheets. Full details for ID {entry['id']} can be searched or managed there.")
                        st.rerun()

def display_clients_tab():
    st.header("Client Management (Mock)")
    if not st.session_state.clients:
        st.info("No client data available.")
        load_clients() # Ensure mock clients are loaded if empty
        if not st.session_state.clients: # Still no clients after attempt
             st.warning("Failed to load mock client data.")
             return

    for client in st.session_state.clients:
        with st.expander(f"{client['name']} ({client['status']})"):
            st.markdown(f"**Contact:** {client['contact']} ({client['email']})")
            st.markdown(f"**Industry:** {client['industry']}")
            st.markdown(f"**Total Hours Logged (Example):** {client['total_hours']}")
            st.markdown(f"**Notes:** {client['notes']}")

def display_settings_tab():
    st.header("Settings")

    # Mock Data Mode Toggle
    st.subheader("API Connection Mode")
    mock_data_mode = st.checkbox("Use Mock Data (No API Connection Required)", 
                                value=st.session_state.mock_data_mode,
                                help="Enable this to use mock data instead of connecting to the TSheets API")
    if mock_data_mode != st.session_state.mock_data_mode:
        st.session_state.mock_data_mode = mock_data_mode
        if mock_data_mode:
            st.success("Mock data mode enabled. The app will use sample data instead of connecting to the API.")
            # Clear caches to ensure mock data is used
            fetch_users_data.clear()
            fetch_jobcodes_data.clear()
            get_timesheet_dataframe.clear()
            calculate_employee_performance_metrics.clear()
            get_timesheets_for_month_display.clear()
            # Force re-authentication to load mock data
            st.session_state.authenticated = False
            if st.session_state.api_token:  # Only try to authenticate if there's a token
                authenticate()
            st.rerun()
        else:
            st.warning("Mock data mode disabled. The app will attempt to connect to the TSheets API.")
            # Clear caches to ensure real API data is used
            fetch_users_data.clear()
            fetch_jobcodes_data.clear()
            get_timesheet_dataframe.clear()
            calculate_employee_performance_metrics.clear()
            get_timesheets_for_month_display.clear()
            # Force re-authentication to load real data
            st.session_state.authenticated = False
            if st.session_state.api_token:  # Only try to authenticate if there's a token
                authenticate()
            st.rerun()

    # API Connection Diagnostics Section
    st.subheader("API Connection Diagnostics")
    if st.button("Run API Connection Diagnostics", key="run_diagnostics_btn"):
        with st.spinner("Running API connection diagnostics..."):
            diagnostics_results = run_api_diagnostics()
        
        st.markdown(f"**Connection Status:** {diagnostics_results['connection_status']}")
        
        if diagnostics_results['endpoints_tested']:
            st.markdown("**Endpoints Tested:**")
            for endpoint in diagnostics_results['endpoints_tested']:
                status_color = "green" if endpoint.get('status') == "Success" else "red"
                st.markdown(f"- {endpoint.get('endpoint')}: <span style='color:{status_color}'>{endpoint.get('status')}</span>", unsafe_allow_html=True)
        
        if diagnostics_results['issues_found']:
            st.markdown("**Issues Found:**")
            for issue in diagnostics_results['issues_found']:
                st.markdown(f"- {issue}")
        
        if diagnostics_results['recommendations']:
            st.markdown("**Recommendations:**")
            for rec in diagnostics_results['recommendations']:
                st.markdown(f"- {rec}")

    # Debug Mode Toggle
    st.subheader("Debug Mode")
    debug_mode = st.checkbox("Enable Debug Mode", 
                            value=st.session_state.debug_mode,
                            help="Show detailed debug information for troubleshooting")
    if debug_mode != st.session_state.debug_mode:
        st.session_state.debug_mode = debug_mode
        st.rerun()

    if st.session_state.debug_mode and st.session_state.debug_info:
        st.markdown("**Last API Request Debug Info:**")
        st.json(st.session_state.debug_info)
        
        st.markdown("**Recent API Logs:**")
        st.dataframe(pd.DataFrame(st.session_state.api_logs[-10:]), use_container_width=True)

    # API Token Section
    st.subheader("API Token")
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
                st.error(f"Failed to re-authenticate with new token. {st.session_state.error_message or 'Check token and connection.'}")
        else:
            st.warning("Please enter a new API token to update.")

    # Date Range Section
    st.subheader("Date Range for Data")
    current_start_date, current_end_date = st.session_state.date_range
    new_date_range = st.date_input(
        "Select Date Range",
        value=(current_start_date, current_end_date),
        max_value=datetime.now().date(),
        key="settings_date_range"
    )
    if len(new_date_range) == 2 and (new_date_range[0], new_date_range[1]) != (current_start_date, current_end_date):
        st.session_state.date_range = (new_date_range[0], new_date_range[1])
        st.info("Date range updated. Refresh data or navigate to see changes.")
        if st.session_state.authenticated:
            with st.spinner("Reloading timesheets for new date range..."):
                load_timesheets() 
            get_timesheet_dataframe.clear() # Clear relevant caches
            calculate_employee_performance_metrics.clear()
            get_timesheets_for_month_display.clear()
            st.rerun()

    # Cache Management Section
    st.subheader("Cache Management")
    if st.button("Clear All App Caches", key="clear_all_caches_btn"):
        fetch_users_data.clear()
        fetch_jobcodes_data.clear()
        get_timesheet_dataframe.clear()
        calculate_employee_performance_metrics.clear()
        get_timesheets_for_month_display.clear()
        st.success("All application data caches have been cleared. Data will be re-fetched on next load.")
        st.rerun()

# --- Main Application Logic ---
def main():
    st.title("TSheets CRM Manager Pro ⏱️")

    with st.sidebar:
        # Using a publicly accessible, generic logo URL for placeholder
        try:
            st.image(
                "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Google_Clock_Icon.svg/1024px-Google_Clock_Icon.svg.png",
                width=150,
                caption="App Logo"
            )
        except Exception as e:
            st.error(f"Logo Error: {e}")  # Should not happen with URL
            st.write("App Logo")  # Fallback text

        st.markdown("## Authentication")
        if not st.session_state.authenticated:
            # Option to use mock data without authentication
            if not st.session_state.mock_data_mode:
                mock_data_toggle = st.checkbox("Use Mock Data (No API Token Required)", 
                                            value=False, 
                                            help="Enable this to use sample data instead of connecting to the TSheets API")
                if mock_data_toggle:
                    st.session_state.mock_data_mode = True
                    st.session_state.api_token = "mock_token"  # Set a dummy token
                    with st.spinner("Loading mock data..."):
                        if authenticate():
                            st.success("Mock data mode enabled successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to initialize mock data mode.")
                            st.session_state.mock_data_mode = False
                            st.session_state.api_token = ""
            
            api_token_input = st.text_input(
                "Enter your TSheets API Token",
                type="password",
                key="api_token_input_sidebar",
                help="Your personal TSheets API access token."
            )
            if st.button("Login", key="login_button_sidebar", use_container_width=True):
                if api_token_input:
                    st.session_state.api_token = api_token_input
                    with st.spinner("Authenticating..."):
                        if authenticate():
                            st.success("Authentication successful!")
                            st.rerun()
                        else:
                            # Error message is set in authenticate() or make_api_request()
                            msg = st.session_state.error_message or 'Authentication failed. Check token and connection.'
                            st.error(msg)
                            
                            # Offer mock data mode if authentication fails
                            if st.button("Use Mock Data Instead", key="use_mock_data_btn"):
                                st.session_state.mock_data_mode = True
                                st.session_state.api_token = "mock_token"  # Set a dummy token
                                with st.spinner("Loading mock data..."):
                                    if authenticate():
                                        st.success("Mock data mode enabled successfully!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to initialize mock data mode.")
                                        st.session_state.mock_data_mode = False
                                        st.session_state.api_token = ""
                else:
                    st.warning("Please enter an API token or enable mock data mode.")
        else:
            if st.session_state.current_user:
                st.markdown(
                    f"Logged in as: **{st.session_state.current_user.get('first_name', '')} "
                    f"{st.session_state.current_user.get('last_name', '')}**"
                )
                st.caption(f"User ID: {st.session_state.current_user.get('id')}")
                
                if st.session_state.mock_data_mode:
                    st.info("Using mock data mode - no actual API connection")
                
            if st.button("Logout", key="logout_button_sidebar", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.api_token = ""
                st.session_state.current_user = None
                st.session_state.timesheets = []
                st.session_state.users = {}
                st.session_state.jobcodes = {}
                st.session_state.clients = []
                st.session_state.mock_data_mode = False
                # Clear all caches on logout
                fetch_users_data.clear()
                fetch_jobcodes_data.clear()
                get_timesheet_dataframe.clear()
                calculate_employee_performance_metrics.clear()
                get_timesheets_for_month_display.clear()
                st.success("Logged out successfully.")
                st.rerun()

            st.markdown("---")
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
                st.rerun()
            if st.session_state.last_refresh:
                st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%Y-%m-%d %H:%M:%S')}")

    # Display messages (success/error/warning) centrally
    if st.session_state.success_message:
        st.success(st.session_state.success_message)
        st.session_state.success_message = None 
    if st.session_state.error_message:
        # Check if it's a warning-level message from retries
        if "Retrying" in st.session_state.error_message:
            st.warning(st.session_state.error_message)
        else:
            st.error(st.session_state.error_message)
        # Do not clear error_message here, let it persist until next successful action or explicit clear

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
        
        # Option to use mock data from the main screen
        if st.button("Use Mock Data Instead (No API Token Required)", key="use_mock_data_main"):
            st.session_state.mock_data_mode = True
            st.session_state.api_token = "mock_token"  # Set a dummy token
            with st.spinner("Loading mock data..."):
                if authenticate():
                    st.success("Mock data mode enabled successfully!")
                    st.rerun()
                else:
                    st.error("Failed to initialize mock data mode.")
                    st.session_state.mock_data_mode = False
                    st.session_state.api_token = ""
    elif st.session_state.error_message and "Authentication failed" in st.session_state.error_message:
        pass # Error is already displayed above

    st.markdown("---")
    st.markdown("TSheets CRM Manager Pro © 2024-2025 | Enhanced Features by Manus")

if __name__ == "__main__":
    main()
