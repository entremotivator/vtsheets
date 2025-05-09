import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta, date
import json
import io
import base64

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

# --- Custom CSS ---
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        margin-bottom: 0.8rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 0.5rem;
        background-color: #f8f9fa;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1.5rem;
    }
    .metric-card {
        text-align: center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #4e73df;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #5a5c69;
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
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
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
if 'date_range' not in st.session_state:
    st.session_state.date_range = (date.today() - timedelta(days=30), date.today())
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "Dashboard"
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = "all"
if 'selected_jobcode' not in st.session_state:
    st.session_state.selected_jobcode = "all"
if 'loading' not in st.session_state:
    st.session_state.loading = False

# --- Utility Functions ---
def api_request(method, url, params=None, data=None):
    """Make an API request to TSheets with proper error handling"""
    headers = {
        "Authorization": f"Bearer {st.session_state.auth_token}",
        "Content-Type": "application/json"
    }
    
    try:
        with st.spinner("Processing request..."):
            response = requests.request(method, url, headers=headers, params=params, json=data)
            
        if response.status_code == 401:
            st.error("Authentication failed. Please check your API token.")
            return None
            
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
        return None

def load_data():
    """Load all necessary data from TSheets API"""
    st.session_state.loading = True
    
    # Get users
    users_data = api_request("GET", USERS_ENDPOINT, params={"active": "yes"})
    if users_data and 'results' in users_data and 'users' in users_data['results']:
        st.session_state.users = {
            str(user_id): user_data 
            for user_id, user_data in users_data['results']['users'].items()
        }
    
    # Get job codes
    jobs_data = api_request("GET", JOBS_ENDPOINT, params={"active": "yes"})
    if jobs_data and 'results' in jobs_data and 'jobcodes' in jobs_data['results']:
        st.session_state.jobcodes = {
            str(job_id): job_data 
            for job_id, job_data in jobs_data['results']['jobcodes'].items()
        }
    
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

def create_timesheet(entry):
    """Create a new timesheet entry"""
    payload = {"data": [entry]}
    return api_request("POST", TIMESHEETS_ENDPOINT, data=payload)

def update_timesheet(entry_id, updates):
    """Update an existing timesheet entry"""
    payload = {"data": [{"id": entry_id, **updates}]}
    return api_request("PUT", TIMESHEETS_ENDPOINT, data=payload)

def delete_timesheet(entry_id):
    """Delete a timesheet entry"""
    payload = {"data": [{"id": entry_id}]}
    return api_request("DELETE", TIMESHEETS_ENDPOINT, data=payload)

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

def format_duration(seconds):
    """Format duration in seconds to hours and minutes"""
    hours, remainder = divmod(seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m"

def get_download_link(df, filename, text):
    """Generate a download link for a dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

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
            "Reports"
        ]
        
        selected_view = st.selectbox("Select View", view_options, index=view_options.index(st.session_state.view_mode))
        
        if selected_view != st.session_state.view_mode:
            st.session_state.view_mode = selected_view
            st.experimental_rerun()
        
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
        
        # Apply Filters Button
        if st.button("Apply Filters", use_container_width=True):
            st.session_state.date_range = st.session_state.date_filter
            st.session_state.selected_user = st.session_state.user_filter
            st.session_state.selected_jobcode = st.session_state.job_filter
            load_data()
            st.success("Filters applied successfully!")
        
        st.markdown("---")
        st.button("🔄 Refresh Data", on_click=load_data, use_container_width=True)

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
                <li>Generate reports and export data</li>
                <li>Filter by date range, user, and job code</li>
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
                    <div class="metric-value">{unique_jobs}</div>
                    <div class="metric-label">Active Job Codes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-value">{avg_daily_hours:.1f}</div>
                    <div class="metric-label">Avg. Daily Hours</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Create dataframe for charts
            df = pd.DataFrame(st.session_state.timesheets)
            df['user_name'] = df['user_id'].apply(get_user_name)
            df['jobcode_name'] = df['jobcode_id'].apply(get_jobcode_name)
            df['hours'] = df['duration'].apply(lambda x: x / 3600)
            df['date'] = pd.to_datetime(df['date'])
            
            # Charts
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
            
        else:
            st.info("No timesheet data available for the selected filters. Please adjust your filters or add new entries.")
    
    # --- View Timesheets ---
    elif st.session_state.view_mode == "View Timesheets":
        st.markdown('<div class="main-header">📋 Timesheet Overview</div>', unsafe_allow_html=True)
        
        if st.session_state.timesheets:
            # Create a dataframe for display
            data = []
            for t in st.session_state.timesheets:
                row = {
                    "ID": t["id"],
                    "User": get_user_name(t["user_id"]),
                    "Job Code": get_jobcode_name(t["jobcode_id"]),
                    "Date": t["date"],
                    "Duration": format_duration(t.get("duration", 0)),
                    "Type": t["type"].capitalize(),
                    "Notes": t["notes"] if "notes" in t else ""
                }
                data.append(row)
            
            df = pd.DataFrame(data)
            
            # Add search and filter options
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_term = st.text_input("Search timesheets", placeholder="Enter user name, job code, or notes...")
            
            with search_col2:
                sort_by = st.selectbox("Sort by", ["Date", "User", "Job Code", "Duration"])
            
            if search_term:
                df = df[
                    df['User'].str.contains(search_term, case=False) |
                    df['Job Code'].str.contains(search_term, case=False) |
                    df['Notes'].str.contains(search_term, case=False)
                ]
            
            if sort_by == "Date":
                df = df.sort_values(by="Date", ascending=False)
            elif sort_by == "User":
                df = df.sort_values(by="User")
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
                            if st.button("Yes, Delete", use_container_width=True):
                                response = delete_timesheet(selected_id)
                                if response:
                                    st.success("✅ Entry deleted successfully.")
                                    load_data()
                                else:
                                    st.error("❌ Failed to delete entry.")
                        with confirm_col2:
                            if st.button("Cancel", use_container_width=True):
                                st.experimental_rerun()
        else:
            st.info("No timesheet data available for the selected filters.")
    
    # --- Add Entry ---
    elif st.session_state.view_mode == "Add Entry":
        st.markdown('<div class="main-header">➕ Add New Timesheet Entry</div>', unsafe_allow_html=True)
        
        with st.form("add_entry_form", clear_on_submit=True):
            st.markdown('<div class="form-section">', unsafe_allow_html=True)
            
            # User and Job Code selection
            col1, col2 = st.columns(2)
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
            custom_col1, custom_col2 = st.columns(2)
            with custom_col1:
                custom1 = st.text_input("Custom Field 1", placeholder="Project code, reference number, etc.")
            
            with custom_col2:
                custom2 = st.text_input("Custom Field 2", placeholder="Additional information")
            
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
                            "19144": custom2
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
                row = {
                    "ID": t["id"],
                    "User": get_user_name(t["user_id"]),
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
                col1, col2 = st.columns(2)
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
                custom_col1, custom_col2 = st.columns(2)
                with custom_col1:
                    new_custom1 = st.text_input("Custom Field 1", value=custom_fields.get("19142", ""))
                
                with custom_col2:
                    new_custom2 = st.text_input("Custom Field 2", value=custom_fields.get("19144", ""))
                
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
                                "19144": new_custom2
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
    
    # --- Reports ---
    elif st.session_state.view_mode == "Reports":
        st.markdown('<div class="main-header">📊 Reports</div>', unsafe_allow_html=True)
        
        report_type = st.selectbox(
            "Select Report Type",
            ["Hours by User", "Hours by Job Code", "Daily Summary", "Weekly Summary", "Custom Report"]
        )
        
        if st.session_state.timesheets:
            # Create dataframe for reports
            df = pd.DataFrame(st.session_state.timesheets)
            df['user_name'] = df['user_id'].apply(get_user_name)
            df['jobcode_name'] = df['jobcode_id'].apply(get_jobcode_name)
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
            
            elif report_type == "Daily Summary":
                st.markdown('<div class="sub-header">Daily Summary Report</div>', unsafe_allow_html=True)
                
                # Group by date
                daily_hours = df.groupby(df['date'].dt.date).agg({
                    'hours': ['sum', 'mean', 'count'],
                    'user_id': 'nunique',
                    'jobcode_id': 'nunique'
                }).reset_index()
                
                daily_hours.columns = ['Date', 'Total Hours', 'Average Hours', 'Entry Count', 'Unique Users', 'Unique Jobs']
                daily_hours = daily_hours.sort_values('Date', ascending=False)
                
                # Display table
                st.dataframe(daily_hours, use_container_width=True)
                
                # Chart
                fig = px.line(
                    daily_hours,
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
                    'date': ['min', 'max']
                }).reset_index()
                
                weekly_hours.columns = [
                    'Year', 'Week', 'Total Hours', 'Average Hours', 'Entry Count', 
                    'Unique Users', 'Unique Jobs', 'Start Date', 'End Date'
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
                    'Unique Users', 'Unique Jobs'
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
            
            elif report_type == "Custom Report":
                st.markdown('<div class="sub-header">Custom Report Builder</div>', unsafe_allow_html=True)
                
                # Report configuration
                config_col1, config_col2 = st.columns(2)
                
                with config_col1:
                    group_by = st.multiselect(
                        "Group By",
                        options=["User", "Job Code", "Date", "Week", "Month", "Year"],
                        default=["User", "Job Code"]
                    )
                
                with config_col2:
                    metrics = st.multiselect(
                        "Metrics",
                        options=["Total Hours", "Average Hours", "Entry Count", "Unique Users", "Unique Jobs"],
                        default=["Total Hours", "Entry Count"]
                    )
                
                # Map selections to dataframe columns
                group_map = {
                    "User": "user_name",
                    "Job Code": "jobcode_name",
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
                    "Unique Jobs": ("jobcode_id", "nunique")
                }
                
                if group_by and metrics:
                    # Create groupby columns
                    groupby_cols = [group_map[g] for g in group_by]
                    
                    # Create aggregation dictionary
                    agg_dict = {metric_map[m][0]: metric_map[m][1] for m in metrics}
                    
                    # Generate report
                    custom_report = df.groupby(groupby_cols).agg(agg_dict).reset_index()
                    
                    # Rename columns
                    column_map = {}
                    for i, g in enumerate(group_by):
                        column_map[i] = g
                    
                    for m in metrics:
                        col_name = f"{metric_map[m][0]}_{metric_map[m][1]}"
                        if col_name in custom_report.columns:
                            column_map[col_name] = m
                    
                    custom_report = custom_report.rename(columns=column_map)
                    
                    # Display report
                    st.dataframe(custom_report, use_container_width=True)
                    
                    # Export
                    st.markdown(
                        get_download_link(custom_report, "custom_report.csv", "📥 Download Custom Report as CSV"),
                        unsafe_allow_html=True
                    )
                    
                    # Visualization options
                    if len(group_by) >= 1 and "Total Hours" in metrics:
                        viz_type = st.selectbox(
                            "Visualization Type",
                            options=["Bar Chart", "Pie Chart", "Line Chart"],
                            index=0
                        )
                        
                        if viz_type == "Bar Chart":
                            fig = px.bar(
                                custom_report,
                                x=group_by[0],
                                y="Total Hours",
                                color=group_by[1] if len(group_by) > 1 else None,
                                barmode="group",
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif viz_type == "Pie Chart":
                            fig = px.pie(
                                custom_report,
                                values="Total Hours",
                                names=group_by[0],
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                        
                        elif viz_type == "Line Chart" and "Date" in group_by:
                            date_col = group_by[group_by.index("Date")]
                            fig = px.line(
                                custom_report.sort_values(date_col),
                                x=date_col,
                                y="Total Hours",
                                color=group_by[1] if len(group_by) > 1 and group_by[1] != "Date" else None,
                                markers=True,
                                height=400
                            )
                            st.plotly_chart(fig, use_container_width=True)
                
                else:
                    st.warning("Please select at least one grouping field and one metric.")
        else:
            st.info("No timesheet data available for reporting. Please adjust your filters or add new entries.")

