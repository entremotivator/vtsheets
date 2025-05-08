import streamlit as st
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
import random
from PIL import Image
import altair as alt
from streamlit_calendar import calendar
from streamlit_option_menu import option_menu

# Set page configuration
st.set_page_config(
    page_title="TSheets CRM Manager",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
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
    .reportview-container .main .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-right: 2rem;
        padding-left: 2rem;
        padding-bottom: 2rem;
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
    .calendar-day {
        padding: 0.5rem;
        border-radius: 0.25rem;
        text-align: center;
    }
    .calendar-day-current {
        background-color: #f8f9fa;
    }
    .calendar-day-has-entries {
        background-color: #d4edda;
    }
    .calendar-day-header {
        font-weight: bold;
        text-align: center;
        padding: 0.5rem;
        background-color: #e9ecef;
        border-radius: 0.25rem;
    }
    .client-card {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1rem;
        box-shadow: 0 0.15rem 1.75rem 0 rgba(58, 59, 69, 0.15);
        margin-bottom: 1rem;
    }
    .client-card:hover {
        background-color: #e9ecef;
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
    }
    .timesheet-entry:hover {
        background-color: #e9ecef;
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
</style>
""", unsafe_allow_html=True)

# Utility functions
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
        
        if not df_timesheets.empty:
            day_entries = df_timesheets[df_timesheets['date'].dt.date == current_date]
            has_entries = not day_entries.empty
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

def generate_calendar_events(df_timesheets):
    """Generate calendar events from timesheet data"""
    if df_timesheets.empty:
        return []
    
    events = []
    for _, row in df_timesheets.iterrows():
        start_time = row['date']
        end_time = start_time + timedelta(hours=row['duration_hours'])
        
        events.append({
            'id': str(row.name),
            'title': f"{row['client']} - {row['description']}",
            'start': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'end': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'backgroundColor': get_client_color(row['client']),
            'borderColor': get_client_color(row['client']),
            'extendedProps': {
                'client': row['client'],
                'description': row['description'],
                'duration': format_duration(row['duration']),
                'duration_hours': row['duration_hours']
            }
        })
    
    return events

def get_client_color(client_name):
    """Generate a consistent color for a client based on their name"""
    # Simple hash function to generate a color
    hash_value = hash(client_name) % 360
    return f"hsl({hash_value}, 70%, 60%)"

# Initialize session state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'password' not in st.session_state:
    st.session_state.password = ""
if 'current_view' not in st.session_state:
    st.session_state.current_view = "Dashboard"
if 'selected_client' not in st.session_state:
    st.session_state.selected_client = None
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

# Sidebar for authentication
with st.sidebar:
    st.image("https://via.placeholder.com/150x80?text=TSheets+CRM", width=200)
    st.title("TSheets CRM Manager")
    
    if not st.session_state.authenticated:
        st.subheader("Authentication")
        auth_method = st.radio("Authentication Method", ["API Key", "Username/Password"])
        
        if auth_method == "API Key":
            api_key = st.text_input("API Key", type="password")
            if st.button("Login with API Key"):
                # In a real app, validate the API key
                if api_key:  # Simplified validation
                    st.session_state.api_key = api_key
                    st.session_state.authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid API Key")
        else:
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            if st.button("Login"):
                # In a real app, validate the credentials
                if username and password:  # Simplified validation
                    st.session_state.username = username
                    st.session_state.password = password
                    st.session_state.authenticated = True
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
    else:
        # Show user info
        st.success("Authenticated")
        if st.session_state.username:
            st.write(f"Logged in as: **{st.session_state.username}**")
        else:
            st.write("Logged in with API Key")
        
        # Navigation
        st.subheader("Navigation")
        selected = option_menu(
            menu_title=None,
            options=["Dashboard", "Timesheets", "Clients", "Calendar", "Reports", "Settings"],
            icons=["speedometer2", "clock", "people", "calendar3", "file-earmark-bar-graph", "gear"],
            menu_icon="cast",
            default_index=0,
        )
        st.session_state.current_view = selected
        
        # Date range selector
        st.subheader("Date Range")
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
        
        st.session_state.selected_date_range = selected_date_range
        
        # Logout button
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.api_key = ""
            st.session_state.username = ""
            st.session_state.password = ""
            st.experimental_rerun()

# Main content
if not st.session_state.authenticated:
    st.title("Welcome to TSheets CRM Manager")
    st.write("Please login using the sidebar to access the application.")
    
    # Show demo images
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://via.placeholder.com/600x400?text=Dashboard+Demo", use_column_width=True)
        st.caption("Dashboard View")
    with col2:
        st.image("https://via.placeholder.com/600x400?text=Reports+Demo", use_column_width=True)
        st.caption("Reports View")
else:
    # Get date range
    if st.session_state.selected_date_range == "Custom":
        start_date = st.session_state.custom_start_date
        end_date = st.session_state.custom_end_date
    else:
        date_range_presets = get_date_range_presets()
        start_date, end_date = date_range_presets[st.session_state.selected_date_range]
    
    # Load mock data
    # In a real app, this would be fetched from the TSheets API
    
    # Generate mock clients
    clients = [
        {
            "id": 1,
            "name": "Acme Corp",
            "contact": "John Doe",
            "email": "john.doe@acme.com",
            "phone": "555-123-4567",
            "address": "123 Main St, Anytown, USA",
            "notes": "Key client for software development projects",
            "active": True,
            "created_at": "2022-01-15"
        },
        {
            "id": 2,
            "name": "Globex Inc",
            "contact": "Jane Smith",
            "email": "jane.smith@globex.com",
            "phone": "555-987-6543",
            "address": "456 Oak Ave, Somewhere, USA",
            "notes": "Regular client for web design services",
            "active": True,
            "created_at": "2022-02-20"
        },
        {
            "id": 3,
            "name": "Initech LLC",
            "contact": "Michael Bolton",
            "email": "michael.bolton@initech.com",
            "phone": "555-555-5555",
            "address": "789 Pine St, Elsewhere, USA",
            "notes": "New client for IT consulting",
            "active": True,
            "created_at": "2022-03-10"
        },
        {
            "id": 4,
            "name": "Umbrella Corp",
            "contact": "Alice Johnson",
            "email": "alice.johnson@umbrella.com",
            "phone": "555-222-3333",
            "address": "321 Elm St, Nowhere, USA",
            "notes": "Pharmaceutical research client",
            "active": False,
            "created_at": "2022-01-05"
        },
        {
            "id": 5,
            "name": "Stark Industries",
            "contact": "Tony Stark",
            "email": "tony.stark@stark.com",
            "phone": "555-444-1111",
            "address": "1 Stark Tower, New York, USA",
            "notes": "High-tech R&D projects",
            "active": True,
            "created_at": "2022-04-15"
        }
    ]
    
    # Generate mock timesheet entries
    np.random.seed(42)  # For reproducible results
    
    # Generate dates within the range
    date_range = pd.date_range(start=start_date - timedelta(days=30), end=end_date + timedelta(days=30))
    
    # Create timesheet entries
    timesheet_entries = []
    for i in range(100):  # Generate 100 entries
        entry_date = np.random.choice(date_range)
        client = np.random.choice(clients)
        
        # Generate a duration between 0.5 and 8 hours (in seconds)
        duration_hours = np.random.uniform(0.5, 8)
        duration = int(duration_hours * 3600)
        
        timesheet_entries.append({
            "id": i + 1,
            "date": entry_date,
            "client": client["name"],
            "description": np.random.choice([
                "Software Development",
                "Web Design",
                "Meeting",
                "Documentation",
                "Testing",
                "Maintenance",
                "Support",
                "Planning",
                "Research",
                "Training"
            ]),
            "duration": duration,
            "duration_hours": duration_hours,
            "billable": np.random.choice([True, False], p=[0.8, 0.2]),
            "billed": np.random.choice([True, False], p=[0.7, 0.3]) if np.random.choice([True, False], p=[0.8, 0.2]) else False,
            "notes": np.random.choice(["", "Follow-up required", "Client was satisfied", "Need to discuss next steps"], p=[0.7, 0.1, 0.1, 0.1])
        })
    
    # Convert to DataFrame
    df_timesheets = pd.DataFrame(timesheet_entries)
    
    # Filter by date range
    df_timesheets_filtered = df_timesheets[
        (df_timesheets['date'].dt.date >= start_date) & 
        (df_timesheets['date'].dt.date <= end_date)
    ]
    
    # Sort by date (most recent first)
    df_timesheets_filtered = df_timesheets_filtered.sort_values(by='date', ascending=False)
    
    # Dashboard View
    if st.session_state.current_view == "Dashboard":
        st.title("Dashboard")
        st.write(f"Showing data from **{start_date}** to **{end_date}**")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_hours = df_timesheets_filtered['duration_hours'].sum()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_hours:.2f}</div>
                <div class="metric-label">Total Hours</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            billable_hours = df_timesheets_filtered[df_timesheets_filtered['billable']]['duration_hours'].sum()
            billable_percentage = (billable_hours / total_hours * 100) if total_hours > 0 else 0
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{billable_hours:.2f} ({billable_percentage:.1f}%)</div>
                <div class="metric-label">Billable Hours</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            unique_clients = df_timesheets_filtered['client'].nunique()
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{unique_clients}</div>
                <div class="metric-label">Active Clients</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_daily_hours = total_hours / (len(pd.date_range(start=start_date, end=end_date)) or 1)
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_daily_hours:.2f}</div>
                <div class="metric-label">Avg. Daily Hours</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Charts
        st.subheader("Time Distribution")
        
        tab1, tab2, tab3 = st.tabs(["By Client", "By Activity", "By Day"])
        
        with tab1:
            # Hours by client
            hours_by_client = df_timesheets_filtered.groupby('client')['duration_hours'].sum().reset_index()
            hours_by_client = hours_by_client.sort_values('duration_hours', ascending=False)
            
            fig = px.bar(
                hours_by_client,
                x='client',
                y='duration_hours',
                title='Hours by Client',
                labels={'client': 'Client', 'duration_hours': 'Hours'},
                color='duration_hours',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Hours by activity
            hours_by_activity = df_timesheets_filtered.groupby('description')['duration_hours'].sum().reset_index()
            hours_by_activity = hours_by_activity.sort_values('duration_hours', ascending=False)
            
            fig = px.pie(
                hours_by_activity,
                values='duration_hours',
                names='description',
                title='Hours by Activity',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Hours by day
            hours_by_day = df_timesheets_filtered.groupby(df_timesheets_filtered['date'].dt.date)['duration_hours'].sum().reset_index()
            hours_by_day = hours_by_day.sort_values('date')
            
            fig = px.line(
                hours_by_day,
                x='date',
                y='duration_hours',
                title='Hours by Day',
                labels={'date': 'Date', 'duration_hours': 'Hours'},
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent activity
        st.subheader("Recent Activity")
        recent_entries = df_timesheets_filtered.head(5)
        
        for _, entry in recent_entries.iterrows():
            st.markdown(f"""
            <div class="timesheet-entry">
                <div class="timesheet-date">{entry['date'].strftime('%Y-%m-%d')}</div>
                <div class="timesheet-client">{entry['client']}</div>
                <div class="timesheet-description">{entry['description']}</div>
                <div class="timesheet-duration">{format_duration_hours(entry['duration'])} hours</div>
            </div>
            """, unsafe_allow_html=True)
        
        if len(recent_entries) == 0:
            st.info("No recent activity in the selected date range.")
        
        # Quick links
        st.subheader("Quick Links")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Add Timesheet Entry"):
                st.session_state.current_view = "Timesheets"
                st.experimental_rerun()
        
        with col2:
            if st.button("View All Clients"):
                st.session_state.current_view = "Clients"
                st.experimental_rerun()
        
        with col3:
            if st.button("Generate Reports"):
                st.session_state.current_view = "Reports"
                st.experimental_rerun()
    
    # Timesheets View
    elif st.session_state.current_view == "Timesheets":
        st.title("Timesheets")
        st.write(f"Showing data from **{start_date}** to **{end_date}**")
        
        # Add new timesheet entry
        with st.expander("Add New Timesheet Entry", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                entry_date = st.date_input("Date", value=datetime.now().date())
                entry_client = st.selectbox("Client", options=[client["name"] for client in clients])
                entry_billable = st.checkbox("Billable", value=True)
            
            with col2:
                entry_description = st.selectbox("Activity", options=[
                    "Software Development",
                    "Web Design",
                    "Meeting",
                    "Documentation",
                    "Testing",
                    "Maintenance",
                    "Support",
                    "Planning",
                    "Research",
                    "Training"
                ])
                entry_duration = st.number_input("Duration (hours)", min_value=0.25, max_value=24.0, value=1.0, step=0.25)
                entry_billed = st.checkbox("Billed", value=False)
            
            entry_notes = st.text_area("Notes", height=100)
            
            if st.button("Save Timesheet Entry"):
                st.success("Timesheet entry saved successfully!")
                # In a real app, this would save to the TSheets API
                st.experimental_rerun()
        
        # Filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_client = st.multiselect(
                "Filter by Client",
                options=sorted(df_timesheets_filtered['client'].unique()),
                default=[]
            )
        
        with col2:
            filter_activity = st.multiselect(
                "Filter by Activity",
                options=sorted(df_timesheets_filtered['description'].unique()),
                default=[]
            )
        
        with col3:
            filter_billable = st.radio("Billable Status", options=["All", "Billable Only", "Non-Billable Only"])
        
        # Apply filters
        filtered_df = df_timesheets_filtered.copy()
        
        if filter_client:
            filtered_df = filtered_df[filtered_df['client'].isin(filter_client)]
        
        if filter_activity:
            filtered_df = filtered_df[filtered_df['description'].isin(filter_activity)]
        
        if filter_billable == "Billable Only":
            filtered_df = filtered_df[filtered_df['billable']]
        elif filter_billable == "Non-Billable Only":
            filtered_df = filtered_df[~filtered_df['billable']]
        
        # Display timesheet entries
        if not filtered_df.empty:
            # Summary metrics
            total_filtered_hours = filtered_df['duration_hours'].sum()
            billable_filtered_hours = filtered_df[filtered_df['billable']]['duration_hours'].sum()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Entries", len(filtered_df))
            
            with col2:
                st.metric("Total Hours", f"{total_filtered_hours:.2f}")
            
            with col3:
                st.metric("Billable Hours", f"{billable_filtered_hours:.2f} ({billable_filtered_hours/total_filtered_hours*100:.1f}%)")
            
            # Download links
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(get_download_link(filtered_df, "timesheet_entries.csv", "Download as CSV"), unsafe_allow_html=True)
            
            with col2:
                st.markdown(get_excel_download_link(filtered_df, "timesheet_entries.xlsx", "Download as Excel"), unsafe_allow_html=True)
            
            # Display as table
            st.dataframe(
                filtered_df[['date', 'client', 'description', 'duration_hours', 'billable', 'billed', 'notes']].rename(columns={
                    'date': 'Date',
                    'client': 'Client',
                    'description': 'Activity',
                    'duration_hours': 'Hours',
                    'billable': 'Billable',
                    'billed': 'Billed',
                    'notes': 'Notes'
                }),
                use_container_width=True
            )
        else:
            st.info("No timesheet entries found with the selected filters.")
    
    # Clients View
    elif st.session_state.current_view == "Clients":
        st.title("Clients")
        
        # Add new client
        with st.expander("Add New Client", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                new_client_name = st.text_input("Client Name")
                new_client_contact = st.text_input("Contact Person")
                new_client_email = st.text_input("Email")
            
            with col2:
                new_client_phone = st.text_input("Phone")
                new_client_address = st.text_area("Address", height=100)
            
            new_client_notes = st.text_area("Notes", height=100)
            new_client_active = st.checkbox("Active", value=True)
            
            if st.button("Save Client"):
                if new_client_name and new_client_email:
                    st.success(f"Client '{new_client_name}' saved successfully!")
                    # In a real app, this would save to the TSheets API
                else:
                    st.error("Client name and email are required.")
        
        # Search clients
        search_query = st.text_input("Search Clients", placeholder="Search by name, contact, or email")
        filtered_clients = search_clients(search_query, clients)
        
        # Display clients
        if filtered_clients:
            # Client cards
            for i in range(0, len(filtered_clients), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(filtered_clients):
                        client = filtered_clients[i + j]
                        with cols[j]:
                            st.markdown(f"""
                            <div class="client-card">
                                <div class="client-name">{client['name']}</div>
                                <div class="client-info"><strong>Contact:</strong> {client['contact']}</div>
                                <div class="client-info"><strong>Email:</strong> {client['email']}</div>
                                <div class="client-info"><strong>Phone:</strong> {client['phone']}</div>
                                <div class="client-info"><strong>Status:</strong> {'Active' if client['active'] else 'Inactive'}</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if st.button(f"View Details #{client['id']}"):
                                st.session_state.selected_client = client
                                st.experimental_rerun()
        else:
            st.info("No clients found matching your search criteria.")
        
        # Client details
        if st.session_state.selected_client:
            client = st.session_state.selected_client
            
            st.subheader(f"Client Details: {client['name']}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Contact Person:** {client['contact']}")
                st.write(f"**Email:** {client['email']}")
                st.write(f"**Phone:** {client['phone']}")
            
            with col2:
                st.write(f"**Address:** {client['address']}")
                st.write(f"**Status:** {'Active' if client['active'] else 'Inactive'}")
                st.write(f"**Created:** {client['created_at']}")
            
            st.write(f"**Notes:** {client['notes']}")
            
            # Client timesheet entries
            st.subheader("Timesheet Entries")
            
            client_entries = df_timesheets_filtered[df_timesheets_filtered['client'] == client['name']]
            
            if not client_entries.empty:
                total_client_hours = client_entries['duration_hours'].sum()
                billable_client_hours = client_entries[client_entries['billable']]['duration_hours'].sum()
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Entries", len(client_entries))
                
                with col2:
                    st.metric("Total Hours", f"{total_client_hours:.2f}")
                
                with col3:
                    st.metric("Billable Hours", f"{billable_client_hours:.2f} ({billable_client_hours/total_client_hours*100:.1f}%)")
                
                st.dataframe(
                    client_entries[['date', 'description', 'duration_hours', 'billable', 'billed', 'notes']].rename(columns={
                        'date': 'Date',
                        'description': 'Activity',
                        'duration_hours': 'Hours',
                        'billable': 'Billable',
                        'billed': 'Billed',
                        'notes': 'Notes'
                    }),
                    use_container_width=True
                )
            else:
                st.info("No timesheet entries found for this client in the selected date range.")
            
            if st.button("Back to Clients List"):
                st.session_state.selected_client = None
                st.experimental_rerun()
    
    # Calendar View
    elif st.session_state.current_view == "Calendar":
        st.title("Calendar")
        
        # Calendar view options
        col1, col2 = st.columns([1, 3])
        
        with col1:
            calendar_view_option = st.radio("Calendar View", ["Month", "Week", "Day", "List"])
            st.session_state.calendar_view = calendar_view_option.lower()
            
            # Month/Year selector for month view
            if calendar_view_option == "Month":
                current_date = st.session_state.calendar_date
                current_month = current_date.month
                current_year = current_date.year
                
                selected_month = st.selectbox("Month", options=list(range(1, 13)), index=current_month-1, format_func=lambda x: calendar.month_name[x])
                selected_year = st.selectbox("Year", options=list(range(current_year-5, current_year+6)), index=5)
                
                if selected_month != current_month or selected_year != current_year:
                    st.session_state.calendar_date = date(selected_year, selected_month, 1)
        
        with col2:
            # Calendar component
            calendar_events = generate_calendar_events(df_timesheets)
            
            calendar_options = {
                "headerToolbar": {
                    "left": "prev,next today",
                    "center": "title",
                    "right": "dayGridMonth,timeGridWeek,timeGridDay,listMonth"
                },
                "initialDate": st.session_state.calendar_date.isoformat(),
                "initialView": st.session_state.calendar_view + "GridMonth" if st.session_state.calendar_view != "list" else "listMonth",
                "selectable": True,
                "editable": False,
                "dayMaxEvents": True,
                "weekNumbers": True,
                "navLinks": True,
                "businessHours": {
                    "daysOfWeek": [1, 2, 3, 4, 5],
                    "startTime": "09:00",
                    "endTime": "17:00"
                },
                "eventTimeFormat": {
                    "hour": "2-digit",
                    "minute": "2-digit",
                    "meridiem": False
                }
            }
            
            calendar_result = calendar(events=calendar_events, options=calendar_options, key="calendar")
            
            if calendar_result.get("eventClick"):
                event_id = calendar_result.get("eventClick")["event"]["id"]
                st.write(f"Clicked on event {event_id}")
                # In a real app, show event details or allow editing
        
        # Alternative calendar view (custom grid)
        if calendar_view_option == "Month":
            st.subheader("Monthly Hours Summary")
            
            # Get calendar data
            current_date = st.session_state.calendar_date
            calendar_data = get_month_calendar_data(current_date.year, current_date.month, df_timesheets)
            
            # Display calendar grid
            st.markdown("<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 4px;'>", unsafe_allow_html=True)
            
            # Day headers
            for day in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]:
                st.markdown(f"<div class='calendar-day-header'>{day}</div>", unsafe_allow_html=True)
            
            # Calendar days
            for date_info in calendar_data:
                day_class = "calendar-day"
                if date_info["current_month"]:
                    day_class += " calendar-day-current"
                if date_info["has_entries"]:
                    day_class += " calendar-day-has-entries"
                
                hours_text = f"{date_info['hours']:.1f}h" if date_info["hours"] > 0 else ""
                
                st.markdown(
                    f"<div class='{day_class}'>{date_info['day']}<br/>{hours_text}</div>",
                    unsafe_allow_html=True
                )
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Reports View
    elif st.session_state.current_view == "Reports":
        st.title("Reports")
        
        # Report types
        report_type = st.selectbox(
            "Report Type",
            options=["Time Summary", "Client Summary", "Activity Summary", "Billable Hours", "Unbilled Time"]
        )
        
        # Time Summary Report
        if report_type == "Time Summary":
            st.subheader("Time Summary Report")
            st.write(f"Period: **{start_date}** to **{end_date}**")
            
            # Summary metrics
            total_hours = df_timesheets_filtered['duration_hours'].sum()
            billable_hours = df_timesheets_filtered[df_timesheets_filtered['billable']]['duration_hours'].sum()
            billed_hours = df_timesheets_filtered[df_timesheets_filtered['billed']]['duration_hours'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Hours", f"{total_hours:.2f}")
            
            with col2:
                st.metric("Billable Hours", f"{billable_hours:.2f} ({billable_hours/total_hours*100:.1f}%)")
            
            with col3:
                st.metric("Billed Hours", f"{billed_hours:.2f} ({billed_hours/total_hours*100:.1f}%)")
            
            with col4:
                st.metric("Unbilled Hours", f"{billable_hours - billed_hours:.2f}")
            
            # Time by day chart
            st.subheader("Time by Day")
            
            hours_by_day = df_timesheets_filtered.groupby(df_timesheets_filtered['date'].dt.date)['duration_hours'].sum().reset_index()
            hours_by_day = hours_by_day.sort_values('date')
            
            fig = px.bar(
                hours_by_day,
                x='date',
                y='duration_hours',
                labels={'date': 'Date', 'duration_hours': 'Hours'},
                color_discrete_sequence=['#4e89ae']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Time by weekday chart
            st.subheader("Time by Weekday")
            
            df_timesheets_filtered['weekday'] = df_timesheets_filtered['date'].dt.day_name()
            hours_by_weekday = df_timesheets_filtered.groupby('weekday')['duration_hours'].sum().reset_index()
            
            # Ensure correct order of weekdays
            weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            hours_by_weekday['weekday'] = pd.Categorical(hours_by_weekday['weekday'], categories=weekday_order, ordered=True)
            hours_by_weekday = hours_by_weekday.sort_values('weekday')
            
            fig = px.bar(
                hours_by_weekday,
                x='weekday',
                y='duration_hours',
                labels={'weekday': 'Weekday', 'duration_hours': 'Hours'},
                color_discrete_sequence=['#4e89ae']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Download report
            st.markdown(get_excel_download_link(df_timesheets_filtered, "time_summary_report.xlsx", "Download Full Report"), unsafe_allow_html=True)
        
        # Client Summary Report
        elif report_type == "Client Summary":
            st.subheader("Client Summary Report")
            st.write(f"Period: **{start_date}** to **{end_date}**")
            
            # Hours by client
            hours_by_client = df_timesheets_filtered.groupby('client')['duration_hours'].sum().reset_index()
            hours_by_client = hours_by_client.sort_values('duration_hours', ascending=False)
            
            # Client metrics
            total_clients = hours_by_client.shape[0]
            top_client = hours_by_client.iloc[0]['client'] if not hours_by_client.empty else "N/A"
            top_client_hours = hours_by_client.iloc[0]['duration_hours'] if not hours_by_client.empty else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Clients", total_clients)
            
            with col2:
                st.metric("Top Client", top_client)
            
            with col3:
                st.metric("Top Client Hours", f"{top_client_hours:.2f}")
            
            # Hours by client chart
            st.subheader("Hours by Client")
            
            fig = px.bar(
                hours_by_client,
                x='client',
                y='duration_hours',
                labels={'client': 'Client', 'duration_hours': 'Hours'},
                color='duration_hours',
                color_continuous_scale=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Client details table
            st.subheader("Client Details")
            
            client_details = []
            for client_name in hours_by_client['client']:
                client_df = df_timesheets_filtered[df_timesheets_filtered['client'] == client_name]
                total_hours = client_df['duration_hours'].sum()
                billable_hours = client_df[client_df['billable']]['duration_hours'].sum()
                billed_hours = client_df[client_df['billed']]['duration_hours'].sum()
                
                client_details.append({
                    'Client': client_name,
                    'Total Hours': f"{total_hours:.2f}",
                    'Billable Hours': f"{billable_hours:.2f}",
                    'Billed Hours': f"{billed_hours:.2f}",
                    'Unbilled Hours': f"{billable_hours - billed_hours:.2f}",
                    'Billable %': f"{billable_hours/total_hours*100:.1f}%" if total_hours > 0 else "0%"
                })
            
            st.dataframe(pd.DataFrame(client_details), use_container_width=True)
            
            # Download report
            st.markdown(get_excel_download_link(pd.DataFrame(client_details), "client_summary_report.xlsx", "Download Client Summary"), unsafe_allow_html=True)
        
        # Activity Summary Report
        elif report_type == "Activity Summary":
            st.subheader("Activity Summary Report")
            st.write(f"Period: **{start_date}** to **{end_date}**")
            
            # Hours by activity
            hours_by_activity = df_timesheets_filtered.groupby('description')['duration_hours'].sum().reset_index()
            hours_by_activity = hours_by_activity.sort_values('duration_hours', ascending=False)
            
            # Activity metrics
            total_activities = hours_by_activity.shape[0]
            top_activity = hours_by_activity.iloc[0]['description'] if not hours_by_activity.empty else "N/A"
            top_activity_hours = hours_by_activity.iloc[0]['duration_hours'] if not hours_by_activity.empty else 0
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Activities", total_activities)
            
            with col2:
                st.metric("Top Activity", top_activity)
            
            with col3:
                st.metric("Top Activity Hours", f"{top_activity_hours:.2f}")
            
            # Hours by activity chart
            st.subheader("Hours by Activity")
            
            fig = px.pie(
                hours_by_activity,
                values='duration_hours',
                names='description',
                color_discrete_sequence=px.colors.sequential.Blues
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Activity details table
            st.subheader("Activity Details")
            
            activity_details = []
            for activity in hours_by_activity['description']:
                activity_df = df_timesheets_filtered[df_timesheets_filtered['description'] == activity]
                total_hours = activity_df['duration_hours'].sum()
                billable_hours = activity_df[activity_df['billable']]['duration_hours'].sum()
                
                activity_details.append({
                    'Activity': activity,
                    'Total Hours': f"{total_hours:.2f}",
                    'Billable Hours': f"{billable_hours:.2f}",
                    'Billable %': f"{billable_hours/total_hours*100:.1f}%" if total_hours > 0 else "0%",
                    'Clients': activity_df['client'].nunique()
                })
            
            st.dataframe(pd.DataFrame(activity_details), use_container_width=True)
            
            # Download report
            st.markdown(get_excel_download_link(pd.DataFrame(activity_details), "activity_summary_report.xlsx", "Download Activity Summary"), unsafe_allow_html=True)
        
        # Billable Hours Report
        elif report_type == "Billable Hours":
            st.subheader("Billable Hours Report")
            st.write(f"Period: **{start_date}** to **{end_date}**")
            
            # Filter for billable entries
            billable_df = df_timesheets_filtered[df_timesheets_filtered['billable']]
            
            # Billable metrics
            total_hours = df_timesheets_filtered['duration_hours'].sum()
            billable_hours = billable_df['duration_hours'].sum()
            billed_hours = billable_df[billable_df['billed']]['duration_hours'].sum()
            unbilled_hours = billable_hours - billed_hours
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Hours", f"{total_hours:.2f}")
            
            with col2:
                st.metric("Billable Hours", f"{billable_hours:.2f} ({billable_hours/total_hours*100:.1f}%)")
            
            with col3:
                st.metric("Billed Hours", f"{billed_hours:.2f} ({billed_hours/billable_hours*100:.1f}%)")
            
            with col4:
                st.metric("Unbilled Hours", f"{unbilled_hours:.2f}")
            
            # Billable vs. Non-billable chart
            st.subheader("Billable vs. Non-billable Hours")
            
            billable_data = [
                {'Category': 'Billable', 'Hours': billable_hours},
                {'Category': 'Non-billable', 'Hours': total_hours - billable_hours}
            ]
            
            fig = px.pie(
                billable_data,
                values='Hours',
                names='Category',
                color='Category',
                color_discrete_map={'Billable': '#4e89ae', 'Non-billable': '#e9ecef'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Billable hours by client
            st.subheader("Billable Hours by Client")
            
            billable_by_client = billable_df.groupby('client')['duration_hours'].sum().reset_index()
            billable_by_client = billable_by_client.sort_values('duration_hours', ascending=False)
            
            fig = px.bar(
                billable_by_client,
                x='client',
                y='duration_hours',
                labels={'client': 'Client', 'duration_hours': 'Billable Hours'},
                color_discrete_sequence=['#4e89ae']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Billable entries table
            st.subheader("Billable Entries")
            
            st.dataframe(
                billable_df[['date', 'client', 'description', 'duration_hours', 'billed']].rename(columns={
                    'date': 'Date',
                    'client': 'Client',
                    'description': 'Activity',
                    'duration_hours': 'Hours',
                    'billed': 'Billed'
                }),
                use_container_width=True
            )
            
            # Download report
            st.markdown(get_excel_download_link(billable_df, "billable_hours_report.xlsx", "Download Billable Hours Report"), unsafe_allow_html=True)
        
        # Unbilled Time Report
        elif report_type == "Unbilled Time":
            st.subheader("Unbilled Time Report")
            st.write(f"Period: **{start_date}** to **{end_date}**")
            
            # Filter for unbilled entries
            unbilled_df = df_timesheets_filtered[(df_timesheets_filtered['billable']) & (~df_timesheets_filtered['billed'])]
            
            # Unbilled metrics
            total_billable_hours = df_timesheets_filtered[df_timesheets_filtered['billable']]['duration_hours'].sum()
            unbilled_hours = unbilled_df['duration_hours'].sum()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Billable Hours", f"{total_billable_hours:.2f}")
            
            with col2:
                st.metric("Unbilled Hours", f"{unbilled_hours:.2f}")
            
            with col3:
                st.metric("Unbilled %", f"{unbilled_hours/total_billable_hours*100:.1f}%" if total_billable_hours > 0 else "0%")
            
            # Unbilled hours by client
            st.subheader("Unbilled Hours by Client")
            
            unbilled_by_client = unbilled_df.groupby('client')['duration_hours'].sum().reset_index()
            unbilled_by_client = unbilled_by_client.sort_values('duration_hours', ascending=False)
            
            fig = px.bar(
                unbilled_by_client,
                x='client',
                y='duration_hours',
                labels={'client': 'Client', 'duration_hours': 'Unbilled Hours'},
                color_discrete_sequence=['#dc3545']
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
            
            # Unbilled entries table
            st.subheader("Unbilled Entries")
            
            st.dataframe(
                unbilled_df[['date', 'client', 'description', 'duration_hours']].rename(columns={
                    'date': 'Date',
                    'client': 'Client',
                    'description': 'Activity',
                    'duration_hours': 'Hours'
                }),
                use_container_width=True
            )
            
            # Download report
            st.markdown(get_excel_download_link(unbilled_df, "unbilled_time_report.xlsx", "Download Unbilled Time Report"), unsafe_allow_html=True)
    
    # Settings View
    elif st.session_state.current_view == "Settings":
        st.title("Settings")
        
        # Settings tabs
        tab1, tab2, tab3 = st.tabs(["General", "Appearance", "Data"])
        
        with tab1:
            st.subheader("General Settings")
            
            # Time tracking settings
            st.write("**Time Tracking**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Round time entries to nearest", value=True)
                st.selectbox("Round to", options=["5 minutes", "10 minutes", "15 minutes", "30 minutes", "1 hour"], index=2)
            
            with col2:
                st.checkbox("Allow overlapping time entries", value=False)
                st.checkbox("Auto-fill previous activity description", value=True)
            
            # Notification settings
            st.write("**Notifications**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.checkbox("Email notifications", value=True)
                st.checkbox("Daily summary", value=False)
            
            with col2:
                st.checkbox("Weekly summary", value=True)
                st.checkbox("Reminder for unbilled time", value=True)
            
            # Save settings
            if st.button("Save General Settings"):
                st.success("Settings saved successfully!")
        
        with tab2:
            st.subheader("Appearance Settings")
            
            # Theme settings
            st.write("**Theme**")
            
            theme = st.radio("Select Theme", options=["Light", "Dark", "System Default"], index=0)
            accent_color = st.color_picker("Accent Color", "#4e89ae")
            
            # Display settings
            st.write("**Display**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.selectbox("Default View", options=["Dashboard", "Timesheets", "Clients", "Calendar", "Reports"], index=0)
                st.checkbox("Show recent activity on dashboard", value=True)
            
            with col2:
                st.selectbox("Date Format", options=["MM/DD/YYYY", "DD/MM/YYYY", "YYYY-MM-DD"], index=2)
                st.checkbox("Use 24-hour time format", value=True)
            
            # Save settings
            if st.button("Save Appearance Settings"):
                st.success("Appearance settings saved successfully!")
        
        with tab3:
            st.subheader("Data Settings")
            
            # Data import/export
            st.write("**Data Import/Export**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.file_uploader("Import Data", type=["csv", "xlsx"])
                st.selectbox("Import Type", options=["Timesheets", "Clients", "All Data"])
            
            with col2:
                st.selectbox("Export Format", options=["CSV", "Excel", "JSON"])
                if st.button("Export All Data"):
                    st.success("Data exported successfully!")
            
            # Data cleanup
            st.write("**Data Cleanup**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.number_input("Delete entries older than", min_value=1, max_value=120, value=24, step=1)
                st.selectbox("Time Unit", options=["Days", "Weeks", "Months"], index=2)
            
            with col2:
                st.checkbox("Archive instead of delete", value=True)
                if st.button("Clean Up Data"):
                    st.warning("This action cannot be undone. Are you sure?")
                    if st.button("Yes, proceed with cleanup"):
                        st.success("Data cleanup completed successfully!")

# Run the app
if __name__ == "__main__":
    # This is handled by Streamlit
    pass
