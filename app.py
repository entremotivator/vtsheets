import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import io
import base64
import time
import uuid
import os
from PIL import Image
from io import BytesIO
import sys

# Page configuration
st.set_page_config(
    page_title="TSheets Manager Pro",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- API Configuration ---
BASE_URL = "https://rest.tsheets.com/api/v1"
TIMESHEETS_ENDPOINT = f"{BASE_URL}/timesheets"
JOBS_ENDPOINT = f"{BASE_URL}/jobcodes"
USERS_ENDPOINT = f"{BASE_URL}/users"
REPORTS_ENDPOINT = f"{BASE_URL}/reports"
CLIENTS_ENDPOINT = f"{BASE_URL}/custom_fields" # We'll use custom fields to store client data

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
        color: #2c3e50;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
        color: #34495e;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1.5rem;
        border-left: 4px solid #4e73df;
    }
    .metric-card {
        text-align: center;
        padding: 1.2rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.1);
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #4e73df;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5a5c69;
        margin-top: 0.5rem;
    }
    .status-success {
        color: #1cc88a;
        font-weight: 600;
    }
    .status-warning {
        color: #f6c23e;
        font-weight: 600;
    }
    .status-danger {
        color: #e74a3b;
        font-weight: 600;
    }
    .form-section {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 0.5rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.1);
        margin-bottom: 1.5rem;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        color: #4e73df;
    }
    .client-card {
        background-color: #ffffff;
        border-radius: 0.5rem;
        padding: 1.2rem;
        margin-bottom: 1rem;
        box-shadow: 0 0.15rem 0.5rem 0 rgba(58, 59, 69, 0.1);
        border-left: 4px solid #36b9cc;
    }
    .client-name {
        font-size: 1.3rem;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.5rem;
    }
    .client-info {
        font-size: 0.9rem;
        color: #5a5c69;
    }
    .client-contact {
        background-color: #f8f9fa;
        padding: 0.8rem;
        border-radius: 0.3rem;
        margin-top: 0.8rem;
    }
    .client-projects {
        margin-top: 0.8rem;
    }
    .project-item {
        background-color: #f1f5f9;
        padding: 0.5rem 0.8rem;
        border-radius: 0.3rem;
        margin-bottom: 0.5rem;
        font-size: 0.9rem;
    }
    .tab-content {
        padding: 1.5rem 0;
    }
    .search-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .avatar-small {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        object-fit: cover;
    }
    .avatar-large {
        width: 100px;
        height: 100px;
        border-radius: 50%;
        object-fit: cover;
        border: 3px solid #4e73df;
    }
    .badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        font-size: 0.75rem;
        font-weight: 600;
        border-radius: 0.25rem;
        margin-right: 0.5rem;
    }
    .badge-primary {
        background-color: #4e73df;
        color: white;
    }
    .badge-success {
        background-color: #1cc88a;
        color: white;
    }
    .badge-warning {
        background-color: #f6c23e;
        color: white;
    }
    .badge-danger {
        background-color: #e74a3b;
        color: white;
    }
    .badge-info {
        background-color: #36b9cc;
        color: white;
    }
    .badge-secondary {
        background-color: #858796;
        color: white;
    }
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        background-color: #e74a3b;
        color: white;
        border-radius: 50%;
        width: 20px;
        height: 20px;
        font-size: 0.7rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 4px 4px 0 0;
        gap: 1rem;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f8f9fa;
        border-bottom: 2px solid #4e73df;
    }
</style>
""", unsafe_allow_html=True)

# --- Session State Initialization ---
if 'auth_token' not in st.session_state:
    st.session_state.auth_token = None
if 'timesheets' not in st.session_state:
    st.session_state.timesheets = []
if 'users' not in st.session_state:
    st.session_state.users = {}
if 'jobcodes' not in st.session_state:
    st.session_state.jobcodes = {}
if 'clients' not in st.session_state:
    st.session_state.clients = {}
if 'date_range' not in st.session_state:
    st.session_state.date_range = (date.today() - timedelta(days=30), date.today())
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Dashboard"
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = "all"
if 'selected_jobcode' not in st.session_state:
    st.session_state.selected_jobcode = "all"
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = "all"
if 'loading' not in st.session_state:
    st.session_state.loading = False
if 'notifications' not in st.session_state:
    st.session_state.notifications = []
if 'client_projects' not in st.session_state:
    st.session_state.client_projects = {}
if 'client_contacts' not in st.session_state:
    st.session_state.client_contacts = {}
if 'client_notes' not in st.session_state:
    st.session_state.client_notes = {}
if 'client_billing' not in st.session_state:
    st.session_state.client_billing = {}
if 'client_avatars' not in st.session_state:
    st.session_state.client_avatars = {}
if 'user_avatars' not in st.session_state:
    st.session_state.user_avatars = {}

# --- Utility Functions ---
def api_request(method, url, params=None, data=None, retry=True):
    """Make an API request to TSheets with proper error handling and retry logic"""
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }
    
    try:
        with st.spinner("Processing request..."):
            response = requests.request(method, url, headers=headers, params=params, json=data, timeout=15)
            
        if response.status_code == 401:
            st.error("Authentication failed. Please check your API token.")
            return None
            
        if response.status_code == 429 and retry:
            # Rate limit hit, wait and retry once
            time.sleep(2)
            return api_request(method, url, params, data, retry=False)
            
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        error_msg = f"API Error: {str(e)}"
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_data = e.response.json()
                if 'error' in error_data and 'message' in error_data['error']:
                    error_msg = f"API Error: {error_data['error']['message']}"
            except:
                pass
        st.error(error_msg)
        # Add to notifications
        add_notification("error", error_msg)
        return None
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
        add_notification("error", f"Unexpected error: {str(e)}")
        return None

def load_data(show_success=True):
    """Load all necessary data from TSheets API"""
    st.session_state.loading = True
    
    # Get users
    users_data = api_request("GET", USERS_ENDPOINT, params={"active": "yes"})
    if users_data and 'results' in users_data and 'users' in users_data['results']:
        st.session_state.users = {
            str(user_id): user_data 
            for user_id, user_data in users_data['results']['users'].items()
        }
        
        # Generate avatar placeholders for users
        for user_id, user_data in st.session_state.users.items():
            if user_id not in st.session_state.user_avatars:
                # Generate a placeholder avatar based on user initials
                first_name = user_data.get('first_name', 'U')
                last_name = user_data.get('last_name', 'U')
                initials = f"{first_name[0]}{last_name[0]}" if first_name and last_name else "UU"
                st.session_state.user_avatars[user_id] = f"https://ui-avatars.com/api/?name={initials}&background=4e73df&color=fff"
    
    # Get job codes
    jobs_data = api_request("GET", JOBS_ENDPOINT, params={"active": "yes"})
    if jobs_data and 'results' in jobs_data and 'jobcodes' in jobs_data['results']:
        st.session_state.jobcodes = {
            str(job_id): job_data 
            for job_id, job_data in jobs_data['results']['jobcodes'].items()
        }
    
    # Get custom fields (for clients)
    clients_data = api_request("GET", CLIENTS_ENDPOINT)
    if clients_data and 'results' in clients_data and 'custom_fields' in clients_data['results']:
        # Process client data from custom fields
        # In a real implementation, you might have a dedicated clients endpoint
        # Here we're simulating client data using custom fields
        load_client_data()
    
    # Get timesheets
    start_date, end_date = st.session_state.date_range
    params = {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "supplemental_data": "yes"
    }
    
    if st.session_state.selected_user != "all":
        params["user_ids"] = st.session_state.selected_user
        
    if st.session_state.selected_jobcode != "all":
        params["jobcode_ids"] = st.session_state.selected_jobcode
    
    data = api_request("GET", TIMESHEETS_ENDPOINT, params=params)
    if data and 'results' in data and 'timesheets' in data['results']:
        st.session_state.timesheets = list(data['results']['timesheets'].values())
    else:
        st.session_state.timesheets = []
    
    st.session_state.loading = False
    
    if show_success:
        add_notification("success", "Data refreshed successfully")

def load_client_data():
    """Load client data (simulated using a predefined structure)"""
    # In a real implementation, this would fetch from an API
    # Here we're creating sample client data
    
    # Sample clients
    clients = {
        "1": {
            "id": "1",
            "name": "Acme Corporation",
            "industry": "Technology",
            "status": "active",
            "created_date": "2022-01-15",
            "address": "123 Tech Blvd, San Francisco, CA 94107",
            "website": "https://acmecorp.example.com",
            "logo": "https://ui-avatars.com/api/?name=AC&background=36b9cc&color=fff"
        },
        "2": {
            "id": "2",
            "name": "Global Enterprises",
            "industry": "Finance",
            "status": "active",
            "created_date": "2022-03-22",
            "address": "456 Finance Ave, New York, NY 10004",
            "website": "https://globalent.example.com",
            "logo": "https://ui-avatars.com/api/?name=GE&background=1cc88a&color=fff"
        },
        "3": {
            "id": "3",
            "name": "Sunshine Retail",
            "industry": "Retail",
            "status": "inactive",
            "created_date": "2022-05-10",
            "address": "789 Market St, Chicago, IL 60601",
            "website": "https://sunshine.example.com",
            "logo": "https://ui-avatars.com/api/?name=SR&background=f6c23e&color=fff"
        },
        "4": {
            "id": "4",
            "name": "Innovative Solutions",
            "industry": "Consulting",
            "status": "active",
            "created_date": "2022-07-05",
            "address": "321 Innovation Dr, Austin, TX 78701",
            "website": "https://innovative.example.com",
            "logo": "https://ui-avatars.com/api/?name=IS&background=e74a3b&color=fff"
        },
        "5": {
            "id": "5",
            "name": "EcoFriendly Products",
            "industry": "Manufacturing",
            "status": "active",
            "created_date": "2022-09-18",
            "address": "555 Green Way, Portland, OR 97201",
            "website": "https://ecofriendly.example.com",
            "logo": "https://ui-avatars.com/api/?name=EP&background=858796&color=fff"
        }
    }
    
    # Sample client contacts
    contacts = {
        "1": [
            {"name": "John Smith", "title": "CEO", "email": "john@acmecorp.example.com", "phone": "555-123-4567"},
            {"name": "Sarah Johnson", "title": "CTO", "email": "sarah@acmecorp.example.com", "phone": "555-123-4568"}
        ],
        "2": [
            {"name": "Michael Brown", "title": "CFO", "email": "michael@globalent.example.com", "phone": "555-234-5678"},
            {"name": "Emily Davis", "title": "COO", "email": "emily@globalent.example.com", "phone": "555-234-5679"}
        ],
        "3": [
            {"name": "Robert Wilson", "title": "CEO", "email": "robert@sunshine.example.com", "phone": "555-345-6789"}
        ],
        "4": [
            {"name": "Jennifer Lee", "title": "President", "email": "jennifer@innovative.example.com", "phone": "555-456-7890"},
            {"name": "David Martinez", "title": "VP of Operations", "email": "david@innovative.example.com", "phone": "555-456-7891"}
        ],
        "5": [
            {"name": "Lisa Taylor", "title": "CEO", "email": "lisa@ecofriendly.example.com", "phone": "555-567-8901"},
            {"name": "Kevin Anderson", "title": "Sustainability Director", "email": "kevin@ecofriendly.example.com", "phone": "555-567-8902"}
        ]
    }
    
    # Sample client projects
    projects = {
        "1": [
            {"id": "101", "name": "Website Redesign", "status": "In Progress", "deadline": "2023-06-30"},
            {"id": "102", "name": "Mobile App Development", "status": "Planning", "deadline": "2023-08-15"},
            {"id": "103", "name": "Cloud Migration", "status": "Completed", "deadline": "2023-03-01"}
        ],
        "2": [
            {"id": "201", "name": "Financial System Upgrade", "status": "In Progress", "deadline": "2023-07-15"},
            {"id": "202", "name": "Security Audit", "status": "Completed", "deadline": "2023-02-28"}
        ],
        "3": [
            {"id": "301", "name": "Inventory Management System", "status": "On Hold", "deadline": "2023-09-01"},
            {"id": "302", "name": "E-commerce Platform", "status": "Planning", "deadline": "2023-10-15"}
        ],
        "4": [
            {"id": "401", "name": "Business Process Optimization", "status": "In Progress", "deadline": "2023-08-01"},
            {"id": "402", "name": "Strategic Planning", "status": "Completed", "deadline": "2023-04-15"},
            {"id": "403", "name": "Market Research", "status": "Planning", "deadline": "2023-09-30"}
        ],
        "5": [
            {"id": "501", "name": "Sustainable Packaging Design", "status": "In Progress", "deadline": "2023-07-30"},
            {"id": "502", "name": "Supply Chain Optimization", "status": "Planning", "deadline": "2023-09-15"}
        ]
    }
    
    # Sample client notes
    notes = {
        "1": [
            {"date": "2023-01-10", "author": "Jane Doe", "content": "Discussed website redesign project scope and timeline."},
            {"date": "2023-02-15", "author": "John Smith", "content": "Client requested additional features for mobile app."},
            {"date": "2023-03-20", "author": "Sarah Johnson", "content": "Cloud migration completed successfully."}
        ],
        "2": [
            {"date": "2023-01-20", "author": "Michael Brown", "content": "Reviewed financial system requirements."},
            {"date": "2023-02-25", "author": "Emily Davis", "content": "Security audit findings presented to client."}
        ],
        "3": [
            {"date": "2023-01-15", "author": "Robert Wilson", "content": "Initial meeting to discuss inventory management needs."},
            {"date": "2023-02-20", "author": "Jane Doe", "content": "Project put on hold due to budget constraints."}
        ],
        "4": [
            {"date": "2023-01-25", "author": "Jennifer Lee", "content": "Kickoff meeting for business process optimization."},
            {"date": "2023-02-28", "author": "David Martinez", "content": "Strategic planning workshop completed."},
            {"date": "2023-03-15", "author": "John Smith", "content": "Market research methodology approved."}
        ],
        "5": [
            {"date": "2023-01-30", "author": "Lisa Taylor", "content": "Initial discussion about sustainable packaging requirements."},
            {"date": "2023-03-05", "author": "Kevin Anderson", "content": "Supply chain analysis started."}
        ]
    }
    
    # Sample client billing info
    billing = {
        "1": {
            "rate": 150,
            "currency": "USD",
            "billing_cycle": "Monthly",
            "payment_terms": "Net 30",
            "billing_contact": "John Smith",
            "billing_email": "billing@acmecorp.example.com"
        },
        "2": {
            "rate": 200,
            "currency": "USD",
            "billing_cycle": "Monthly",
            "payment_terms": "Net 15",
            "billing_contact": "Michael Brown",
            "billing_email": "accounts@globalent.example.com"
        },
        "3": {
            "rate": 125,
            "currency": "USD",
            "billing_cycle": "Bi-weekly",
            "payment_terms": "Net 30",
            "billing_contact": "Robert Wilson",
            "billing_email": "finance@sunshine.example.com"
        },
        "4": {
            "rate": 175,
            "currency": "USD",
            "billing_cycle": "Monthly",
            "payment_terms": "Net 45",
            "billing_contact": "Jennifer Lee",
            "billing_email": "accounting@innovative.example.com"
        },
        "5": {
            "rate": 160,
            "currency": "USD",
            "billing_cycle": "Monthly",
            "payment_terms": "Net 30",
            "billing_contact": "Lisa Taylor",
            "billing_email": "finance@ecofriendly.example.com"
        }
    }
    
    # Store in session state
    st.session_state.clients = clients
    st.session_state.client_contacts = contacts
    st.session_state.client_projects = projects
    st.session_state.client_notes = notes
    st.session_state.client_billing = billing
    
    # Store client logos
    for client_id, client_data in clients.items():
        st.session_state.client_avatars[client_id] = client_data.get('logo')

def create_timesheet(entry):
    """Create a new timesheet entry"""
    payload = {"data": [entry]}
    response = api_request("POST", TIMESHEETS_ENDPOINT, data=payload)
    if response:
        add_notification("success", "Timesheet entry created successfully")
    return response

def update_timesheet(entry_id, updates):
    """Update an existing timesheet entry"""
    payload = {"data": [{"id": entry_id, **updates}]}
    response = api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)
    if response:
        add_notification("success", "Timesheet entry updated successfully")
    return response

def delete_timesheet(entry_id):
    """Delete a timesheet entry"""
    payload = {"data": [{"id": entry_id}]}
    response = api_request("DELETE", TIMESHEETS_ENDPOINT, data=payload)
    if response:
        add_notification("success", "Timesheet entry deleted successfully")
    return response

def get_user_name(user_id):
    """Get user name from user ID"""
    user_id = str(user_id)
    if user_id in st.session_state.users:
        return f"{st.session_state.users[user_id]['first_name']} {st.session_state.users[user_id]['last_name']}"
    return f"User {user_id}"

def get_jobcode_name(jobcode_id):
    """Get job code name from job code ID"""
    jobcode_id = str(jobcode_id)
    if jobcode_id in st.session_state.jobcodes:
        return st.session_state.jobcodes[jobcode_id]['name']
    return f"Job {jobcode_id}"

def get_client_for_jobcode(jobcode_id):
    """Get client associated with a job code"""
    # In a real implementation, this would look up the client-job relationship
    # Here we're using a simple mapping based on our sample data
    jobcode_id = str(jobcode_id)
    
    # Simple mapping for demo purposes
    job_to_client = {
        # Acme Corporation jobs
        "101": "1",
        "102": "1",
        "103": "1",
        # Global Enterprises jobs
        "201": "2",
        "202": "2",
        # Sunshine Retail jobs
        "301": "3",
        "302": "3",
        # Innovative Solutions jobs
        "401": "4",
        "402": "4",
        "403": "4",
        # EcoFriendly Products jobs
        "501": "5",
        "502": "5"
    }
    
    # Try to find a match in our job names
    if jobcode_id in st.session_state.jobcodes:
        job_name = st.session_state.jobcodes[jobcode_id]['name']
        for project_id, project_name in job_to_client.items():
            if project_id in job_name:
                return project_name
    
    # Default mapping for demo
    last_digit = int(jobcode_id) % 5
    return str(last_digit + 1) if last_digit > 0 else "1"

def format_duration(seconds):
    """Format duration in seconds to hours and minutes"""
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m"

def get_download_link(df, filename, text):
    """Generate a download link for a dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="btn-download">{text}</a>'
    return href

def add_notification(type, message):
    """Add a notification to the session state"""
    notification_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.notifications.append({
        "id": notification_id,
        "type": type,
        "message": message,
        "timestamp": timestamp,
        "read": False
    })
    
    # Keep only the last 50 notifications
    if len(st.session_state.notifications) > 50:
        st.session_state.notifications = st.session_state.notifications[-50:]

def create_client(client_data):
    """Create a new client"""
    # In a real implementation, this would call an API
    # Here we're just adding to our session state
    
    client_id = str(len(st.session_state.clients) + 1)
    client_data["id"] = client_id
    client_data["created_date"] = date.today().isoformat()
    
    # Generate avatar
    name_parts = client_data["name"].split()
    initials = "".join([name_part[0] for name_part in name_parts if name_part])[:2]
    client_data["logo"] = f"https://ui-avatars.com/api/?name={initials}&background=36b9cc&color=fff"
    
    # Add to session state
    st.session_state.clients[client_id] = client_data
    st.session_state.client_contacts[client_id] = []
    st.session_state.client_projects[client_id] = []
    st.session_state.client_notes[client_id] = []
    st.session_state.client_billing[client_id] = {
        "rate": 150,
        "currency": "USD",
        "billing_cycle": "Monthly",
        "payment_terms": "Net 30",
        "billing_contact": "",
        "billing_email": ""
    }
    st.session_state.client_avatars[client_id] = client_data["logo"]
    
    add_notification("success", f"Client '{client_data['name']}' created successfully")
    return client_id

def update_client(client_id, updates):
    """Update an existing client"""
    # In a real implementation, this would call an API
    # Here we're just updating our session state
    
    if client_id in st.session_state.clients:
        st.session_state.clients[client_id].update(updates)
        add_notification("success", f"Client '{st.session_state.clients[client_id]['name']}' updated successfully")
        return True
    
    add_notification("error", "Client not found")
    return False

def add_client_contact(client_id, contact_data):
    """Add a contact to a client"""
    if client_id in st.session_state.client_contacts:
        st.session_state.client_contacts[client_id].append(contact_data)
        add_notification("success", f"Contact added to {st.session_state.clients[client_id]['name']}")
        return True
    
    add_notification("error", "Client not found")
    return False

def add_client_project(client_id, project_data):
    """Add a project to a client"""
    if client_id in st.session_state.client_projects:
        project_data["id"] = str(int(time.time()))
        st.session_state.client_projects[client_id].append(project_data)
        add_notification("success", f"Project added to {st.session_state.clients[client_id]['name']}")
        return True
    
    add_notification("error", "Client not found")
    return False

def add_client_note(client_id, note_data):
    """Add a note to a client"""
    if client_id in st.session_state.client_notes:
        note_data["date"] = date.today().isoformat()
        st.session_state.client_notes[client_id].append(note_data)
        add_notification("success", f"Note added to {st.session_state.clients[client_id]['name']}")
        return True
    
    add_notification("error", "Client not found")
    return False

def update_client_billing(client_id, billing_data):
    """Update client billing information"""
    if client_id in st.session_state.client_billing:
        st.session_state.client_billing[client_id].update(billing_data)
        add_notification("success", f"Billing information updated for {st.session_state.clients[client_id]['name']}")
        return True
    
    add_notification("error", "Client not found")
    return False

def get_client_hours(client_id, start_date=None, end_date=None):
    """Get hours worked for a specific client"""
    if not start_date:
        start_date, end_date = st.session_state.date_range
    
    # Filter timesheets by date range
    filtered_timesheets = [
        t for t in st.session_state.timesheets
        if start_date <= datetime.strptime(t['date'], '%Y-%m-%d').date() <= end_date
    ]
    
    # Calculate hours for the client
    client_hours = 0
    for timesheet in filtered_timesheets:
        timesheet_client_id = get_client_for_jobcode(timesheet['jobcode_id'])
        if timesheet_client_id == client_id:
            client_hours += timesheet.get('duration', 0) / 3600
    
    return client_hours

def get_client_revenue(client_id, start_date=None, end_date=None):
    """Calculate revenue for a specific client"""
    hours = get_client_hours(client_id, start_date, end_date)
    rate = st.session_state.client_billing.get(client_id, {}).get('rate', 0)
    return hours * rate

def get_client_project_status(client_id):
    """Get status counts for client projects"""
    if client_id not in st.session_state.client_projects:
        return {"In Progress": 0, "Planning": 0, "Completed": 0, "On Hold": 0}
    
    status_counts = {"In Progress": 0, "Planning": 0, "Completed": 0, "On Hold": 0}
    for project in st.session_state.client_projects[client_id]:
        status = project.get('status', 'Unknown')
        if status in status_counts:
            status_counts[status] += 1
        else:
            status_counts[status] = 1
    
    return status_counts

def get_client_stats():
    """Get overall client statistics"""
    active_clients = sum(1 for c in st.session_state.clients.values() if c.get('status') == 'active')
    total_projects = sum(len(projects) for projects in st.session_state.client_projects.values())
    
    # Calculate total revenue
    total_revenue = sum(get_client_revenue(client_id) for client_id in st.session_state.clients)
    
    # Calculate average hourly rate
    rates = [billing.get('rate', 0) for billing in st.session_state.client_billing.values()]
    avg_rate = sum(rates) / len(rates) if rates else 0
    
    return {
        "active_clients": active_clients,
        "total_clients": len(st.session_state.clients),
        "total_projects": total_projects,
        "total_revenue": total_revenue,
        "avg_rate": avg_rate
    }

# --- Sidebar: Authentication and Navigation ---
with st.sidebar:
    st.markdown('<div class="sidebar-header">⏱️ TSheets Manager Pro</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Authentication Section
    st.markdown('<div class="sidebar-header">🔐 Authentication</div>', unsafe_allow_html=True)
    auth_action = st.radio("", ["Login", "Logout"], horizontal=True)

    if auth_action == "Login":
        token = st.text_input("API Token", type="password")
        login_col1, login_col2 = st.columns([3, 1])
        with login_col1:
            login_button = st.button("Authenticate", use_container_width=True)
        
        if login_button and token:
            st.session_state.auth_token = token
            user_check = api_request("GET", f"{BASE_URL}/current_user")
            if user_check:
                st.success("✅ Authentication successful!")
                load_data()
            else:
                st.session_state.auth_token = None
                st.error("❌ Invalid API token")
    else:
        if st.button("Confirm Logout", use_container_width=True):
            st.session_state.auth_token = None
            st.warning("Logged out successfully.")
    
    # Only show navigation when authenticated
    if st.session_state.auth_token:
        st.markdown("---")
        st.markdown('<div class="sidebar-header">📊 Navigation</div>', unsafe_allow_html=True)
        
        view_options = [
            "Dashboard", 
            "View Timesheets", 
            "Add Entry", 
            "Edit Entry",
            "Clients",
            "Reports",
            "Settings"
        ]
        
        selected_view = st.selectbox("Select View", view_options, index=view_options.index(st.session_state.view_mode))
        
        if selected_view != st.session_state.view_mode:
            st.session_state.view_mode = selected_view
            st.rerun()
        
        st.markdown("---")
        st.markdown('<div class="sidebar-header">🔍 Filters</div>', unsafe_allow_html=True)
        
        # Date Range Filter
        st.date_input(
            "Date Range",
            value=st.session_state.date_range,
            min_value=date(2020, 1, 1),
            max_value=date.today(),
            key="date_filter"
        )
        
        # User Filter
        user_options = {"all": "All Users"}
        if st.session_state.users:
            for user_id, user_data in st.session_state.users.items():
                user_options[user_id] = f"{user_data['first_name']} {user_data['last_name']}"
        
        st.selectbox(
            "Filter by User",
            options=list(user_options.keys()),
            format_func=lambda x: user_options[x],
            key="user_filter"
        )
        
        # Job Code Filter
        job_options = {"all": "All Job Codes"}
        if st.session_state.jobcodes:
            for job_id, job_data in st.session_state.jobcodes.items():
                job_options[job_id] = job_data['name']
        
        st.selectbox(
            "Filter by Job Code",
            options=list(job_options.keys()),
            format_func=lambda x: job_options[x],
            key="job_filter"
        )
        
        # Client Filter
        client_options = {"all": "All Clients"}
        if st.session_state.clients:
            for client_id, client_data in st.session_state.clients.items():
                client_options[client_id] = client_data['name']
        
        st.selectbox(
            "Filter by Client",
            options=list(client_options.keys()),
            format_func=lambda x: client_options[x],
            key="client_filter"
        )
        
        # Apply Filters Button
        if st.button("Apply Filters", use_container_width=True):
            st.session_state.date_range = st.session_state.date_filter
            st.session_state.selected_user = st.session_state.user_filter
            st.session_state.selected_jobcode = st.session_state.job_filter
            st.session_state.selected_client = st.session_state.client_filter
            load_data()
            st.success("Filters applied successfully!")
        
        st.markdown("---")
        st.button("🔄 Refresh Data", on_click=load_data, use_container_width=True)
        
        # Notifications
        st.markdown("---")
        unread_count = sum(1 for n in st.session_state.notifications if not n['read'])
        st.markdown(f'<div class="sidebar-header">🔔 Notifications ({unread_count})</div>', unsafe_allow_html=True)
        
        if st.session_state.notifications:
            for i, notification in enumerate(st.session_state.notifications[:5]):
                notification_type = notification['type']
                icon = "✅" if notification_type == "success" else "❌" if notification_type == "error" else "ℹ️"
                st.markdown(f"""
                <div style="font-size: 0.8rem; margin-bottom: 0.5rem;">
                    <span style="color: {'#1cc88a' if notification_type == 'success' else '#e74a3b' if notification_type == 'error' else '#4e73df'}">{icon} {notification['message']}</span>
                    <div style="font-size: 0.7rem; color: #858796;">{notification['timestamp']}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if len(st.session_state.notifications) > 5:
                st.markdown(f"<div style='font-size: 0.8rem; text-align: center;'>+{len(st.session_state.notifications) - 5} more</div>", unsafe_allow_html=True)
            
            if st.button("Mark All as Read", use_container_width=True):
                for notification in st.session_state.notifications:
                    notification['read'] = True
                st.rerun()
        else:
            st.info("No notifications")

# --- Main App Content ---
if not st.session_state.auth_token:
    st.markdown('<div class="main-header">⏱️ TSheets Manager Pro</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        <div class="card">
            <h2>Welcome to TSheets Manager Pro</h2>
            <p>This application allows you to manage your TSheets timesheets efficiently with advanced features:</p>
            <ul>
                <li>View and analyze timesheet data with interactive dashboards</li>
                <li>Add, edit, and delete timesheet entries</li>
                <li>Manage client profiles and projects</li>
                <li>Generate reports and export data</li>
                <li>Filter by date range, user, job code, and client</li>
            </ul>
            <p>Please authenticate via the sidebar to get started.</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="card">
            <h3>Getting Started</h3>
            <ol>
                <li>Generate an API token from your TSheets account</li>
                <li>Enter the token in the sidebar authentication section</li>
                <li>Click "Authenticate" to log in</li>
                <li>Navigate through the app using the sidebar options</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)
    
    st.info("Need help? Contact your TSheets administrator for assistance.")

elif st.session_state.loading:
    st.markdown('<div class="main-header">Loading Data...</div>', unsafe_allow_html=True)
    st.spinner()
    progress_bar = st.progress(0)
    for i in range(100):
        progress_bar.progress(i + 1)
        time.sleep(0.01)
    st.experimental_rerun()

else:
    # --- Dashboard View ---
    if st.session_state.view_mode == "Dashboard":
        st.markdown('<div class="main-header">📊 TSheets Dashboard</div>', unsafe_allow_html=True)
        
        # Summary metrics
        if st.session_state.timesheets:
            # Calculate metrics
            total_hours = sum(entry.get('duration', 0) for entry in st.session_state.timesheets) / 3600
            unique_users = len(set(str(entry.get('user_id')) for entry in st.session_state.timesheets))
            unique_jobs = len(set(str(entry.get('jobcode_id')) for entry in st.session_state.timesheets))
            avg_daily_hours = total_hours / len(set(entry.get('date') for entry in st.session_state.timesheets)) if st.session_state.timesheets else 0
            
            # Client stats
            client_stats = get_client_stats()
            
            # Display metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{total_hours:.1f}</div>
                    <div class="metric-label">Total Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{unique_users}</div>
                    <div class="metric-label">Active Users</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{client_stats['active_clients']}</div>
                    <div class="metric-label">Active Clients</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">${client_stats['total_revenue']:,.2f}</div>
                    <div class="metric-label">Total Revenue</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Create dataframe for charts
            df = pd.DataFrame(st.session_state.timesheets)
            df['user_name'] = df['user_id'].apply(get_user_name)
            df['jobcode_name'] = df['jobcode_id'].apply(get_jobcode_name)
            df['client_id'] = df['jobcode_id'].apply(get_client_for_jobcode)
            df['client_name'] = df['client_id'].apply(lambda x: st.session_state.clients.get(x, {}).get('name', f"Client {x}"))
            df['hours'] = df['duration'].apply(lambda x: x / 3600)
            df['date'] = pd.to_datetime(df['date'])
            
            # Dashboard tabs
            tab1, tab2, tab3 = st.tabs(["Time Tracking", "Client Overview", "Project Status"])
            
            with tab1:
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    st.markdown('<div class="sub-header">Hours by User</div>', unsafe_allow_html=True)
                    user_hours = df.groupby('user_name')['hours'].sum().reset_index().sort_values('hours', ascending=False)
                    
                    fig = px.bar(
                        user_hours,
                        x='user_name',
                        y='hours',
                        color='hours',
                        color_continuous_scale='Blues',
                        labels={'user_name': 'User', 'hours': 'Hours'},
                        height=400
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with chart_col2:
                    st.markdown('<div class="sub-header">Hours by Job Code</div>', unsafe_allow_html=True)
                    job_hours = df.groupby('jobcode_name')['hours'].sum().reset_index().sort_values('hours', ascending=False)
                    
                    fig = px.pie(
                        job_hours,
                        values='hours',
                        names='jobcode_name',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Blues_r,
                        height=400
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Time trend chart
                st.markdown('<div class="sub-header">Daily Hours Trend</div>', unsafe_allow_html=True)
                daily_hours = df.groupby(df['date'].dt.date)['hours'].sum().reset_index()
                daily_hours.columns = ['date', 'hours']
                
                fig = px.line(
                    daily_hours,
                    x='date',
                    y='hours',
                    markers=True,
                    labels={'date': 'Date', 'hours': 'Hours'},
                    height=300
                )
                fig.update_layout(xaxis_title='Date', yaxis_title='Hours')
                st.plotly_chart(fig, use_container_width=True)
            
            with tab2:
                # Client metrics
                client_col1, client_col2, client_col3 = st.columns(3)
                
                with client_col1:
                    st.markdown('<div class="sub-header">Hours by Client</div>', unsafe_allow_html=True)
                    client_hours = df.groupby('client_name')['hours'].sum().reset_index().sort_values('hours', ascending=False)
                    
                    fig = px.bar(
                        client_hours,
                        x='client_name',
                        y='hours',
                        color='hours',
                        color_continuous_scale='Viridis',
                        labels={'client_name': 'Client', 'hours': 'Hours'},
                        height=400
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
                
                with client_col2:
                    st.markdown('<div class="sub-header">Revenue by Client</div>', unsafe_allow_html=True)
                    
                    # Calculate revenue for each client
                    revenue_data = []
                    for client_id, client in st.session_state.clients.items():
                        revenue = get_client_revenue(client_id)
                        revenue_data.append({
                            "client_name": client['name'],
                            "revenue": revenue
                        })
                    
                    revenue_df = pd.DataFrame(revenue_data)
                    revenue_df = revenue_df.sort_values('revenue', ascending=False)
                    
                    fig = px.pie(
                        revenue_df,
                        values='revenue',
                        names='client_name',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Viridis,
                        height=400
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                with client_col3:
                    st.markdown('<div class="sub-header">Client Status</div>', unsafe_allow_html=True)
                    
                    # Count clients by status
                    status_counts = {"active": 0, "inactive": 0}
                    for client in st.session_state.clients.values():
                        status = client.get('status', 'unknown')
                        if status in status_counts:
                            status_counts[status] += 1
                        else:
                            status_counts[status] = 1
                    
                    status_df = pd.DataFrame({
                        "status": list(status_counts.keys()),
                        "count": list(status_counts.values())
                    })
                    
                    fig = px.bar(
                        status_df,
                        x='status',
                        y='count',
                        color='status',
                        color_discrete_map={"active": "#1cc88a", "inactive": "#e74a3b"},
                        labels={'status': 'Status', 'count': 'Count'},
                        height=400
                    )
                    fig.update_layout(xaxis_title='Status', yaxis_title='Count')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Client table
                st.markdown('<div class="sub-header">Client Overview</div>', unsafe_allow_html=True)
                
                client_table_data = []
                for client_id, client in st.session_state.clients.items():
                    hours = get_client_hours(client_id)
                    revenue = get_client_revenue(client_id)
                    project_count = len(st.session_state.client_projects.get(client_id, []))
                    
                    client_table_data.append({
                        "Client ID": client_id,
                        "Client Name": client['name'],
                        "Industry": client.get('industry', 'N/A'),
                        "Status": client.get('status', 'unknown'),
                        "Hours": f"{hours:.1f}",
                        "Revenue": f"${revenue:,.2f}",
                        "Projects": project_count,
                        "Hourly Rate": f"${st.session_state.client_billing.get(client_id, {}).get('rate', 0):,.2f}"
                    })
                
                client_df = pd.DataFrame(client_table_data)
                st.dataframe(client_df, use_container_width=True)
            
            with tab3:
                # Project status overview
                st.markdown('<div class="sub-header">Project Status Overview</div>', unsafe_allow_html=True)
                
                # Collect project status data
                status_data = {"In Progress": 0, "Planning": 0, "Completed": 0, "On Hold": 0}
                for client_id, projects in st.session_state.client_projects.items():
                    for project in projects:
                        status = project.get('status', 'Unknown')
                        if status in status_data:
                            status_data[status] += 1
                        else:
                            status_data[status] = 1
                
                status_df = pd.DataFrame({
                    "status": list(status_data.keys()),
                    "count": list(status_data.values())
                })
                
                project_col1, project_col2 = st.columns(2)
                
                with project_col1:
                    fig = px.pie(
                        status_df,
                        values='count',
                        names='status',
                        color='status',
                        color_discrete_map={
                            "In Progress": "#4e73df",
                            "Planning": "#f6c23e",
                            "Completed": "#1cc88a",
                            "On Hold": "#e74a3b"
                        },
                        height=400
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                with project_col2:
                    fig = px.bar(
                        status_df,
                        x='status',
                        y='count',
                        color='status',
                        color_discrete_map={
                            "In Progress": "#4e73df",
                            "Planning": "#f6c23e",
                            "Completed": "#1cc88a",
                            "On Hold": "#e74a3b"
                        },
                        labels={'status': 'Status', 'count': 'Count'},
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Project table
                st.markdown('<div class="sub-header">Project List</div>', unsafe_allow_html=True)
                
                project_table_data = []
                for client_id, projects in st.session_state.client_projects.items():
                    client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                    
                    for project in projects:
                        project_table_data.append({
                            "Project ID": project.get('id', 'N/A'),
                            "Project Name": project.get('name', 'Unnamed Project'),
                            "Client": client_name,
                            "Status": project.get('status', 'Unknown'),
                            "Deadline": project.get('deadline', 'N/A')
                        })
                
                project_df = pd.DataFrame(project_table_data)
                st.dataframe(project_df, use_container_width=True)
        else:
            st.info("No timesheet data available for the selected filters. Please adjust your filters or add new entries.")
    
    # --- View Timesheets ---
    elif st.session_state.view_mode == "View Timesheets":
        st.markdown('<div class="main-header">📋 Timesheet Overview</div>', unsafe_allow_html=True)
        
        if st.session_state.timesheets:
            # Create a dataframe for display
            data = []
            for t in st.session_state.timesheets:
                client_id = get_client_for_jobcode(t["jobcode_id"])
                client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                
                row = {
                    "ID": t["id"],
                    "User": get_user_name(t["user_id"]),
                    "Client": client_name,
                    "Job Code": get_jobcode_name(t["jobcode_id"]),
                    "Date": t["date"],
                    "Duration": format_duration(t.get("duration", 0)),
                    "Type": t["type"].capitalize(),
                    "Notes": t["notes"] if "notes" in t else ""
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Add search and filter options
            st.markdown('<div class="search-box">', unsafe_allow_html=True)
            search_col1, search_col2, search_col3 = st.columns([3, 2, 1])
            with search_col1:
                search_term = st.text_input("Search timesheets", placeholder="Enter user name, client, job code, or notes...")
            
            with search_col2:
                filter_options = st.multiselect(
                    "Filter by Type",
                    options=["Regular", "Manual"],
                    default=[]
                )
            
            with search_col3:
                sort_by = st.selectbox("Sort by", ["Date", "User", "Client", "Job Code", "Duration"])
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Apply filters
            if search_term:
                df = df[
                    df['User'].str.contains(search_term, case=False) |
                    df['Client'].str.contains(search_term, case=False) |
                    df['Job Code'].str.contains(search_term, case=False) |
                    df['Notes'].str.contains(search_term, case=False)
                ]
            
            if filter_options:
                df = df[df['Type'].isin(filter_options)]
            
            if sort_by == "Date":
                df = df.sort_values(by="Date", ascending=False)
            elif sort_by == "User":
                df = df.sort_values(by="User")
            elif sort_by == "Client":
                df = df.sort_values(by="Client")
            elif sort_by == "Job Code":
                df = df.sort_values(by="Job Code")
            elif sort_by == "Duration":
                # Extract hours and minutes for sorting
                df['Sort Duration'] = df['Duration'].apply(
                    lambda x: int(x.split('h')[0]) * 60 + int(x.split('h')[1].strip().split('m')[0])
                )
                df = df.sort_values(by="Sort Duration", ascending=False)
                df = df.drop(columns=['Sort Duration'])
            
            # Display the dataframe
            st.dataframe(df, use_container_width=True)
            
            # Export options
            export_col1, export_col2 = st.columns([3, 1])
            with export_col1:
                st.markdown(
                    get_download_link(df, "timesheets_export.csv", "📥 Download as CSV"),
                    unsafe_allow_html=True
                )
            
            # Actions for selected timesheet
            st.markdown('<div class="sub-header">Timesheet Actions</div>', unsafe_allow_html=True)
            selected_id = st.selectbox("Select Timesheet ID for Actions", df['ID'].tolist())
            
            action_col1, action_col2, action_col3 = st.columns(3)
            with action_col1:
                if st.button("View Details", use_container_width=True):
                    selected_entry = next((t for t in st.session_state.timesheets if t['id'] == selected_id), None)
                    if selected_entry:
                        st.json(selected_entry)
            
            with action_col2:
                if st.button("Edit Entry", use_container_width=True):
                    st.session_state.view_mode = "Edit Entry"
                    st.experimental_rerun()
            
            with action_col3:
                if st.button("Delete Entry", use_container_width=True):
                    if st.session_state.auth_token:
                        confirm = st.warning("Are you sure you want to delete this entry? This action cannot be undone.")
                        confirm_col1, confirm_col2 = st.columns(2)
                        with confirm_col1:
                            if st.button("Yes, Delete", key="confirm_delete", use_container_width=True):
                                response = delete_timesheet(selected_id)
                                if response:
                                    st.success("✅ Entry deleted successfully.")
                                    load_data()
                                else:
                                    st.error("❌ Failed to delete entry.")
                        with confirm_col2:
                            if st.button("Cancel", key="cancel_delete", use_container_width=True):
                                st.experimental_rerun()
        else:
            st.info("No timesheet data available for the selected filters.")
    
    # --- Add Entry ---
    elif st.session_state.view_mode == "Add Entry":
        st.markdown('<div class="main-header">➕ Add New Timesheet Entry</div>', unsafe_allow_html=True)
        
        with st.form("add_entry_form", clear_on_submit=True):
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
            # User and Job Code selection
            col1, col2, col3 = st.columns(3)
            with col1:
                user_options = {}
                if st.session_state.users:
                    for user_id, user_data in st.session_state.users.items():
                        user_options[user_id] = f"{user_data['first_name']} {user_data['last_name']}"
                
                user_id = st.selectbox(
                    "User",
                    options=list(user_options.keys()),
                    format_func=lambda x: user_options[x]
                )
            
            with col2:
                job_options = {}
                if st.session_state.jobcodes:
                    for job_id, job_data in st.session_state.jobcodes.items():
                        job_options[job_id] = job_data['name']
                
                jobcode_id = st.selectbox(
                    "Job Code",
                    options=list(job_options.keys()),
                    format_func=lambda x: job_options[x]
                )
            
            with col3:
                client_id = get_client_for_jobcode(jobcode_id)
                client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                st.text_input("Client", value=client_name, disabled=True)
            
            # Date and Time
            col1, col2, col3 = st.columns(3)
            with col1:
                entry_date = st.date_input("Entry Date", value=date.today())
            
            with col2:
                start_time = st.time_input("Start Time", value=datetime.now().time().replace(minute=0, second=0, microsecond=0))
            
            with col3:
                # Default to 1 hour after start time
                default_end = datetime.combine(date.today(), start_time) + timedelta(hours=1)
                end_time = st.time_input("End Time", value=default_end.time())
            
            # Entry type and notes
            col1, col2 = st.columns(2)
            with col1:
                entry_type = st.selectbox("Entry Type", ["regular", "manual"])
            
            with col2:
                notes = st.text_area("Notes", placeholder="Enter any notes about this timesheet entry...")
            
            # Custom fields
            st.markdown("### Custom Fields")
            custom_col1, custom_col2, custom_col3 = st.columns(3)
            with custom_col1:
                custom1 = st.text_input("Project Reference", placeholder="Project code, reference number, etc.")
            
            with custom_col2:
                custom2 = st.text_input("Task Category", placeholder="Design, Development, Meeting, etc.")
            
            with custom_col3:
                custom3 = st.text_input("Billable Status", placeholder="Billable, Non-billable, etc.")
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Validation before submission
            start_dt = datetime.combine(entry_date, start_time)
            end_dt = datetime.combine(entry_date, end_time)
            
            if end_dt <= start_dt:
                st.warning("End time must be after start time.")
            
            # Submit button
            submit_col1, submit_col2 = st.columns([3, 1])
            with submit_col2:
                submit_button = st.form_submit_button("Submit Entry", use_container_width=True)
            
            if submit_button:
                if end_dt <= start_dt:
                    st.error("❌ End time must be after start time.")
                else:
                    new_entry = {
                        "user_id": int(user_id),
                        "jobcode_id": int(jobcode_id),
                        "type": entry_type,
                        "start": start_dt.isoformat(),
                        "end": end_dt.isoformat(),
                        "date": entry_date.isoformat(),
                        "notes": notes,
                        "customfields": {
                            "19142": custom1,
                            "19144": custom2,
                            "19146": custom3
                        }
                    }
                    
                    response = create_timesheet(new_entry)
                    if response:
                        st.success("✅ Entry created successfully.")
                        load_data()
                    else:
                        st.error("❌ Failed to create entry.")
    
    # --- Edit Entry ---
    elif st.session_state.view_mode == "Edit Entry":
        st.markdown('<div class="main-header">✏️ Edit Timesheet Entry</div>', unsafe_allow_html=True)
        
        if st.session_state.timesheets:
            # Create a selection dataframe for better UX
            selection_data = []
            for t in st.session_state.timesheets:
                client_id = get_client_for_jobcode(t["jobcode_id"])
                client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                
                row = {
                    "ID": t["id"],
                    "User": get_user_name(t["user_id"]),
                    "Client": client_name,
                    "Job Code": get_jobcode_name(t["jobcode_id"]),
                    "Date": t["date"],
                    "Duration": format_duration(t.get("duration", 0))
                }
                selection_data.append(row)
            
            selection_df = pd.DataFrame(selection_data)
            
            # Display selection dataframe
            st.dataframe(selection_df, use_container_width=True)
            
            # Select entry to edit
            selected_id = st.selectbox("Select Entry ID to Edit", selection_df['ID'].tolist())
            selected = next(t for t in st.session_state.timesheets if t['id'] == selected_id)
            
            with st.form("edit_entry_form"):
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                
                # User and Job Code selection
                col1, col2, col3 = st.columns(3)
                with col1:
                    user_options = {}
                    if st.session_state.users:
                        for user_id, user_data in st.session_state.users.items():
                            user_options[user_id] = f"{user_data['first_name']} {user_data['last_name']}"
                    
                    new_user_id = st.selectbox(
                        "User",
                        options=list(user_options.keys()),
                        format_func=lambda x: user_options[x],
                        index=list(user_options.keys()).index(str(selected['user_id'])) if str(selected['user_id']) in user_options else 0
                    )
                
                with col2:
                    job_options = {}
                    if st.session_state.jobcodes:
                        for job_id, job_data in st.session_state.jobcodes.items():
                            job_options[job_id] = job_data['name']
                    
                    new_jobcode_id = st.selectbox(
                        "Job Code",
                        options=list(job_options.keys()),
                        format_func=lambda x: job_options[x],
                        index=list(job_options.keys()).index(str(selected['jobcode_id'])) if str(selected['jobcode_id']) in job_options else 0
                    )
                
                with col3:
                    client_id = get_client_for_jobcode(new_jobcode_id)
                    client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                    st.text_input("Client", value=client_name, disabled=True)
                
                # Parse existing dates and times
                try:
                    start_dt = datetime.fromisoformat(selected['start'].replace('Z', '+00:00'))
                    end_dt = datetime.fromisoformat(selected['end'].replace('Z', '+00:00'))
                    entry_date = datetime.strptime(selected['date'], '%Y-%m-%d').date()
                except (ValueError, KeyError):
                    start_dt = datetime.now()
                    end_dt = datetime.now() + timedelta(hours=1)
                    entry_date = date.today()
                
                # Date and Time
                col1, col2, col3 = st.columns(3)
                with col1:
                    new_date = st.date_input("Entry Date", value=entry_date)
                
                with col2:
                    new_start_time = st.time_input("Start Time", value=start_dt.time())
                
                with col3:
                    new_end_time = st.time_input("End Time", value=end_dt.time())
                
                # Entry type and notes
                col1, col2 = st.columns(2)
                with col1:
                    new_type = st.selectbox(
                        "Type",
                        ["regular", "manual"],
                        index=0 if selected['type'] == "regular" else 1
                    )
                
                with col2:
                    new_notes = st.text_area("Notes", value=selected.get('notes', ''))
                
                # Custom fields
                st.markdown("### Custom Fields")
                custom_fields = selected.get('customfields', {})
                custom_col1, custom_col2, custom_col3 = st.columns(3)
                with custom_col1:
                    new_custom1 = st.text_input("Project Reference", value=custom_fields.get("19142", ""))
                
                with custom_col2:
                    new_custom2 = st.text_input("Task Category", value=custom_fields.get("19144", ""))
                
                with custom_col3:
                    new_custom3 = st.text_input("Billable Status", value=custom_fields.get("19146", ""))
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Validation before submission
                new_start_dt = datetime.combine(new_date, new_start_time)
                new_end_dt = datetime.combine(new_date, new_end_time)
                
                if new_end_dt <= new_start_dt:
                    st.warning("End time must be after start time.")
                
                # Submit button
                submit_col1, submit_col2, submit_col3 = st.columns([2, 2, 1])
                with submit_col3:
                    update_button = st.form_submit_button("Update Entry", use_container_width=True)
                
                if update_button:
                    if new_end_dt <= new_start_dt:
                        st.error("❌ End time must be after start time.")
                    else:
                        updated_entry = {
                            "user_id": int(new_user_id),
                            "jobcode_id": int(new_jobcode_id),
                            "type": new_type,
                            "start": new_start_dt.isoformat(),
                            "end": new_end_dt.isoformat(),
                            "date": new_date.isoformat(),
                            "notes": new_notes,
                            "customfields": {
                                "19142": new_custom1,
                                "19144": new_custom2,
                                "19146": new_custom3
                            }
                        }
                        
                        response = update_timesheet(selected_id, updated_entry)
                        if response:
                            st.success("✅ Entry updated successfully.")
                            load_data()
                        else:
                            st.error("❌ Failed to update entry.")
        else:
            st.info("No entries available to edit. Please adjust your filters or add new entries.")
    
    # --- Clients View ---
    elif st.session_state.view_mode == "Clients":
        st.markdown('<div class="main-header">👥 Client Management</div>', unsafe_allow_html=True)
        
        # Client tabs
        tab1, tab2, tab3 = st.tabs(["Client List", "Add Client", "Client Details"])
        
        with tab1:
            # Client list
            st.markdown('<div class="sub-header">Client Directory</div>', unsafe_allow_html=True)
            
            # Search and filter
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                client_search = st.text_input("Search Clients", placeholder="Enter client name, industry, etc...")
            
            with search_col2:
                client_status_filter = st.selectbox(
                    "Filter by Status",
                    options=["All", "Active", "Inactive"],
                    index=0
                )
            
            # Display clients
            client_list = []
            for client_id, client in st.session_state.clients.items():
                # Apply filters
                if client_search and not (
                    client_search.lower() in client['name'].lower() or
                    client_search.lower() in client.get('industry', '').lower() or
                    client_search.lower() in client.get('address', '').lower()
                ):
                    continue
                
                if client_status_filter == "Active" and client.get('status') != "active":
                    continue
                
                if client_status_filter == "Inactive" and client.get('status') != "inactive":
                    continue
                
                client_list.append(client)
            
            if client_list:
                # Display clients in a grid
                cols = st.columns(3)
                for i, client in enumerate(client_list):
                    with cols[i % 3]:
                        client_id = client['id']
                        client_avatar = st.session_state.client_avatars.get(client_id, "https://ui-avatars.com/api/?name=CL&background=36b9cc&color=fff")
                        
                        st.markdown(f"""
                        <div class="client-card">
                            <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                                <img src="{client_avatar}" alt="{client['name']}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 1rem;">
                                <div>
                                    <div class="client-name">{client['name']}</div>
                                    <div style="font-size: 0.8rem; color: #858796;">{client.get('industry', 'N/A')}</div>
                                </div>
                            </div>
                            <div class="client-info">
                                <div><strong>Status:</strong> <span class="{'status-success' if client.get('status') == 'active' else 'status-danger'}">{client.get('status', 'Unknown').capitalize()}</span></div>
                                <div><strong>Projects:</strong> {len(st.session_state.client_projects.get(client_id, []))}</div>
                                <div><strong>Hours:</strong> {get_client_hours(client_id):.1f}</div>
                                <div><strong>Revenue:</strong> ${get_client_revenue(client_id):,.2f}</div>
                            </div>
                            <div style="margin-top: 1rem; text-align: center;">
                                <a href="#" onclick="javascript:document.getElementById('client-details-{client_id}').click(); return false;" style="text-decoration: none; color: #4e73df;">View Details</a>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Hidden button to trigger client details
                        if st.button("View Details", key=f"client-details-{client_id}", use_container_width=True):
                            st.session_state.selected_client = client_id
                            st.experimental_rerun()
            else:
                st.info("No clients found matching your search criteria.")
        
        with tab2:
            # Add new client
            st.markdown('<div class="sub-header">Add New Client</div>', unsafe_allow_html=True)
            
            with st.form("add_client_form", clear_on_submit=True):
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                
                # Basic information
                col1, col2 = st.columns(2)
                with col1:
                    new_client_name = st.text_input("Client Name", placeholder="Enter client name")
                
                with col2:
                    new_client_industry = st.selectbox(
                        "Industry",
                        options=["Technology", "Finance", "Healthcare", "Education", "Retail", "Manufacturing", "Consulting", "Other"]
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    new_client_status = st.selectbox("Status", options=["active", "inactive"], index=0)
                
                with col2:
                    new_client_website = st.text_input("Website", placeholder="https://example.com")
                
                new_client_address = st.text_area("Address", placeholder="Enter client address")
                
                # Contact information
                st.markdown("### Primary Contact")
                contact_col1, contact_col2 = st.columns(2)
                with contact_col1:
                    contact_name = st.text_input("Contact Name", placeholder="Enter contact name")
                
                with contact_col2:
                    contact_title = st.text_input("Title", placeholder="CEO, CTO, etc.")
                
                contact_col1, contact_col2 = st.columns(2)
                with contact_col1:
                    contact_email = st.text_input("Email", placeholder="contact@example.com")
                
                with contact_col2:
                    contact_phone = st.text_input("Phone", placeholder="555-123-4567")
                
                # Billing information
                st.markdown("### Billing Information")
                billing_col1, billing_col2 = st.columns(2)
                with billing_col1:
                    billing_rate = st.number_input("Hourly Rate ($)", min_value=0.0, value=150.0, step=5.0)
                
                with billing_col2:
                    billing_cycle = st.selectbox(
                        "Billing Cycle",
                        options=["Weekly", "Bi-weekly", "Monthly", "Quarterly"],
                        index=2
                    )
                
                billing_col1, billing_col2 = st.columns(2)
                with billing_col1:
                    payment_terms = st.selectbox(
                        "Payment Terms",
                        options=["Net 15", "Net 30", "Net 45", "Net 60"],
                        index=1
                    )
                
                with billing_col2:
                    billing_email = st.text_input("Billing Email", placeholder="billing@example.com")
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Submit button
                submit_col1, submit_col2 = st.columns([3, 1])
                with submit_col2:
                    submit_button = st.form_submit_button("Add Client", use_container_width=True)
                
                if submit_button:
                    if not new_client_name:
                        st.error("❌ Client name is required.")
                    else:
                        # Create client
                        client_data = {
                            "name": new_client_name,
                            "industry": new_client_industry,
                            "status": new_client_status,
                            "website": new_client_website,
                            "address": new_client_address
                        }
                        
                        client_id = create_client(client_data)
                        
                        # Add contact
                        if contact_name:
                            contact_data = {
                                "name": contact_name,
                                "title": contact_title,
                                "email": contact_email,
                                "phone": contact_phone
                            }
                            add_client_contact(client_id, contact_data)
                        
                        # Add billing info
                        billing_data = {
                            "rate": billing_rate,
                            "currency": "USD",
                            "billing_cycle": billing_cycle,
                            "payment_terms": payment_terms,
                            "billing_contact": contact_name,
                            "billing_email": billing_email
                        }
                        update_client_billing(client_id, billing_data)
                        
                        st.success(f"✅ Client '{new_client_name}' added successfully.")
        
        with tab3:
            # Client details
            if st.session_state.selected_client != "all" and st.session_state.selected_client in st.session_state.clients:
                client_id = st.session_state.selected_client
                client = st.session_state.clients[client_id]
                
                # Client header
                client_avatar = st.session_state.client_avatars.get(client_id, "https://ui-avatars.com/api/?name=CL&background=36b9cc&color=fff")
                
                st.markdown(f"""
                <div style="display: flex; align-items: center; margin-bottom: 1.5rem;">
                    <img src="{client_avatar}" alt="{client['name']}" class="avatar-large">
                    <div style="margin-left: 1.5rem;">
                        <div style="font-size: 2rem; font-weight: 700; color: #2c3e50;">{client['name']}</div>
                        <div style="font-size: 1.2rem; color: #5a5c69;">{client.get('industry', 'N/A')}</div>
                        <div style="margin-top: 0.5rem;">
                            <span class="badge badge-{'success' if client.get('status') == 'active' else 'danger'}">{client.get('status', 'Unknown').capitalize()}</span>
                            <span class="badge badge-info">Client #{client_id}</span>
                            <span class="badge badge-secondary">Since {client.get('created_date', 'N/A')}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Client details tabs
                client_tab1, client_tab2, client_tab3, client_tab4 = st.tabs(["Overview", "Projects", "Contacts", "Billing"])
                
                with client_tab1:
                    # Client overview
                    overview_col1, overview_col2 = st.columns([2, 1])
                    
                    with overview_col1:
                        st.markdown('<div class="sub-header">Client Information</div>', unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="form-section">
                            <div style="margin-bottom: 1rem;"><strong>Website:</strong> <a href="{client.get('website', '#')}" target="_blank">{client.get('website', 'N/A')}</a></div>
                            <div style="margin-bottom: 1rem;"><strong>Address:</strong> {client.get('address', 'N/A')}</div>
                            <div style="margin-bottom: 1rem;"><strong>Created Date:</strong> {client.get('created_date', 'N/A')}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Client notes
                        st.markdown('<div class="sub-header">Notes</div>', unsafe_allow_html=True)
                        
                        notes = st.session_state.client_notes.get(client_id, [])
                        if notes:
                            for note in sorted(notes, key=lambda x: x.get('date', ''), reverse=True):
                                st.markdown(f"""
                                <div style="background-color: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.8rem;">
                                    <div style="font-size: 0.8rem; color: #858796; margin-bottom: 0.3rem;">{note.get('date', 'N/A')} - {note.get('author', 'Unknown')}</div>
                                    <div>{note.get('content', '')}</div>
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No notes available for this client.")
                        
                        # Add note
                        with st.form("add_note_form", clear_on_submit=True):
                            new_note = st.text_area("Add Note", placeholder="Enter a new note about this client...")
                            note_col1, note_col2 = st.columns([3, 1])
                            with note_col2:
                                add_note_button = st.form_submit_button("Add Note", use_container_width=True)
                            
                            if add_note_button and new_note:
                                note_data = {
                                    "author": "Current User",  # In a real app, this would be the logged-in user
                                    "content": new_note
                                }
                                add_client_note(client_id, note_data)
                                st.success("✅ Note added successfully.")
                                st.experimental_rerun()
                    
                    with overview_col2:
                        # Client metrics
                        hours = get_client_hours(client_id)
                        revenue = get_client_revenue(client_id)
                        project_count = len(st.session_state.client_projects.get(client_id, []))
                        contact_count = len(st.session_state.client_contacts.get(client_id, []))
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{hours:.1f}</div>
                            <div class="metric-label">Total Hours</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">${revenue:,.2f}</div>
                            <div class="metric-label">Total Revenue</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{project_count}</div>
                            <div class="metric-label">Active Projects</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class="metric-card">
                            <div class="metric-value">{contact_count}</div>
                            <div class="metric-label">Contacts</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Project status
                        st.markdown('<div class="sub-header">Project Status</div>', unsafe_allow_html=True)
                        
                        status_counts = get_client_project_status(client_id)
                        status_df = pd.DataFrame({
                            "status": list(status_counts.keys()),
                            "count": list(status_counts.values())
                        })
                        
                        fig = px.pie(
                            status_df,
                            values='count',
                            names='status',
                            color='status',
                            color_discrete_map={
                                "In Progress": "#4e73df",
                                "Planning": "#f6c23e",
                                "Completed": "#1cc88a",
                                "On Hold": "#e74a3b"
                            },
                            height=300
                        )
                        fig.update_traces(textposition='inside', textinfo='percent+label')
                        st.plotly_chart(fig, use_container_width=True)
                
                with client_tab2:
                    # Client projects
                    st.markdown('<div class="sub-header">Projects</div>', unsafe_allow_html=True)
                    
                    projects = st.session_state.client_projects.get(client_id, [])
                    if projects:
                        # Display projects
                        for project in projects:
                            status_color = {
                                "In Progress": "#4e73df",
                                "Planning": "#f6c23e",
                                "Completed": "#1cc88a",
                                "On Hold": "#e74a3b"
                            }.get(project.get('status', 'Unknown'), "#858796")
                            
                            st.markdown(f"""
                            <div style="background-color: #ffffff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.8rem; box-shadow: 0 0.15rem 0.5rem 0 rgba(58, 59, 69, 0.1); border-left: 4px solid {status_color};">
                                <div style="display: flex; justify-content: space-between; align-items: center;">
                                    <div>
                                        <div style="font-size: 1.2rem; font-weight: 600; color: #2c3e50;">{project.get('name', 'Unnamed Project')}</div>
                                        <div style="font-size: 0.9rem; color: #5a5c69;">Status: <span style="color: {status_color};">{project.get('status', 'Unknown')}</span></div>
                                    </div>
                                    <div style="text-align: right;">
                                        <div style="font-size: 0.9rem; color: #5a5c69;">Deadline: {project.get('deadline', 'N/A')}</div>
                                        <div style="font-size: 0.9rem; color: #5a5c69;">ID: {project.get('id', 'N/A')}</div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No projects available for this client.")
                    
                    # Add project
                    st.markdown('<div class="sub-header">Add New Project</div>', unsafe_allow_html=True)
                    
                    with st.form("add_project_form", clear_on_submit=True):
                        project_col1, project_col2 = st.columns(2)
                        with project_col1:
                            project_name = st.text_input("Project Name", placeholder="Enter project name")
                        
                        with project_col2:
                            project_status = st.selectbox(
                                "Status",
                                options=["Planning", "In Progress", "On Hold", "Completed"],
                                index=0
                            )
                        
                        project_deadline = st.date_input("Deadline", value=date.today() + timedelta(days=30))
                        
                        project_col1, project_col2 = st.columns([3, 1])
                        with project_col2:
                            add_project_button = st.form_submit_button("Add Project", use_container_width=True)
                        
                        if add_project_button:
                            if not project_name:
                                st.error("❌ Project name is required.")
                            else:
                                project_data = {
                                    "name": project_name,
                                    "status": project_status,
                                    "deadline": project_deadline.isoformat()
                                }
                                add_client_project(client_id, project_data)
                                st.success("✅ Project added successfully.")
                                st.experimental_rerun()
                
                with client_tab3:
                    # Client contacts
                    st.markdown('<div class="sub-header">Contacts</div>', unsafe_allow_html=True)
                    
                    contacts = st.session_state.client_contacts.get(client_id, [])
                    if contacts:
                        # Display contacts
                        contact_cols = st.columns(2)
                        for i, contact in enumerate(contacts):
                            with contact_cols[i % 2]:
                                st.markdown(f"""
                                <div class="client-contact">
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50;">{contact.get('name', 'Unnamed Contact')}</div>
                                    <div style="font-size: 0.9rem; color: #5a5c69;">{contact.get('title', 'N/A')}</div>
                                    <div style="margin-top: 0.5rem;">
                                        <div style="font-size: 0.9rem;"><strong>Email:</strong> <a href="mailto:{contact.get('email', '#')}">{contact.get('email', 'N/A')}</a></div>
                                        <div style="font-size: 0.9rem;"><strong>Phone:</strong> {contact.get('phone', 'N/A')}</div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
                    else:
                        st.info("No contacts available for this client.")
                    
                    # Add contact
                    st.markdown('<div class="sub-header">Add New Contact</div>', unsafe_allow_html=True)
                    
                    with st.form("add_contact_form", clear_on_submit=True):
                        contact_col1, contact_col2 = st.columns(2)
                        with contact_col1:
                            contact_name = st.text_input("Contact Name", placeholder="Enter contact name", key="new_contact_name")
                        
                        with contact_col2:
                            contact_title = st.text_input("Title", placeholder="CEO, CTO, etc.", key="new_contact_title")
                        
                        contact_col1, contact_col2 = st.columns(2)
                        with contact_col1:
                            contact_email = st.text_input("Email", placeholder="contact@example.com", key="new_contact_email")
                        
                        with contact_col2:
                            contact_phone = st.text_input("Phone", placeholder="555-123-4567", key="new_contact_phone")
                        
                        contact_col1, contact_col2 = st.columns([3, 1])
                        with contact_col2:
                            add_contact_button = st.form_submit_button("Add Contact", use_container_width=True)
                        
                        if add_contact_button:
                            if not contact_name:
                                st.error("❌ Contact name is required.")
                            else:
                                contact_data = {
                                    "name": contact_name,
                                    "title": contact_title,
                                    "email": contact_email,
                                    "phone": contact_phone
                                }
                                add_client_contact(client_id, contact_data)
                                st.success("✅ Contact added successfully.")
                                st.experimental_rerun()
                
                with client_tab4:
                    # Client billing
                    st.markdown('<div class="sub-header">Billing Information</div>', unsafe_allow_html=True)
                    
                    billing = st.session_state.client_billing.get(client_id, {})
                    
                    with st.form("edit_billing_form"):
                        billing_col1, billing_col2 = st.columns(2)
                        with billing_col1:
                            billing_rate = st.number_input(
                                "Hourly Rate ($)",
                                min_value=0.0,
                                value=float(billing.get('rate', 150.0)),
                                step=5.0
                            )
                        
                        with billing_col2:
                            billing_cycle = st.selectbox(
                                "Billing Cycle",
                                options=["Weekly", "Bi-weekly", "Monthly", "Quarterly"],
                                index=["Weekly", "Bi-weekly", "Monthly", "Quarterly"].index(billing.get('billing_cycle', "Monthly"))
                            )
                        
                        billing_col1, billing_col2 = st.columns(2)
                        with billing_col1:
                            payment_terms = st.selectbox(
                                "Payment Terms",
                                options=["Net 15", "Net 30", "Net 45", "Net 60"],
                                index=["Net 15", "Net 30", "Net 45", "Net 60"].index(billing.get('payment_terms', "Net 30"))
                            )
                        
                        with billing_col2:
                            billing_currency = st.selectbox(
                                "Currency",
                                options=["USD", "EUR", "GBP", "CAD", "AUD"],
                                index=["USD", "EUR", "GBP", "CAD", "AUD"].index(billing.get('currency', "USD"))
                            )
                        
                        billing_col1, billing_col2 = st.columns(2)
                        with billing_col1:
                            billing_contact = st.text_input(
                                "Billing Contact",
                                value=billing.get('billing_contact', ""),
                                placeholder="Enter billing contact name"
                            )
                        
                        with billing_col2:
                            billing_email = st.text_input(
                                "Billing Email",
                                value=billing.get('billing_email', ""),
                                placeholder="billing@example.com"
                            )
                        
                        billing_col1, billing_col2 = st.columns([3, 1])
                        with billing_col2:
                            update_billing_button = st.form_submit_button("Update Billing", use_container_width=True)
                        
                        if update_billing_button:
                            billing_data = {
                                "rate": billing_rate,
                                "currency": billing_currency,
                                "billing_cycle": billing_cycle,
                                "payment_terms": payment_terms,
                                "billing_contact": billing_contact,
                                "billing_email": billing_email
                            }
                            update_client_billing(client_id, billing_data)
                            st.success("✅ Billing information updated successfully.")
                            st.experimental_rerun()
                    
                    # Billing history
                    st.markdown('<div class="sub-header">Billing History</div>', unsafe_allow_html=True)
                    
                    # In a real app, this would show actual invoices
                    # Here we'll simulate some billing history
                    
                    # Generate some sample billing history
                    today = date.today()
                    billing_history = []
                    
                    for i in range(3):
                        invoice_date = today.replace(day=1) - timedelta(days=i*30)
                        hours = get_client_hours(
                            client_id,
                            invoice_date.replace(day=1),
                            (invoice_date.replace(day=28) if invoice_date.month != 2 else invoice_date.replace(day=28))
                        )
                        amount = hours * billing.get('rate', 150.0)
                        
                        billing_history.append({
                            "invoice_id": f"INV-{client_id}-{invoice_date.strftime('%Y%m')}",
                            "date": invoice_date.strftime("%Y-%m-%d"),
                            "period": invoice_date.strftime("%B %Y"),
                            "hours": hours,
                            "amount": amount,
                            "status": "Paid" if i > 0 else "Pending"
                        })
                    
                    if billing_history:
                        for invoice in billing_history:
                            status_color = "#1cc88a" if invoice["status"] == "Paid" else "#f6c23e"
                            
                            st.markdown(f"""
                            <div style="background-color: #ffffff; padding: 1rem; border-radius: 0.5rem; margin-bottom: 0.8rem; box-shadow: 0 0.15rem 0.5rem 0 rgba(58, 59, 69, 0.1); display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50;">{invoice["invoice_id"]}</div>
                                    <div style="font-size: 0.9rem; color: #5a5c69;">Period: {invoice["period"]}</div>
                                    <div style="font-size: 0.9rem; color: #5a5c69;">Date: {invoice["date"]}</div>
                                </div>
                                <div style="text-align: right;">
                                    <div style="font-size: 1.1rem; font-weight: 600; color: #2c3e50;">${invoice["amount"]:,.2f}</div>
                                    <div style="font-size: 0.9rem; color: #5a5c69;">{invoice["hours"]:.1f} hours</div>
                                    <div style="font-size: 0.9rem; color: {status_color};">{invoice["status"]}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.info("No billing history available for this client.")
            else:
                st.info("Select a client from the Client List tab to view details.")
    
    # --- Reports ---
    elif st.session_state.view_mode == "Reports":
        st.markdown('<div class="main-header">📊 Reports</div>', unsafe_allow_html=True)
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Hours by User", "Hours by Job Code", "Hours by Client", "Daily Summary", "Weekly Summary", "Client Revenue", "Custom Report"]
        )
        
        if st.session_state.timesheets:
            # Create dataframe for reports
            df = pd.DataFrame(st.session_state.timesheets)
            df['user_name'] = df['user_id'].apply(get_user_name)
            df['jobcode_name'] = df['jobcode_id'].apply(get_jobcode_name)
            df['client_id'] = df['jobcode_id'].apply(get_client_for_jobcode)
            df['client_name'] = df['client_id'].apply(lambda x: st.session_state.clients.get(x, {}).get('name', f"Client {x}"))
            df['hours'] = df['duration'].apply(lambda x: x / 3600)
            df['date'] = pd.to_datetime(df['date'])
            df['week'] = df['date'].dt.isocalendar().week
            df['month'] = df['date'].dt.month
            df['year'] = df['date'].dt.year
            
            if report_type == "Hours by User":
                st.markdown('<div class="sub-header">Hours by User Report</div>', unsafe_allow_html=True)
                
                # Group by user
                user_hours = df.groupby('user_name')['hours'].agg(['sum', 'mean', 'count']).reset_index()
                user_hours.columns = ['User', 'Total Hours', 'Average Hours', 'Entry Count']
                user_hours = user_hours.sort_values('Total Hours', ascending=False)
                
                # Display table
                st.dataframe(user_hours, use_container_width=True)
                
                # Chart
                fig = px.bar(
                    user_hours,
                    x='User',
                    y='Total Hours',
                    color='Total Hours',
                    text='Total Hours',
                    color_continuous_scale='Blues',
                    labels={'User': 'User', 'Total Hours': 'Total Hours'},
                    height=400
                )
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(user_hours, "hours_by_user.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Hours by Job Code":
                st.markdown('<div class="sub-header">Hours by Job Code Report</div>', unsafe_allow_html=True)
                
                # Group by job code
                job_hours = df.groupby('jobcode_name')['hours'].agg(['sum', 'mean', 'count']).reset_index()
                job_hours.columns = ['Job Code', 'Total Hours', 'Average Hours', 'Entry Count']
                job_hours = job_hours.sort_values('Total Hours', ascending=False)
                
                # Display table
                st.dataframe(job_hours, use_container_width=True)
                
                # Chart
                fig = px.pie(
                    job_hours,
                    values='Total Hours',
                    names='Job Code',
                    hole=0.4,
                    color_discrete_sequence=px.colors.sequential.Blues_r,
                    height=400
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(job_hours, "hours_by_job_code.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Hours by Client":
                st.markdown('<div class="sub-header">Hours by Client Report</div>', unsafe_allow_html=True)
                
                # Group by client
                client_hours = df.groupby('client_name')['hours'].agg(['sum', 'mean', 'count']).reset_index()
                client_hours.columns = ['Client', 'Total Hours', 'Average Hours', 'Entry Count']
                client_hours = client_hours.sort_values('Total Hours', ascending=False)
                
                # Calculate revenue
                client_hours['Hourly Rate'] = client_hours['Client'].apply(
                    lambda x: next(
                        (st.session_state.client_billing.get(client_id, {}).get('rate', 0) 
                         for client_id, client in st.session_state.clients.items() 
                         if client.get('name') == x),
                        0
                    )
                )
                client_hours['Total Revenue'] = client_hours['Total Hours'] * client_hours['Hourly Rate']
                
                # Display table
                st.dataframe(client_hours, use_container_width=True)
                
                # Charts
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    fig = px.bar(
                        client_hours,
                        x='Client',
                        y='Total Hours',
                        color='Total Hours',
                        text='Total Hours',
                        color_continuous_scale='Viridis',
                        labels={'Client': 'Client', 'Total Hours': 'Total Hours'},
                        height=400
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with chart_col2:
                    fig = px.pie(
                        client_hours,
                        values='Total Revenue',
                        names='Client',
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.Viridis,
                        height=400
                    )
                    fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(client_hours, "hours_by_client.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Daily Summary":
                st.markdown('<div class="sub-header">Daily Summary Report</div>', unsafe_allow_html=True)
                
                # Group by date
                daily_hours = df.groupby(df['date'].dt.date).agg({
                    'hours': ['sum', 'mean', 'count'],
                    'user_id': 'nunique',
                    'jobcode_id': 'nunique',
                    'client_id': 'nunique'
                }).reset_index()
                
                daily_hours.columns = ['Date', 'Total Hours', 'Average Hours', 'Entry Count', 'Unique Users', 'Unique Jobs', 'Unique Clients']
                daily_hours = daily_hours.sort_values('Date', ascending=False)
                
                # Display table
                st.dataframe(daily_hours, use_container_width=True)
                
                # Chart
                fig = px.line(
                    daily_hours.sort_values('Date'),
                    x='Date',
                    y='Total Hours',
                    markers=True,
                    labels={'Date': 'Date', 'Total Hours': 'Total Hours'},
                    height=400
                )
                fig.update_layout(xaxis_title='Date', yaxis_title='Hours')
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(daily_hours, "daily_summary.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Weekly Summary":
                st.markdown('<div class="sub-header">Weekly Summary Report</div>', unsafe_allow_html=True)
                
                # Group by year and week
                weekly_hours = df.groupby([df['year'], df['week']]).agg({
                    'hours': ['sum', 'mean', 'count'],
                    'user_id': 'nunique',
                    'jobcode_id': 'nunique',
                    'client_id': 'nunique',
                    'date': ['min', 'max']
                }).reset_index()
                
                weekly_hours.columns = [
                    'Year', 'Week', 'Total Hours', 'Average Hours', 'Entry Count', 
                    'Unique Users', 'Unique Jobs', 'Unique Clients', 'Start Date', 'End Date'
                ]
                weekly_hours = weekly_hours.sort_values(['Year', 'Week'], ascending=[False, False])
                
                # Add week label
                weekly_hours['Week Label'] = weekly_hours.apply(
                    lambda x: f"Week {int(x['Week'])}: {x['Start Date'].strftime('%b %d')} - {x['End Date'].strftime('%b %d')}", 
                    axis=1
                )
                
                # Display table
                display_cols = [
                    'Week Label', 'Total Hours', 'Average Hours', 'Entry Count', 
                    'Unique Users', 'Unique Jobs', 'Unique Clients'
                ]
                st.dataframe(weekly_hours[display_cols], use_container_width=True)
                
                # Chart
                fig = px.bar(
                    weekly_hours.sort_values(['Year', 'Week']),
                    x='Week Label',
                    y='Total Hours',
                    color='Unique Users',
                    text='Total Hours',
                    labels={'Week Label': 'Week', 'Total Hours': 'Total Hours'},
                    height=400
                )
                fig.update_layout(xaxis_tickangle=-45)
                fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(weekly_hours[display_cols], "weekly_summary.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Client Revenue":
                st.markdown('<div class="sub-header">Client Revenue Report</div>', unsafe_allow_html=True)
                
                # Calculate revenue for each client
                revenue_data = []
                for client_id, client in st.session_state.clients.items():
                    hours = get_client_hours(client_id)
                    rate = st.session_state.client_billing.get(client_id, {}).get('rate', 0)
                    revenue = hours * rate
                    
                    # Get project counts by status
                    project_status = get_client_project_status(client_id)
                    
                    revenue_data.append({
                        "Client ID": client_id,
                        "Client Name": client['name'],
                        "Industry": client.get('industry', 'N/A'),
                        "Status": client.get('status', 'unknown'),
                        "Total Hours": hours,
                        "Hourly Rate": rate,
                        "Total Revenue": revenue,
                        "Projects In Progress": project_status.get("In Progress", 0),
                        "Projects Completed": project_status.get("Completed", 0),
                        "Projects Planned": project_status.get("Planning", 0),
                        "Projects On Hold": project_status.get("On Hold", 0)
                    })
                
                revenue_df = pd.DataFrame(revenue_data)
                revenue_df = revenue_df.sort_values('Total Revenue', ascending=False)
                
                # Display table
                st.dataframe(revenue_df, use_container_width=True)
                
                # Charts
                chart_col1, chart_col2 = st.columns(2)
                
                with chart_col1:
                    fig = px.bar(
                        revenue_df,
                        x='Client Name',
                        y='Total Revenue',
                        color='Industry',
                        text='Total Revenue',
                        labels={'Client Name': 'Client', 'Total Revenue': 'Revenue ($)'},
                        height=400
                    )
                    fig.update_layout(xaxis_tickangle=-45)
                    fig.update_traces(texttemplate='$%{text:.2f}', textposition='outside')
                    st.plotly_chart(fig, use_container_width=True)
                
                with chart_col2:
                    fig = px.scatter(
                        revenue_df,
                        x='Total Hours',
                        y='Total Revenue',
                        size='Total Revenue',
                        color='Industry',
                        hover_name='Client Name',
                        labels={'Total Hours': 'Hours', 'Total Revenue': 'Revenue ($)'},
                        height=400
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Export
                st.markdown(
                    get_download_link(revenue_df, "client_revenue.csv", "📥 Download Report as CSV"),
                    unsafe_allow_html=True
                )
            
            elif report_type == "Custom Report":
                st.markdown('<div class="sub-header">Custom Report Builder</div>', unsafe_allow_html=True)
                
                # Report configuration
                config_col1, config_col2 = st.columns(2)
                
                with config_col1:
                    group_by = st.multiselect(
                        "Group By",
                        options=["User", "Job Code", "Client", "Date", "Week", "Month", "Year"],
                        default=["User", "Client"]
                    )
                
                with config_col2:
                    metrics = st.multiselect(
                        "Metrics",
                        options=["Total Hours", "Average Hours", "Entry Count", "Unique Users", "Unique Jobs", "Unique Clients", "Revenue"],
                        default=["Total Hours", "Revenue"]
                    )
                
                # Map selections to dataframe columns
                group_map = {
                    "User": "user_name",
                    "Job Code": "jobcode_name",
                    "Client": "client_name",
                    "Date": df['date'].dt.date,
                    "Week": df['week'],
                    "Month": df['month'],
                    "Year": df['year']
                }
                
                metric_map = {
                    "Total Hours": ("hours", "sum"),
                    "Average Hours": ("hours", "mean"),
                    "Entry Count": ("hours", "count"),
                    "Unique Users": ("user_id", "nunique"),
                    "Unique Jobs": ("jobcode_id", "nunique"),
                    "Unique Clients": ("client_id", "nunique")
                }
                
                if group_by and metrics:
                    # Create groupby columns
                    groupby_cols = [group_map[g] for g in group_by]
                    
                    # Create aggregation dictionary
                    agg_dict = {metric_map[m][0]: metric_map[m][1] for m in metrics if m != "Revenue"}
                    
                    # Generate report
                    custom_report = df.groupby(groupby_cols).agg(agg_dict).reset_index()
                    
                    # Rename columns
                    column_map = {}
                    for i, g in enumerate(group_by):
                        column_map[custom_report.columns[i]] = g
                    
                    for m in metrics:
                        if m != "Revenue":
                            col_name = f"{metric_map[m][0]}_{metric_map[m][1]}"
                            if col_name in custom_report.columns:
                                column_map[col_name] = m
                    
                    custom_report = custom_report.rename(columns=column_map)
                    
                    # Add revenue calculation if selected
                    if "Revenue" in metrics and "Client" in group_by:
                        # Get hourly rates for clients
                        client_rates = {}
                        for client_id, billing in st.session_state.client_billing.items():
                            client_name = st.session_state.clients.get(client_id, {}).get('name', f"Client {client_id}")
                            client_rates[client_name] = billing.get('rate', 0)
                        
                        # Calculate revenue
                        custom_report["Revenue"] = custom_report.apply(
                            lambda x: x["Total Hours"] * client_rates.get(x["Client"], 0) if "Client" in x else 0,
                            axis=1
                        )
                    
                    # Display report
                    st.dataframe(custom_report, use_container_width=True)
                    
                    # Export
                    st.markdown(
                        get_download_link(custom_report, "custom_report.csv", "📥 Download Custom Report as CSV"),
                        unsafe_allow_html=True
                    )
                    
                    # Visualization options
                    if len(group_by) >= 1 and ("Total Hours" in metrics or "Revenue" in metrics):
                        viz_type = st.selectbox(
                            "Visualization Type",
                            options=["Bar Chart", "Pie Chart", "Line Chart", "Scatter Plot"],
                            index=0
                        )
                        
                        viz_metric = st.selectbox(
                            "Visualization Metric",
                            options=[m for m in metrics if m in ["Total Hours", "Revenue", "Entry Count"]],
                            index=0
                        )
                        
                        if viz_type == "Bar Chart":
                            fig = px.bar(
                                custom_report,
                                x=group_by[0],
                                y=viz_metric,
                                color=group_by[1] if len(group_by) > 1 else None,
                                barmode="group",
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif viz_type == "Pie Chart":
                            fig = px.pie(
                                custom_report,
                                values=viz_metric,
                                names=group_by[0],
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif viz_type == "Line Chart" and "Date" in group_by:
                            date_col = "Date"
                            fig = px.line(
                                custom_report.sort_values(date_col),
                                x=date_col,
                                y=viz_metric,
                                color=group_by[1] if len(group_by) > 1 and group_by[1] != "Date" else None,
                                markers=True,
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif viz_type == "Scatter Plot" and len(group_by) >= 2:
                            scatter_x = st.selectbox("X-Axis", options=metrics, index=0)
                            scatter_y = st.selectbox("Y-Axis", options=metrics, index=min(1, len(metrics)-1))
                            
                            # Continuing from where we left off - Custom Report scatter plot
                            fig = px.scatter(
                                custom_report,
                                x=scatter_x,
                                y=scatter_y,
                                color=group_by[0],
                                size=scatter_y,
                                hover_name=group_by[0],
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("Please select at least one grouping field and one metric.")
        else:
            st.info("No timesheet data available for reporting. Please adjust your filters or add new entries.")
    
    # --- Settings View ---
    elif st.session_state.view_mode == "Settings":
        st.markdown('<div class="main-header">⚙️ Settings</div>', unsafe_allow_html=True)
        
        # Settings tabs
        tab1, tab2, tab3 = st.tabs(["Application Settings", "User Profiles", "Export/Import"])
        
        with tab1:
            st.markdown('<div class="sub-header">Application Settings</div>', unsafe_allow_html=True)
            
            settings_col1, settings_col2 = st.columns(2)
            
            with settings_col1:
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown("### Display Settings")
                
                default_view = st.selectbox(
                    "Default View",
                    options=["Dashboard", "View Timesheets", "Add Entry", "Clients", "Reports"],
                    index=0
                )
                
                date_format = st.selectbox(
                    "Date Format",
                    options=["YYYY-MM-DD", "MM/DD/YYYY", "DD/MM/YYYY"],
                    index=0
                )
                
                time_format = st.selectbox(
                    "Time Format",
                    options=["24-hour", "12-hour (AM/PM)"],
                    index=0
                )
                
                items_per_page = st.slider("Items Per Page", min_value=10, max_value=100, value=25, step=5)
                
                st.markdown("### Notification Settings")
                
                enable_notifications = st.checkbox("Enable Notifications", value=True)
                notification_sound = st.checkbox("Play Sound on Notifications", value=False)
                
                if st.button("Save Display Settings", use_container_width=True):
                    st.success("✅ Settings saved successfully.")
                    add_notification("success", "Application settings updated")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with settings_col2:
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown("### API Settings")
                
                api_url = st.text_input("API URL", value=BASE_URL)
                api_timeout = st.number_input("API Timeout (seconds)", min_value=5, max_value=60, value=15)
                
                st.markdown("### Data Retention")
                
                cache_duration = st.slider("Cache Duration (minutes)", min_value=5, max_value=120, value=30, step=5)
                auto_refresh = st.checkbox("Auto-refresh Data", value=True)
                
                if auto_refresh:
                    refresh_interval = st.slider("Refresh Interval (minutes)", min_value=1, max_value=60, value=15, step=1)
                
                if st.button("Save API Settings", use_container_width=True):
                    st.success("✅ API settings saved successfully.")
                    add_notification("success", "API settings updated")
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        with tab2:
            st.markdown('<div class="sub-header">User Profiles</div>', unsafe_allow_html=True)
            
            # Display user profiles
            if st.session_state.users:
                user_cols = st.columns(3)
                for i, (user_id, user) in enumerate(st.session_state.users.items()):
                    with user_cols[i % 3]:
                        user_avatar = st.session_state.user_avatars.get(user_id, "https://ui-avatars.com/api/?name=UU&background=4e73df&color=fff")
                        
                        st.markdown(f"""
                        <div class="client-card">
                            <div style="display: flex; align-items: center; margin-bottom: 0.8rem;">
                                <img src="{user_avatar}" alt="{user['first_name']} {user['last_name']}" style="width: 50px; height: 50px; border-radius: 50%; margin-right: 1rem;">
                                <div>
                                    <div class="client-name">{user['first_name']} {user['last_name']}</div>
                                    <div style="font-size: 0.8rem; color: #858796;">{user.get('email', 'No email')}</div>
                                </div>
                            </div>
                            <div class="client-info">
                                <div><strong>Username:</strong> {user.get('username', 'N/A')}</div>
                                <div><strong>Role:</strong> {user.get('role', 'User')}</div>
                                <div><strong>Status:</strong> <span class="{'status-success' if user.get('active') else 'status-danger'}">{('Active' if user.get('active') else 'Inactive')}</span></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No user profiles available.")
            
            # User preferences
            st.markdown('<div class="sub-header">User Preferences</div>', unsafe_allow_html=True)
            
            with st.form("user_preferences_form"):
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                
                pref_col1, pref_col2 = st.columns(2)
                
                with pref_col1:
                    theme = st.selectbox(
                        "Theme",
                        options=["Light", "Dark", "System Default"],
                        index=0
                    )
                    
                    language = st.selectbox(
                        "Language",
                        options=["English", "Spanish", "French", "German", "Japanese"],
                        index=0
                    )
                
                with pref_col2:
                    timezone = st.selectbox(
                        "Timezone",
                        options=["UTC", "US/Eastern", "US/Central", "US/Pacific", "Europe/London", "Asia/Tokyo"],
                        index=0
                    )
                    
                    email_notifications = st.checkbox("Email Notifications", value=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
                
                if st.form_submit_button("Save Preferences", use_container_width=True):
                    st.success("✅ User preferences saved successfully.")
                    add_notification("success", "User preferences updated")
        
        with tab3:
            st.markdown('<div class="sub-header">Export/Import Data</div>', unsafe_allow_html=True)
            
            export_col1, export_col2 = st.columns(2)
            
            with export_col1:
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown("### Export Data")
                
                export_options = st.multiselect(
                    "Select Data to Export",
                    options=["Timesheets", "Users", "Job Codes", "Clients", "Projects", "All Data"],
                    default=["All Data"]
                )
                
                export_format = st.selectbox(
                    "Export Format",
                    options=["CSV", "JSON", "Excel"],
                    index=0
                )
                
                date_range_export = st.date_input(
                    "Date Range for Export",
                    value=st.session_state.date_range
                )
                
                if st.button("Export Data", use_container_width=True):
                    st.success("✅ Data exported successfully.")
                    
                    # Generate export links based on selected options
                    if "Timesheets" in export_options or "All Data" in export_options:
                        timesheet_df = pd.DataFrame(st.session_state.timesheets)
                        st.markdown(
                            get_download_link(timesheet_df, "timesheets_export.csv", "📥 Download Timesheets"),
                            unsafe_allow_html=True
                        )
                    
                    if "Clients" in export_options or "All Data" in export_options:
                        client_data = []
                        for client_id, client in st.session_state.clients.items():
                            client_data.append(client)
                        client_df = pd.DataFrame(client_data)
                        st.markdown(
                            get_download_link(client_df, "clients_export.csv", "📥 Download Clients"),
                            unsafe_allow_html=True
                        )
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with export_col2:
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                st.markdown("### Import Data")
                
                import_type = st.selectbox(
                    "Import Type",
                    options=["Timesheets", "Clients", "Projects", "Contacts"]
                )
                
                uploaded_file = st.file_uploader("Upload File", type=["csv", "json", "xlsx"])
                
                overwrite = st.checkbox("Overwrite Existing Data", value=False)
                
                if uploaded_file is not None:
                    if st.button("Import Data", use_container_width=True):
                        st.success("✅ Data imported successfully.")
                        add_notification("success", f"Imported {import_type} data")
                
                st.markdown('</div>', unsafe_allow_html=True)

# --- Create a short version of the app for quick access ---
def run_short_version():
    """Run a condensed version of the app with essential features only"""
    st.set_page_config(page_title="TSheets Quick", layout="wide")
    
    st.title("⏱️ TSheets Quick Access")
    
    # Authentication
    if 'auth_token' not in st.session_state or not st.session_state.auth_token:
        token = st.text_input("API Token", type="password")
        if st.button("Login"):
            st.session_state.auth_token = token
            st.experimental_rerun()
    else:
        # Quick actions
        st.subheader("Quick Actions")
        
        action_col1, action_col2, action_col3, action_col4 = st.columns(4)
        
        with action_col1:
            if st.button("Add Timesheet", use_container_width=True):
                st.session_state.quick_action = "add_timesheet"
        
        with action_col2:
            if st.button("View Today", use_container_width=True):
                st.session_state.quick_action = "view_today"
        
        with action_col3:
            if st.button("Client Summary", use_container_width=True):
                st.session_state.quick_action = "client_summary"
        
        with action_col4:
            if st.button("Logout", use_container_width=True):
                st.session_state.auth_token = None
                st.experimental_rerun()
        
        # Handle quick actions
        if 'quick_action' in st.session_state:
            if st.session_state.quick_action == "add_timesheet":
                with st.form("quick_add_form"):
                    st.subheader("Add Timesheet Entry")
                    
                    user_id = st.selectbox("User", options=["1", "2", "3"], format_func=lambda x: f"User {x}")
                    jobcode_id = st.selectbox("Job Code", options=["101", "102", "103"], format_func=lambda x: f"Job {x}")
                    hours = st.number_input("Hours", min_value=0.25, max_value=24.0, value=1.0, step=0.25)
                    notes = st.text_area("Notes")
                    
                    if st.form_submit_button("Submit"):
                        st.success("Entry added successfully!")
                        del st.session_state.quick_action
            
            elif st.session_state.quick_action == "view_today":
                st.subheader("Today's Entries")
                
                # Sample data for demonstration
                data = {
                    "User": ["John Doe", "Jane Smith", "Bob Johnson"],
                    "Job Code": ["Website Development", "Design", "Meeting"],
                    "Hours": [3.5, 2.0, 1.5],
                    "Notes": ["Frontend work", "Logo design", "Client call"]
                }
                
                st.dataframe(pd.DataFrame(data))
                
                if st.button("Back"):
                    del st.session_state.quick_action
            
            elif st.session_state.quick_action == "client_summary":
                st.subheader("Client Summary")
                
                # Sample data for demonstration
                data = {
                    "Client": ["Acme Corp", "Global Enterprises", "Sunshine Retail"],
                    "Hours": [45.5, 32.0, 18.5],
                    "Revenue": ["$6,825", "$4,800", "$2,775"],
                    "Projects": [3, 2, 1]
                }
                
                st.dataframe(pd.DataFrame(data))
                
                if st.button("Back"):
                    del st.session_state.quick_action

# Check if running in short mode
if len(sys.argv) > 1 and sys.argv[1] == "--short":
    run_short_version()
