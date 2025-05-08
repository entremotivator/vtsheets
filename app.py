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
import calendar
import re
import altair as alt
from PIL import Image
from io import BytesIO
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.colors import LinearSegmentedColormap
import seaborn as sns
import os
import logging
from typing import Dict, List, Tuple, Optional, Any, Union
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('tsheets_crm')

# Set page configuration
st.set_page_config(
    page_title="TSheets CRM Manager Pro",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling (keeping your existing CSS)
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
        margin-bottom: 25px;
    }
    .activity-item:before {
        content: '';
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
    
    /* Calendar Styles */
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
    }
    .calendar-day:hover {
        background-color: #e9ecef;
        transform: scale(1.05);
    }
    .calendar-day.today {
        background-color: #d4edda;
        color: #155724;
        font-weight: bold;
    }
    .calendar-day.has-entries {
        background-color: #d1ecf1;
        color: #0c5460;
    }
    .calendar-day.selected {
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .calendar-day.other-month {
        color: #aaa;
        background-color: #f8f9fa;
    }
    
    /* Day View */
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
    
    /* Heat Map Calendar */
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
    
    /* Analytics Dashboard */
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
    
    /* Productivity Score */
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
    
    /* Progress Bar */
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
    
    /* Notification Badge */
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
    
    /* Search Bar */
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
    
    /* Footer */
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
    
    /* API Debug Panel */
    .debug-panel {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-top: 20px;
        border-left: 5px solid #17a2b8;
    }
    .debug-header {
        font-weight: bold;
        color: #17a2b8;
        margin-bottom: 10px;
    }
    .debug-content {
        font-family: monospace;
        white-space: pre-wrap;
        font-size: 0.9rem;
        background-color: #f1f1f1;
        padding: 10px;
        border-radius: 5px;
        max-height: 300px;
        overflow-y: auto;
    }
    
    /* API Connection Status */
    .connection-status {
        display: inline-block;
        padding: 5px 10px;
        border-radius: 15px;
        font-size: 0.85rem;
        font-weight: bold;
        margin-left: 10px;
    }
    .connection-success {
        background-color: #d4edda;
        color: #155724;
    }
    .connection-error {
        background-color: #f8d7da;
        color: #721c24;
    }
    .connection-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    
    /* Responsive Adjustments */
    @media (max-width: 768px) {
        .client-stats {
            flex-direction: column;
        }
        .client-stat {
            margin: 5px 0;
        }
        .calendar-weekday, .calendar-day {
            padding: 5px;
            font-size: 0.9rem;
        }
    }
    
    /* New Features */
    .feature-badge {
        display: inline-block;
        background-color: #4CAF50;
        color: white;
        border-radius: 15px;
        padding: 3px 8px;
        font-size: 0.7rem;
        font-weight: bold;
        margin-left: 5px;
        vertical-align: middle;
    }
    
    /* Data Sync Indicator */
    .sync-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.9rem;
        color: #666;
    }
    .sync-spinner {
        display: inline-block;
        width: 12px;
        height: 12px;
        border: 2px solid rgba(0, 0, 0, 0.1);
        border-top-color: #4CAF50;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
    
    /* API Rate Limit Indicator */
    .rate-limit-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        font-size: 0.9rem;
        color: #666;
        margin-top: 5px;
    }
    .rate-limit-bar {
        flex-grow: 1;
        height: 6px;
        background-color: #f8f9fa;
        border-radius: 3px;
        overflow: hidden;
    }
    .rate-limit-fill {
        height: 100%;
        background-color: #4CAF50;
        border-radius: 3px;
    }
    .rate-limit-warning .rate-limit-fill {
        background-color: #ffc107;
    }
    .rate-limit-critical .rate-limit-fill {
        background-color: #dc3545;
    }
    
    /* New Feature: Export Options Panel */
    .export-options-panel {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-top: 15px;
        border: 1px solid #e9ecef;
    }
    .export-option {
        display: flex;
        align-items: center;
        padding: 10px;
        border-radius: 5px;
        transition: background-color 0.3s ease;
        cursor: pointer;
    }
    .export-option:hover {
        background-color: #e9ecef;
    }
    .export-icon {
        margin-right: 10px;
        color: #4CAF50;
    }
    
    /* New Feature: Integration Status */
    .integration-status {
        display: flex;
        align-items: center;
        margin-bottom: 10px;
        padding: 10px;
        border-radius: 5px;
        background-color: #f8f9fa;
    }
    .integration-icon {
        margin-right: 10px;
        font-size: 1.5rem;
    }
    .integration-info {
        flex-grow: 1;
    }
    .integration-name {
        font-weight: bold;
    }
    .integration-description {
        font-size: 0.9rem;
        color: #666;
    }
    .integration-connected {
        color: #4CAF50;
    }
    .integration-disconnected {
        color: #dc3545;
    }
    
    /* New Feature: Data Quality Indicator */
    .data-quality-indicator {
        display: flex;
        align-items: center;
        gap: 5px;
        margin-top: 5px;
    }
    .quality-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
    }
    .quality-high {
        background-color: #4CAF50;
    }
    .quality-medium {
        background-color: #FFC107;
    }
    .quality-low {
        background-color: #F44336;
    }
    .quality-text {
        font-size: 0.8rem;
        color: #666;
    }
    
    /* New Feature: Bulk Actions */
    .bulk-actions {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .bulk-action-count {
        font-weight: bold;
        margin-right: 10px;
    }
    
    /* New Feature: Tooltip */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .tooltip .tooltip-text {
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
    .tooltip:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }
    
    /* New Feature: Drag and Drop Area */
    .drop-area {
        border: 2px dashed #ddd;
        border-radius: 10px;
        padding: 30px;
        text-align: center;
        transition: border-color 0.3s ease;
        margin-bottom: 20px;
    }
    .drop-area:hover, .drop-area.active {
        border-color: #4CAF50;
    }
    .drop-icon {
        font-size: 2rem;
        color: #aaa;
        margin-bottom: 10px;
    }
    .drop-text {
        color: #666;
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
REPORTS_ENDPOINT = f"{BASE_URL}/reports"
CUSTOM_FIELDS_ENDPOINT = f"{BASE_URL}/customfields"
GROUPS_ENDPOINT = f"{BASE_URL}/groups"
PROJECTS_ENDPOINT = f"{BASE_URL}/projects"  # New endpoint for projects
TAGS_ENDPOINT = f"{BASE_URL}/tags"  # New endpoint for tags
GEOFENCES_ENDPOINT = f"{BASE_URL}/geofences"  # New endpoint for geofences
REMINDERS_ENDPOINT = f"{BASE_URL}/reminders"  # New endpoint for reminders
LOCATIONS_ENDPOINT = f"{BASE_URL}/locations"  # New endpoint for locations

# API Rate Limiting
API_RATE_LIMIT = 300  # Requests per 5 minutes (example value)
API_RATE_REMAINING = API_RATE_LIMIT

# Cache TTL in seconds
CACHE_TTL = {
    "users": 3600,  # 1 hour
    "jobcodes": 3600,  # 1 hour
    "timesheets": 300,  # 5 minutes
    "clients": 1800,  # 30 minutes
    "current_user": 3600,  # 1 hour
    "projects": 3600,  # 1 hour
    "tags": 3600,  # 1 hour
    "geofences": 3600,  # 1 hour
    "reminders": 1800,  # 30 minutes
    "locations": 1800,  # 30 minutes
    "custom_fields": 3600,  # 1 hour
    "groups": 3600,  # 1 hour
}

# Initialize session state variables
def init_session_state():
    """Initialize all session state variables with default values"""
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
    if 'calendar_date' not in st.session_state:
        st.session_state.calendar_date = datetime.now().date()
    if 'calendar_view' not in st.session_state:
        st.session_state.calendar_view = "month"  # "month", "week", or "day"
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = datetime.now().date()
    if 'notifications' not in st.session_state:
        st.session_state.notifications = [
            {"id": 1, "message": "New client added: Acme Corporation", "date": "2023-05-08", "read": False},
            {"id": 2, "message": "Timesheet approval pending", "date": "2023-05-07", "read": False},
            {"id": 3, "message": "Weekly report generated", "date": "2023-05-06", "read": True}
        ]
    if 'cache' not in st.session_state:
        st.session_state.cache = {
            "users": {"data": None, "timestamp": None},
            "jobcodes": {"data": None, "timestamp": None},
            "timesheets": {"data": None, "timestamp": None},
            "clients": {"data": None, "timestamp": None},
            "current_user": {"data": None, "timestamp": None},
            "projects": {"data": None, "timestamp": None},
            "tags": {"data": None, "timestamp": None},
            "geofences": {"data": None, "timestamp": None},
            "reminders": {"data": None, "timestamp": None},
            "locations": {"data": None, "timestamp": None},
            "custom_fields": {"data": None, "timestamp": None},
            "groups": {"data": None, "timestamp": None},
        }
    if 'api_requests_count' not in st.session_state:
        st.session_state.api_requests_count = 0
    if 'api_rate_remaining' not in st.session_state:
        st.session_state.api_rate_remaining = API_RATE_LIMIT
    if 'api_rate_reset' not in st.session_state:
        st.session_state.api_rate_reset = datetime.now() + timedelta(minutes=5)
    if 'api_debug_mode' not in st.session_state:
        st.session_state.api_debug_mode = False
    if 'api_response_log' not in st.session_state:
        st.session_state.api_response_log = []
    if 'sync_in_progress' not in st.session_state:
        st.session_state.sync_in_progress = False
    if 'custom_fields' not in st.session_state:
        st.session_state.custom_fields = {}
    if 'groups' not in st.session_state:
        st.session_state.groups = {}
    if 'projects' not in st.session_state:
        st.session_state.projects = {}
    if 'tags' not in st.session_state:
        st.session_state.tags = {}
    if 'geofences' not in st.session_state:
        st.session_state.geofences = {}
    if 'reminders' not in st.session_state:
        st.session_state.reminders = {}
    if 'locations' not in st.session_state:
        st.session_state.locations = {}
    if 'client_timesheet_map' not in st.session_state:
        st.session_state.client_timesheet_map = {}  # Map client IDs to timesheet IDs
    if 'theme' not in st.session_state:
        st.session_state.theme = "Light"
    if 'accent_color' not in st.session_state:
        st.session_state.accent_color = "#4CAF50"
    if 'date_format' not in st.session_state:
        st.session_state.date_format = "YYYY-MM-DD"
    if 'time_format' not in st.session_state:
        st.session_state.time_format = "24-hour"
    if 'default_calendar_view' not in st.session_state:
        st.session_state.default_calendar_view = "Month"
    if 'week_starts_on' not in st.session_state:
        st.session_state.week_starts_on = "Sunday"
    if 'email_notifications' not in st.session_state:
        st.session_state.email_notifications = True
    if 'daily_summary' not in st.session_state:
        st.session_state.daily_summary = True
    if 'weekly_summary' not in st.session_state:
        st.session_state.weekly_summary = True
    if 'last_api_call' not in st.session_state:
        st.session_state.last_api_call = None
    if 'api_call_history' not in st.session_state:
        st.session_state.api_call_history = []
    if 'api_error_count' not in st.session_state:
        st.session_state.api_error_count = 0
    if 'selected_timesheets' not in st.session_state:
        st.session_state.selected_timesheets = []  # For bulk actions
    if 'bulk_action_mode' not in st.session_state:
        st.session_state.bulk_action_mode = False
    if 'integrations' not in st.session_state:
        st.session_state.integrations = {
            "quickbooks": {"connected": False, "last_sync": None},
            "slack": {"connected": False, "last_sync": None},
            "google_calendar": {"connected": False, "last_sync": None},
            "zapier": {"connected": False, "last_sync": None},
            "jira": {"connected": False, "last_sync": None}
        }
    if 'report_templates' not in st.session_state:
        st.session_state.report_templates = [
            {"id": 1, "name": "Weekly Summary", "description": "Summary of hours by day and job for the week"},
            {"id": 2, "name": "Client Billing", "description": "Detailed timesheet entries for client billing"},
            {"id": 3, "name": "Project Status", "description": "Hours spent on each project with completion status"},
            {"id": 4, "name": "Team Productivity", "description": "Productivity metrics for team members"},
            {"id": 5, "name": "Custom Report", "description": "User-defined custom report template"}
        ]
    if 'favorite_reports' not in st.session_state:
        st.session_state.favorite_reports = [1, 3]  # IDs of favorite report templates
    if 'recent_searches' not in st.session_state:
        st.session_state.recent_searches = []  # Recent search queries
    if 'data_export_history' not in st.session_state:
        st.session_state.data_export_history = []  # History of data exports
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            "dashboard_widgets": ["productivity", "recent_activity", "weekly_summary", "job_distribution"],
            "default_view": "week",
            "auto_refresh": True,
            "refresh_interval": 5,  # minutes
            "show_weekends": True,
            "default_report_format": "excel"
        }
    if 'timesheet_templates' not in st.session_state:
        st.session_state.timesheet_templates = [
            {"id": 1, "name": "Standard Day", "jobcode_id": 1, "duration": 28800, "notes": "Regular workday"},
            {"id": 2, "name": "Half Day", "jobcode_id": 1, "duration": 14400, "notes": "Half day work"},
            {"id": 3, "name": "Meeting", "jobcode_id": 4, "duration": 3600, "notes": "Team meeting"}
        ]
    if 'quick_notes' not in st.session_state:
        st.session_state.quick_notes = [
            "Client meeting",
            "Development work",
            "Bug fixing",
            "Documentation",
            "Team collaboration"
        ]

# Initialize session state
init_session_state()

# Helper Functions
def is_cache_valid(cache_key: str) -> bool:
    """Check if cache for a specific key is still valid"""
    cache_data = st.session_state.cache.get(cache_key)
    if not cache_data or not cache_data["timestamp"]:
        return False
    
    ttl = CACHE_TTL.get(cache_key, 300)  # Default 5 minutes
    cache_age = (datetime.now() - cache_data["timestamp"]).total_seconds()
    
    return cache_age < ttl

def update_cache(cache_key: str, data: Any) -> None:
    """Update cache for a specific key"""
    st.session_state.cache[cache_key] = {
        "data": data,
        "timestamp": datetime.now()
    }

def get_from_cache(cache_key: str) -> Any:
    """Get data from cache if valid"""
    if is_cache_valid(cache_key):
        return st.session_state.cache[cache_key]["data"]
    return None

def log_api_call(endpoint: str, method: str, status_code: int, response_data: Any = None, error: str = None) -> None:
    """Log API call for debugging"""
    timestamp = datetime.now()
    log_entry = {
        "timestamp": timestamp,
        "endpoint": endpoint,
        "method": method,
        "status_code": status_code,
        "success": 200 <= status_code < 300,
        "error": error
    }
    
    # Add to API call history (limit to last 100 calls)
    st.session_state.api_call_history.insert(0, log_entry)
    st.session_state.api_call_history = st.session_state.api_call_history[:100]
    
    # Update last API call
    st.session_state.last_api_call = log_entry
    
    # Update error count if applicable
    if status_code >= 400:
        st.session_state.api_error_count += 1
    
    # Add detailed response data to log if in debug mode
    if st.session_state.api_debug_mode and response_data:
        log_entry = {
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response": response_data if isinstance(response_data, (dict, list)) else str(response_data)[:500]
        }
        st.session_state.api_response_log.insert(0, log_entry)
        st.session_state.api_response_log = st.session_state.api_response_log[:20]  # Keep only last 20 responses

def update_rate_limit(headers: Dict) -> None:
    """Update API rate limit information from response headers"""
    # Example headers: X-Rate-Limit-Limit, X-Rate-Limit-Remaining, X-Rate-Limit-Reset
    # These are example header names, adjust based on actual TSheets API
    if 'X-Rate-Limit-Remaining' in headers:
        try:
            st.session_state.api_rate_remaining = int(headers['X-Rate-Limit-Remaining'])
        except (ValueError, TypeError):
            pass
    
    if 'X-Rate-Limit-Reset' in headers:
        try:
            reset_time = int(headers['X-Rate-Limit-Reset'])
            st.session_state.api_rate_reset = datetime.fromtimestamp(reset_time)
        except (ValueError, TypeError):
            st.session_state.api_rate_reset = datetime.now() + timedelta(minutes=5)

def make_api_request(endpoint: str, method: str = "GET", params: Dict = None, data: Dict = None, 
                     retry_count: int = 0, max_retries: int = 3) -> Optional[Dict]:
    """Make an API request to TSheets with improved error handling and retry logic"""
    if not st.session_state.api_token:
        st.session_state.error_message = "API token is missing. Please log in again."
        return None
    
    # For demo mode, return mock data
    if st.session_state.api_token == "demo_token":
        return generate_mock_response(endpoint, method, params, data)
    
    headers = {
        "Authorization": f"Bearer {st.session_state.api_token}",
        "Content-Type": "application/json"
    }
    
    # Increment API request counter
    st.session_state.api_requests_count += 1
    
    # Check if we're approaching rate limit
    rate_limit_percentage = (API_RATE_LIMIT - st.session_state.api_rate_remaining) / API_RATE_LIMIT * 100
    if rate_limit_percentage > 90 and retry_count == 0:
        logger.warning(f"Approaching API rate limit: {rate_limit_percentage:.1f}% used")
        st.session_state.error_message = f"Warning: Approaching API rate limit ({rate_limit_percentage:.1f}% used). Some requests may be delayed."
    
    try:
        response = None
        if method == "GET":
            response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        elif method == "POST":
            response = requests.post(endpoint, headers=headers, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(endpoint, headers=headers, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(endpoint, headers=headers, json=data, timeout=10)
        
        # Log the API call
        log_api_call(endpoint, method, response.status_code if response else 0)
        
        # Update rate limit info if available in headers
        if response and response.headers:
            update_rate_limit(response.headers)
        
        # Store debug info for troubleshooting
        if endpoint == TIMESHEETS_ENDPOINT and method == "GET":
            st.session_state.debug_info = {
                "endpoint": endpoint,
                "params": params,
                "status_code": response.status_code if response else "No response",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        if response and response.status_code == 200:
            try:
                json_response = response.json()
                # Log detailed response in debug mode
                if st.session_state.api_debug_mode:
                    log_api_call(endpoint, method, response.status_code, json_response)
                return json_response
            except json.JSONDecodeError:
                error_msg = f"Invalid JSON response from API: {response.text[:100]}..."
                log_api_call(endpoint, method, response.status_code, error=error_msg)
                st.session_state.error_message = error_msg
                return None
        elif response and response.status_code == 429:  # Rate limited
            # Wait and retry if we haven't exceeded max retries
            if retry_count < max_retries:
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Retrying after {retry_after} seconds. Retry {retry_count + 1}/{max_retries}")
                time.sleep(min(retry_after, 60))  # Cap at 60 seconds max wait
                return make_api_request(endpoint, method, params, data, retry_count + 1, max_retries)
            else:
                error_msg = "API rate limit exceeded. Please try again later."
                log_api_call(endpoint, method, response.status_code, error=error_msg)
                st.session_state.error_message = error_msg
                return None
        elif response and response.status_code == 401:
            error_msg = "Authentication failed. Your API token may have expired."
            log_api_call(endpoint, method, response.status_code, error=error_msg)
            st.session_state.error_message = error_msg
            st.session_state.authenticated = False
            return None
        else:
            # For other errors, retry a few times with exponential backoff
            if retry_count < max_retries:
                wait_time = 2 ** retry_count  # Exponential backoff: 1, 2, 4 seconds
                logger.warning(f"API request failed with status {response.status_code if response else 'No response'}. "
                              f"Retrying in {wait_time} seconds. Retry {retry_count + 1}/{max_retries}")
                time.sleep(wait_time)
                return make_api_request(endpoint, method, params, data, retry_count + 1, max_retries)
            else:
                error_msg = f"API Error: {response.status_code if response else 'No response'} - {response.text if response else 'No response'}"
                log_api_call(endpoint, method, response.status_code if response else 0, error=error_msg)
                st.session_state.error_message = error_msg
                return None
    except requests.exceptions.Timeout:
        error_msg = f"Request timed out for {endpoint}"
        log_api_call(endpoint, method, 0, error=error_msg)
        
        # Retry on timeout
        if retry_count < max_retries:
            wait_time = 2 ** retry_count
            logger.warning(f"Request timed out. Retrying in {wait_time} seconds. Retry {retry_count + 1}/{max_retries}")
            time.sleep(wait_time)
            return make_api_request(endpoint, method, params, data, retry_count + 1, max_retries)
        else:
            st.session_state.error_message = error_msg
            return None
    except requests.exceptions.ConnectionError:
        error_msg = f"Connection error for {endpoint}. Please check your internet connection."
        log_api_call(endpoint, method, 0, error=error_msg)
        st.session_state.error_message = error_msg
        return None
    except Exception as e:
        error_msg = f"Request Error: {str(e)}"
        log_api_call(endpoint, method, 0, error=error_msg)
        st.session_state.error_message = error_msg
        logger.error(f"API request exception: {str(e)}")
        logger.error(traceback.format_exc())
        return None

def generate_mock_response(endpoint: str, method: str, params: Dict = None, data: Dict = None) -> Dict:
    """Generate mock API response data for demo mode"""
    # Log the mock API call
    log_api_call(endpoint, method, 200)
    
    # Current user endpoint
    if endpoint == CURRENT_USER_ENDPOINT:
        return {
            "results": {
                "users": {
                    "12345": {
                        "id": 12345,
                        "first_name": "Demo",
                        "last_name": "User",
                        "email": "demo@example.com",
                        "company_name": "Demo Company",
                        "active": True,
                        "employee_number": "EMP001",
                        "hire_date": "2020-01-15",
                        "timezone": "America/New_York",
                        "permissions": {
                            "admin": True,
                            "mobile": True,
                            "status_box": True,
                            "reports": True,
                            "manage_timesheets": True,
                            "manage_authorization": True,
                            "manage_users": True,
                            "manage_my_timesheets": True,
                            "manage_jobcodes": True,
                            "approve_timesheets": True
                        }
                    }
                }
            }
        }
    
    # Users endpoint
    elif endpoint == USERS_ENDPOINT:
        return {
            "results": {
                "users": {
                    "12345": {
                        "id": 12345,
                        "first_name": "Demo",
                        "last_name": "User",
                        "email": "demo@example.com",
                        "active": True
                    },
                    "67890": {
                        "id": 67890,
                        "first_name": "Jane",
                        "last_name": "Smith",
                        "email": "jane@example.com",
                        "active": True
                    },
                    "54321": {
                        "id": 54321,
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john@example.com",
                        "active": True
                    },
                    "98765": {
                        "id": 98765,
                        "first_name": "Alice",
                        "last_name": "Johnson",
                        "email": "alice@example.com",
                        "active": True
                    },
                    "13579": {
                        "id": 13579,
                        "first_name": "Bob",
                        "last_name": "Brown",
                        "email": "bob@example.com",
                        "active": False
                    }
                }
            }
        }
    
    # Jobcodes endpoint
    elif endpoint == JOBCODES_ENDPOINT:
        return {
            "results": {
                "jobcodes": {
                    "1": {
                        "id": 1,
                        "name": "Web Development",
                        "type": "regular",
                        "billable": True,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 150,
                        "short_code": "WEB",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "2": {
                        "id": 2,
                        "name": "Mobile App Development",
                        "type": "regular",
                        "billable": True,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 175,
                        "short_code": "MOB",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "3": {
                        "id": 3,
                        "name": "Design",
                        "type": "regular",
                        "billable": True,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 125,
                        "short_code": "DES",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "4": {
                        "id": 4,
                        "name": "Meetings",
                        "type": "regular",
                        "billable": False,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 0,
                        "short_code": "MTG",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "5": {
                        "id": 5,
                        "name": "Administrative",
                        "type": "regular",
                        "billable": False,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 0,
                        "short_code": "ADM",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "6": {
                        "id": 6,
                        "name": "Project Management",
                        "type": "regular",
                        "billable": True,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 135,
                        "short_code": "PM",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "7": {
                        "id": 7,
                        "name": "Quality Assurance",
                        "type": "regular",
                        "billable": True,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 110,
                        "short_code": "QA",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    },
                    "8": {
                        "id": 8,
                        "name": "Research",
                        "type": "regular",
                        "billable": False,
                        "active": True,
                        "assigned_to_all": True,
                        "billable_rate": 0,
                        "short_code": "RES",
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00",
                        "parent_id": 0
                    }
                }
            }
        }
    
    # Timesheets endpoint
    elif endpoint == TIMESHEETS_ENDPOINT:
        # Generate mock timesheet data based on date range
        if method == "GET" and params and 'start_date' in params and 'end_date' in params:
            start_date = datetime.strptime(params['start_date'], "%Y-%m-%d").date()
            end_date = datetime.strptime(params['end_date'], "%Y-%m-%d").date()
            
            timesheets = {}
            timesheet_id = 1000
            
            # Generate timesheets for each day in the range
            current_date = start_date
            while current_date <= end_date:
                # Skip weekends
                if current_date.weekday() < 5:  # Monday to Friday
                    # Generate 1-3 entries per day
                    for i in range(np.random.randint(1, 4)):
                        jobcode_id = np.random.randint(1, 9)  # Random jobcode
                        duration = np.random.randint(3600, 14400)  # 1-4 hours
                        
                        # Create start and end times for regular entries
                        start_hour = np.random.randint(8, 15)
                        start_time = datetime.combine(current_date, time(start_hour, 0, 0))
                        end_time = start_time + timedelta(seconds=duration)
                        
                        timesheet = {
                            "id": timesheet_id,
                            "user_id": 12345,
                            "jobcode_id": jobcode_id,
                            "date": current_date.strftime("%Y-%m-%d"),
                            "duration": duration,
                            "type": "manual" if np.random.random() < 0.3 else "regular",
                            "notes": f"Work on {get_jobcode_name(jobcode_id)} tasks",
                            "customfields": {
                                "client_id": np.random.randint(1001, 1008),
                                "project_id": np.random.randint(1, 5),
                                "billable": jobcode_id in [1, 2, 3, 6, 7]
                            }
                        }
                        
                        # Add start/end times for regular entries
                        if timesheet["type"] == "regular":
                            timesheet["start"] = start_time.isoformat()
                            timesheet["end"] = end_time.isoformat()
                        
                        timesheets[str(timesheet_id)] = timesheet
                        timesheet_id += 1
                
                current_date += timedelta(days=1)
            
            return {
                "results": {
                    "timesheets": timesheets
                }
            }
        
        # Create a new timesheet
        elif method == "POST" and data:
            return {
                "results": {
                    "timesheets": {
                        "9999": {
                            "id": 9999,
                            "_status_code": 200,  {
                        "9999": {
                            "id": 9999,
                            "_status_code": 200,
                            "user_id": data["data"][0]["user_id"],
                            "jobcode_id": data["data"][0]["jobcode_id"],
                            "date": data["data"][0]["date"],
                            "duration": data["data"][0]["duration"],
                            "type": data["data"][0]["type"],
                            "notes": data["data"][0].get("notes", ""),
                            "created": datetime.now().isoformat(),
                            "last_modified": datetime.now().isoformat()
                        }
                    }
                }
            }
        
        # Update a timesheet
        elif method == "PUT" and data:
            return {
                "results": {
                    "timesheets": {
                        str(data["data"][0]["id"]): {
                            "id": data["data"][0]["id"],
                            "_status_code": 200,
                            "user_id": data["data"][0]["user_id"],
                            "jobcode_id": data["data"][0]["jobcode_id"],
                            "date": data["data"][0]["date"],
                            "duration": data["data"][0]["duration"],
                            "type": data["data"][0]["type"],
                            "notes": data["data"][0].get("notes", ""),
                            "last_modified": datetime.now().isoformat()
                        }
                    }
                }
            }
        
        # Delete a timesheet
        elif method == "DELETE":
            return {
                "results": {
                    "_status_code": 200,
                    "message": "Timesheet deleted successfully"
                }
            }
    
    # Projects endpoint
    elif endpoint == PROJECTS_ENDPOINT:
        return {
            "results": {
                "projects": {
                    "1": {
                        "id": 1,
                        "name": "Website Redesign",
                        "client_id": 1001,
                        "status": "in_progress",
                        "budget_hours": 120,
                        "actual_hours": 85,
                        "start_date": "2023-01-15",
                        "due_date": "2023-06-30",
                        "notes": "Complete redesign of client website",
                        "created": "2023-01-01T00:00:00+00:00",
                        "last_modified": "2023-05-15T00:00:00+00:00"
                    },
                    "2": {
                        "id": 2,
                        "name": "Mobile App Development",
                        "client_id": 1002,
                        "status": "in_progress",
                        "budget_hours": 200,
                        "actual_hours": 110,
                        "start_date": "2023-02-01",
                        "due_date": "2023-08-15",
                        "notes": "iOS and Android app development",
                        "created": "2023-01-20T00:00:00+00:00",
                        "last_modified": "2023-05-10T00:00:00+00:00"
                    },
                    "3": {
                        "id": 3,
                        "name": "E-commerce Integration",
                        "client_id": 1003,
                        "status": "not_started",
                        "budget_hours": 80,
                        "actual_hours": 0,
                        "start_date": "2023-06-01",
                        "due_date": "2023-07-31",
                        "notes": "Integrate payment gateway and shopping cart",
                        "created": "2023-04-15T00:00:00+00:00",
                        "last_modified": "2023-04-15T00:00:00+00:00"
                    },
                    "4": {
                        "id": 4,
                        "name": "SEO Optimization",
                        "client_id": 1004,
                        "status": "completed",
                        "budget_hours": 40,
                        "actual_hours": 38,
                        "start_date": "2023-03-01",
                        "due_date": "2023-04-15",
                        "notes": "Improve search engine rankings",
                        "created": "2023-02-15T00:00:00+00:00",
                        "last_modified": "2023-04-16T00:00:00+00:00"
                    }
                }
            }
        }
    
    # Tags endpoint
    elif endpoint == TAGS_ENDPOINT:
        return {
            "results": {
                "tags": {
                    "1": {
                        "id": 1,
                        "name": "Urgent",
                        "color": "#FF0000",
                        "active": True
                    },
                    "2": {
                        "id": 2,
                        "name": "Client Meeting",
                        "color": "#0000FF",
                        "active": True
                    },
                    "3": {
                        "id": 3,
                        "name": "Remote Work",
                        "color": "#00FF00",
                        "active": True
                    },
                    "4": {
                        "id": 4,
                        "name": "Overtime",
                        "color": "#FFA500",
                        "active": True
                    },
                    "5": {
                        "id": 5,
                        "name": "Training",
                        "color": "#800080",
                        "active": True
                    }
                }
            }
        }
    
    # Custom fields endpoint
    elif endpoint == CUSTOM_FIELDS_ENDPOINT:
        return {
            "results": {
                "customfields": {
                    "1": {
                        "id": 1,
                        "name": "Client",
                        "required": True,
                        "applies_to": "timesheet",
                        "type": "managed-list",
                        "active": True
                    },
                    "2": {
                        "id": 2,
                        "name": "Project",
                        "required": True,
                        "applies_to": "timesheet",
                        "type": "managed-list",
                        "active": True
                    },
                    "3": {
                        "id": 3,
                        "name": "Billable",
                        "required": True,
                        "applies_to": "timesheet",
                        "type": "yes-no",
                        "active": True
                    },
                    "4": {
                        "id": 4,
                        "name": "Task Type",
                        "required": False,
                        "applies_to": "timesheet",
                        "type": "free-form",
                        "active": True
                    }
                }
            }
        }
    
    # Groups endpoint
    elif endpoint == GROUPS_ENDPOINT:
        return {
            "results": {
                "groups": {
                    "1": {
                        "id": 1,
                        "name": "Developers",
                        "active": True,
                        "manager_ids": [12345],
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00"
                    },
                    "2": {
                        "id": 2,
                        "name": "Designers",
                        "active": True,
                        "manager_ids": [67890],
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00"
                    },
                    "3": {
                        "id": 3,
                        "name": "Project Managers",
                        "active": True,
                        "manager_ids": [12345],
                        "created": "2022-01-01T00:00:00+00:00",
                        "last_modified": "2022-01-01T00:00:00+00:00"
                    }
                }
            }
        }
    
    # Default response for other endpoints
    return {
        "results": {
            "_status_code": 200,
            "message": "Mock response for demo mode"
        }
    }

def authenticate() -> bool:
    """Authenticate with TSheets API with improved error handling"""
    # Check if we already have valid cached data
    cached_user = get_from_cache("current_user")
    if cached_user:
        st.session_state.authenticated = True
        st.session_state.current_user = cached_user
        return True
    
    # Otherwise make a new API request
    response = make_api_request(CURRENT_USER_ENDPOINT)
    
    if response and 'results' in response and 'users' in response['results']:
        st.session_state.authenticated = True
        # Extract current user info
        try:
            user_data = list(response['results']['users'].values())[0]
            st.session_state.current_user = user_data
            update_cache("current_user", user_data)
            
            # Load initial data
            with st.spinner("Loading data..."):
                load_users()
                load_jobcodes()
                load_timesheets()
                load_clients()
                load_custom_fields()
                load_groups()
                load_projects()
                load_tags()
                st.session_state.last_refresh = datetime.now()
            return True
        except (IndexError, KeyError) as e:
            logger.error(f"Error extracting user data: {str(e)}")
            logger.error(f"Response: {response}")
            st.session_state.error_message = "Error extracting user data from API response."
            st.session_state.authenticated = False
            return False
    else:
        st.session_state.authenticated = False
        return False

def load_users() -> None:
    """Load users from TSheets API with caching"""
    # Check if we have valid cached data
    cached_users = get_from_cache("users")
    if cached_users:
        st.session_state.users = cached_users
        create_user_map()
        return
    
    # Otherwise make a new API request
    response = make_api_request(USERS_ENDPOINT, params={"active": "yes"})
    
    if response and 'results' in response and 'users' in response['results']:
        st.session_state.users = response['results']['users']
        update_cache("users", response['results']['users'])
        create_user_map()
    else:
        # If API request fails, use empty dict
        st.session_state.users = {}
        st.session_state.user_map = {}

def create_user_map() -> None:
    """Create a mapping of user IDs to full names"""
    user_map = {}
    for user_id, user_data in st.session_state.users.items():
        full_name = f"{user_data['first_name']} {user_data['last_name']}"
        user_map[int(user_id)] = full_name
    
    st.session_state.user_map = user_map

def load_jobcodes() -> None:
    """Load jobcodes from TSheets API with caching"""
    # Check if we have valid cached data
    cached_jobcodes = get_from_cache("jobcodes")
    if cached_jobcodes:
        st.session_state.jobcodes = cached_jobcodes
        return
    
    # Otherwise make a new API request
    response = make_api_request(JOBCODES_ENDPOINT, params={"active": "yes"})
    
    if response and 'results' in response and 'jobcodes' in response['results']:
        st.session_state.jobcodes = response['results']['jobcodes']
        update_cache("jobcodes", response['results']['jobcodes'])
    else:
        # If API request fails, use empty dict
        st.session_state.jobcodes = {}

def load_custom_fields() -> None:
    """Load custom fields from TSheets API"""
    # Check if we have valid cached data
    cached_custom_fields = get_from_cache("custom_fields")
    if cached_custom_fields:
        st.session_state.custom_fields = cached_custom_fields
        return
    
    # Otherwise make a new API request
    response = make_api_request(CUSTOM_FIELDS_ENDPOINT)
    
    if response and 'results' in response and 'customfields' in response['results']:
        st.session_state.custom_fields = response['results']['customfields']
        update_cache("custom_fields", response['results']['customfields'])
    else:
        # If API request fails, use empty dict
        st.session_state.custom_fields = {}

def load_groups() -> None:
    """Load groups from TSheets API"""
    # Check if we have valid cached data
    cached_groups = get_from_cache("groups")
    if cached_groups:
        st.session_state.groups = cached_groups
        return
    
    # Otherwise make a new API request
    response = make_api_request(GROUPS_ENDPOINT)
    
    if response and 'results' in response and 'groups' in response['results']:
        st.session_state.groups = response['results']['groups']
        update_cache("groups", response['results']['groups'])
    else:
        # If API request fails, use empty dict
        st.session_state.groups = {}

def load_projects() -> None:
    """Load projects from TSheets API"""
    # Check if we have valid cached data
    cached_projects = get_from_cache("projects")
    if cached_projects:
        st.session_state.projects = cached_projects
        return
    
    # Otherwise make a new API request
    response = make_api_request(PROJECTS_ENDPOINT)
    
    if response and 'results' in response and 'projects' in response['results']:
        st.session_state.projects = response['results']['projects']
        update_cache("projects", response['results']['projects'])
    else:
        # If API request fails, use empty dict
        st.session_state.projects = {}

def load_tags() -> None:
    """Load tags from TSheets API"""
    # Check if we have valid cached data
    cached_tags = get_from_cache("tags")
    if cached_tags:
        st.session_state.tags = cached_tags
        return
    
    # Otherwise make a new API request
    response = make_api_request(TAGS_ENDPOINT)
    
    if response and 'results' in response and 'tags' in response['results']:
        st.session_state.tags = response['results']['tags']
        update_cache("tags", response['results']['tags'])
    else:
        # If API request fails, use empty dict
        st.session_state.tags = {}

def load_timesheets() -> None:
    """Load timesheets from TSheets API with improved error handling and caching"""
    # Set sync in progress flag
    st.session_state.sync_in_progress = True
    
    try:
        # Check if we have valid cached data and it's not too old
        cached_timesheets = get_from_cache("timesheets")
        if cached_timesheets:
            st.session_state.timesheets = cached_timesheets
            st.session_state.sync_in_progress = False
            return
        
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
            update_cache("timesheets", timesheets)
            
            # Map timesheets to clients (in a real app, you'd use actual client IDs)
            map_timesheets_to_clients(timesheets)
            
            # Clear any previous error message about timesheets
            if st.session_state.error_message and "timesheet" in st.session_state.error_message.lower():
                st.session_state.error_message = None
        else:
            # If no timesheets found or error, set to empty list
            st.session_state.timesheets = []
            
            # Add more specific error message if needed
            if not st.session_state.error_message:
                st.session_state.error_message = "Failed to load timesheet data. Please check your API token and connection."
    except Exception as e:
        logger.error(f"Error loading timesheets: {str(e)}")
        logger.error(traceback.format_exc())
        st.session_state.error_message = f"Error loading timesheets: {str(e)}"
        st.session_state.timesheets = []
    finally:
        # Clear sync in progress flag
        st.session_state.sync_in_progress = False

def map_timesheets_to_clients(timesheets: List[Dict]) -> None:
    """Map timesheets to clients based on jobcode or custom fields"""
    client_timesheet_map = {}
    
    # In a real implementation, you would use actual client IDs from your timesheets
    for ts in timesheets:
        try:
            # Check if timesheet has client_id in customfields
            client_id = None
            if 'customfields' in ts and 'client_id' in ts['customfields']:
                client_id = ts['customfields']['client_id']
            else:
                # Mock logic: assign to clients based on jobcode_id modulo number of clients
                if st.session_state.clients:
                    jobcode_id = ts['jobcode_id']
                    client_index = int(jobcode_id) % len(st.session_state.clients)
                    client_id = st.session_state.clients[client_index]['id']
            
            if client_id:
                if client_id not in client_timesheet_map:
                    client_timesheet_map[client_id] = []
                
                client_timesheet_map[client_id].append(ts['id'])
        except (KeyError, ValueError, IndexError):
            continue
    
    st.session_state.client_timesheet_map = client_timesheet_map

def load_clients() -> None:
    """Load clients from TSheets API (using customfields as a proxy)"""
    # Check if we have valid cached data
    cached_clients = get_from_cache("clients")
    if cached_clients:
        st.session_state.clients = cached_clients
        return
    
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
        },
        {
            "id": 1006,
            "name": "Umbrella Corporation",
            "contact": "Albert Wesker",
            "email": "wesker@umbrella.com",
            "phone": "555-VIRUS",
            "address": "123 Raccoon St, Raccoon City, USA",
            "status": "active",
            "industry": "Pharmaceuticals",
            "notes": "Biotech research projects",
            "created_date": "2022-09-15",
            "last_contact": "2023-05-01",
            "projects": ["Vaccine Development", "Genetic Research"],
            "total_hours": 325.5,
            "billing_rate": 275,
            "avatar": "https://www.gravatar.com/avatar/55555555555555555555555555555555?d=mp&f=y"
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
    
    st.session_state.clients = clients
    update_cache("clients", clients)

def format_duration(seconds: int) -> str:
    """Format duration in seconds to HH:MM:SS"""
    if seconds is None:
        return "00:00:00"
    
    try:
        seconds = int(seconds)
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    except (ValueError, TypeError):
        logger.error(f"Error formatting duration: {seconds}")
        return "00:00:00"

def format_duration_hours(seconds: int) -> str:
    """Format duration in seconds to decimal hours"""
    if seconds is None:
        return "0.00"
    
    try:
        hours = float(seconds) / 3600
        return f"{hours:.2f}"
    except (ValueError, TypeError):
        logger.error(f"Error formatting duration hours: {seconds}")
        return "0.00"

def get_jobcode_name(jobcode_id: Union[int, str]) -> str:
    """Get jobcode name from jobcode ID with error handling"""
    try:
        jobcode_id = str(int(jobcode_id))
        if jobcode_id in st.session_state.jobcodes:
            return st.session_state.jobcodes[jobcode_id]['name']
        return f"Job {jobcode_id}"
    except (ValueError, TypeError):
        logger.error(f"Invalid jobcode_id: {jobcode_id}")
        return f"Job (unknown)"

def get_user_name(user_id: Union[int, str]) -> str:
    """Get user full name from user ID with error handling"""
    try:
        user_id = int(user_id)
        if user_id in st.session_state.user_map:
            return st.session_state.user_map[user_id]
        return f"User {user_id}"
    except (ValueError, TypeError):
        logger.error(f"Invalid user_id: {user_id}")
        return f"User (unknown)"

def get_project_name(project_id: Union[int, str]) -> str:
    """Get project name from project ID with error handling"""
    try:
        project_id = str(int(project_id))
        if project_id in st.session_state.projects:
            return st.session_state.projects[project_id]['name']
        return f"Project {project_id}"
    except (ValueError, TypeError):
        logger.error(f"Invalid project_id: {project_id}")
        return f"Project (unknown)"

def get_client_name(client_id: Union[int, str]) -> str:
    """Get client name from client ID with error handling"""
    try:
        client_id = int(client_id)
        client = get_client_by_id(client_id)
        if client:
            return client['name']
        return f"Client {client_id}"
    except (ValueError, TypeError):
        logger.error(f"Invalid client_id: {client_id}")
        return f"Client (unknown)"

def create_timesheet(data: Dict) -> bool:
    """Create a new timesheet entry with improved error handling"""
    payload = {
        "data": [data]
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="POST", data=payload)
    
    if response and 'results' in response and 'timesheets' in response['results']:
        st.session_state.success_message = "Timesheet entry created successfully!"
        # Invalidate timesheets cache
        st.session_state.cache["timesheets"]["timestamp"] = None
        # Reload timesheets to show the new entry
        load_timesheets()
        return True
    
    # Add more specific error message
    if not st.session_state.error_message:
        st.session_state.error_message = "Failed to create timesheet entry. Please check your inputs and try again."
    
    return False

def update_timesheet(timesheet_id: Union[int, str], data: Dict) -> bool:
    """Update an existing timesheet entry with improved error handling"""
    payload = {
        "data": [{
            "id": timesheet_id,
            **data
        }]
    }
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="PUT", data=payload)
    
    if response and 'results' in response and 'timesheets' in response['results']:
        st.session_state.success_message = "Timesheet entry updated successfully!"
        # Invalidate timesheets cache
        st.session_state.cache["timesheets"]["timestamp"] = None
        # Reload timesheets to show the updated entry
        load_timesheets()
        return True
    
    # Add more specific error message
    if not st.session_state.error_message:
        st.session_state.error_message = "Failed to update timesheet entry. Please check your inputs and try again."
    
    return False

def delete_timesheet(timesheet_id: Union[int, str]) -> bool:
    """Delete a timesheet entry with improved error handling"""
    response = make_api_request(f"{TIMESHEETS_ENDPOINT}?ids={timesheet_id}", method="DELETE")
    
    if response and 'results' in response:
        st.session_state.success_message = "Timesheet entry deleted successfully!"
        # Invalidate timesheets cache
        st.session_state.cache["timesheets"]["timestamp"] = None
        # Reload timesheets to show the changes
        load_timesheets()
        return True
    
    # Add more specific error message
    if not st.session_state.error_message:
        st.session_state.error_message = "Failed to delete timesheet entry. Please try again."
    
    return False

def bulk_delete_timesheets(timesheet_ids: List[Union[int, str]]) -> bool:
    """Delete multiple timesheet entries"""
    if not timesheet_ids:
        return False
    
    # Convert list to comma-separated string
    ids_str = ",".join(str(id) for id in timesheet_ids)
    
    response = make_api_request(f"{TIMESHEETS_ENDPOINT}?ids={ids_str}", method="DELETE")
    
    if response and 'results' in response:
        st.session_state.success_message = f"Successfully deleted {len(timesheet_ids)} timesheet entries!"
        # Invalidate timesheets cache
        st.session_state.cache["timesheets"]["timestamp"] = None
        # Reload timesheets to show the changes
        load_timesheets()
        # Clear selected timesheets
        st.session_state.selected_timesheets = []
        return True
    
    # Add more specific error message
    if not st.session_state.error_message:
        st.session_state.error_message = "Failed to delete timesheet entries. Please try again."
    
    return False

def bulk_update_timesheets(timesheet_ids: List[Union[int, str]], update_data: Dict) -> bool:
    """Update multiple timesheet entries with the same data"""
    if not timesheet_ids or not update_data:
        return False
    
    # Prepare payload with multiple timesheet entries
    payload = {
        "data": []
    }
    
    for ts_id in timesheet_ids:
        payload["data"].append({
            "id": ts_id,
            **update_data
        })
    
    response = make_api_request(TIMESHEETS_ENDPOINT, method="PUT", data=payload)
    
    if response and 'results' in response and 'timesheets' in response['results']:
        st.session_state.success_message = f"Successfully updated {len(timesheet_ids)} timesheet entries!"
        # Invalidate timesheets cache
        st.session_state.cache["timesheets"]["timestamp"] = None
        # Reload timesheets to show the updated entries
        load_timesheets()
        # Clear selected timesheets
        st.session_state.selected_timesheets = []
        return True
    
    # Add more specific error message
    if not st.session_state.error_message:
        st.session_state.error_message = "Failed to update timesheet entries. Please try again."
    
    return False

def get_timesheet_dataframe(timesheets: List[Dict]) -> pd.DataFrame:
    """Convert timesheet data to a DataFrame for analysis with improved error handling"""
    if not timesheets:
        return pd.DataFrame()
    
    data = []
    for ts in timesheets:
        try:
            # Format dates and times
            entry_date = datetime.strptime(ts['date'], "%Y-%m-%d")
            
            # Handle different timesheet types
            if ts['type'] == 'regular':
                start_time = datetime.fromisoformat(ts['start'].replace('Z', '+00:00')) if 'start' in ts and ts['start'] else None
                end_time = datetime.fromisoformat(ts['end'].replace('Z', '+00:00')) if 'end' in ts and ts['end'] else None
            else:  # manual timesheet
                start_time = None
                end_time = None
            
            # Extract client and project IDs from customfields if available
            client_id = None
            project_id = None
            billable = False
            
            if 'customfields' in ts:
                if 'client_id' in ts['customfields']:
                    client_id = ts['customfields']['client_id']
                if 'project_id' in ts['customfields']:
                    project_id = ts['customfields']['project_id']
                if 'billable' in ts['customfields']:
                    billable = ts['customfields']['billable']
            
            # If client_id is not in customfields, try to get it from client_timesheet_map
            if not client_id and hasattr(st.session_state, 'client_timesheet_map'):
                for cid, ts_ids in st.session_state.client_timesheet_map.items():
                    if ts['id'] in ts_ids:
                        client_id = cid
                        break
            
            # Get client and project names
            client_name = get_client_name(client_id) if client_id else "Unassigned"
            project_name = get_project_name(project_id) if project_id else "Unassigned"
            
            # For billable, if not in customfields, determine based on jobcode
            if not billable and 'jobcode_id' in ts:
                jobcode_id = str(ts['jobcode_id'])
                if jobcode_id in st.session_state.jobcodes:
                    billable = st.session_state.jobcodes[jobcode_id].get('billable', False)
            
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
                "duration_seconds": ts.get('duration', 0),
                "duration_hours": ts.get('duration', 0) / 3600,
                "duration_formatted": format_duration(ts.get('duration', 0)),
                "type": ts.get('type', '').capitalize(),
                "notes": ts.get('notes', ''),
                "on_the_clock": ts.get('on_the_clock', False),
                "client_id": client_id,
                "client_name": client_name,
                "project_id": project_id,
                "project_name": project_name,
                "billable": billable,
                "customfields": ts.get('customfields', {})
            })
        except Exception as e:
            # Skip entries with invalid data
            logger.error(f"Error processing timesheet entry: {str(e)}")
            logger.error(f"Problematic timesheet: {ts}")
            continue
    
    return pd.DataFrame(data)

def generate_dashboard_metrics(df: pd.DataFrame) -> Dict:
    """Generate metrics for the dashboard with improved calculations"""
    if df.empty:
        return {
            "total_hours": "0:00:00",
            "total_hours_decimal": "0.00",
            "avg_daily_hours": "0.00",
            "days_worked": 0,
            "most_common_job": "N/A",
            "billable_hours": "0.00",
            "non_billable_hours": "0.00",
            "productivity_score": 0,
            "utilization_rate": 0,
            "weekly_target_met": False,
            "weekly_target_percentage": 0,
            "trend": "neutral",  # neutral, up, down
            "most_common_client": "N/A",
            "most_common_project": "N/A",
            "billable_percentage": 0
        }
    
    total_seconds = df['duration_seconds'].sum()
    days_worked = df['date'].nunique()
    
    # Calculate average daily hours (only for days worked)
    avg_daily_seconds = total_seconds / days_worked if days_worked > 0 else 0
    
    # Get most common job
    if not df.empty:
        job_counts = df['job_name'].value_counts()
        most_common_job = job_counts.index[0] if not job_counts.empty else "N/A"
        
        # Get most common client
        client_counts = df['client_name'].value_counts()
        most_common_client = client_counts.index[0] if not client_counts.empty else "N/A"
        
        # Get most common project
        project_counts = df['project_name'].value_counts()
        most_common_project = project_counts.index[0] if not project_counts.empty else "N/A"
    else:
        most_common_job = "N/A"
        most_common_client = "N/A"
        most_common_project = "N/A"
    
    # Calculate billable vs non-billable hours
    if 'billable' in df.columns:
        billable_mask = df['billable'] == True
        billable_seconds = df.loc[billable_mask, 'duration_seconds'].sum()
        non_billable_seconds = df.loc[~billable_mask, 'duration_seconds'].sum()
        billable_percentage = (billable_seconds / total_seconds * 100) if total_seconds > 0 else 0
    else:
        # Fallback to the mock data approach
        billable_seconds = total_seconds * 0.75  # Assuming 75% billable
        non_billable_seconds = total_seconds * 0.25
        billable_percentage = 75
    
    # Calculate productivity score
    # Assuming 40-hour work week (8 hours per day, 5 days per week)
    weekly_target_seconds = 40 * 3600
    current_week_mask = df['date'] >= (datetime.now().date() - timedelta(days=datetime.now().weekday()))
    current_week_seconds = df.loc[current_week_mask, 'duration_seconds'].sum() if not current_week_mask.empty else 0
    weekly_target_percentage = min(100, int((current_week_seconds / weekly_target_seconds) * 100))
    weekly_target_met = weekly_target_percentage >= 100
    
    # Calculate overall productivity score
    productivity_score = min(100, int((total_seconds / (8 * 3600 * days_worked)) * 100)) if days_worked > 0 else 0
    
    # Calculate utilization rate (billable hours / total hours)
    utilization_rate = min(100, int((billable_seconds / total_seconds) * 100)) if total_seconds > 0 else 0
    
    # Calculate trend (comparing current week to previous week)
    prev_week_start = datetime.now().date() - timedelta(days=datetime.now().weekday() + 7)
    prev_week_end = datetime.now().date() - timedelta(days=datetime.now().weekday() + 1)
    prev_week_mask = (df['date'] >= prev_week_start) & (df['date'] <= prev_week_end)
    prev_week_seconds = df.loc[prev_week_mask, 'duration_seconds'].sum() if not prev_week_mask.empty else 0
    
    # Compare current week progress to same point in previous week
    days_into_week = min(datetime.now().weekday() + 1, 5)  # Cap at 5 for business days
    prev_week_prorated = prev_week_seconds * (days_into_week / 5)
    
    if current_week_seconds > prev_week_prorated * 1.1:  # 10% improvement
        trend = "up"
    elif current_week_seconds < prev_week_prorated * 0.9:  # 10% decline
        trend = "down"
    else:
        trend = "neutral"
    
    return {
        "total_hours": format_duration(total_seconds),
        "total_hours_decimal": format_duration_hours(total_seconds),
        "avg_daily_hours": format_duration_hours(avg_daily_seconds),
        "days_worked": days_worked,
        "most_common_job": most_common_job,
        "most_common_client": most_common_client,
        "most_common_project": most_common_project,
        "billable_hours": format_duration_hours(billable_seconds),
        "non_billable_hours": format_duration_hours(non_billable_seconds),
        "billable_percentage": round(billable_percentage, 1),
        "productivity_score": productivity_score,
        "utilization_rate": utilization_rate,
        "weekly_target_met": weekly_target_met,
        "weekly_target_percentage": weekly_target_percentage,
        "trend": trend
    }

def generate_weekly_report(df: pd.DataFrame) -> pd.DataFrame:
    """Generate weekly report data with improved calculations"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by week and calculate total hours
    weekly_data = df.groupby(['year', 'week_number']).agg({
        'duration_seconds': 'sum',
        'date': ['min', 'max'],  # Get first and last day of each week
        'id': 'count',  # Count entries
        'billable': lambda x: (x == True).sum() if 'billable' in df.columns else 0  # Count billable entries
    }).reset_index()
    
    # Flatten multi-level columns
    weekly_data.columns = ['year', 'week_number', 'duration_seconds', 'week_start', 'week_end', 'entry_count', 'billable_count']
    
    # Format the data
    weekly_data['week_ending'] = weekly_data['week_end'].apply(
        lambda x: x.strftime("%b %d, %Y")
    )
    weekly_data['week_starting'] = weekly_data['week_start'].apply(
        lambda x: x.strftime("%b %d, %Y")
    )
    weekly_data['week_label'] = weekly_data.apply(
        lambda x: f"Week {x['week_number']} ({x['week_starting']} - {x['week_ending']})",
        axis=1
    )
    weekly_data['hours'] = weekly_data['duration_seconds'] / 3600
    weekly_data['hours_formatted'] = weekly_data['duration_seconds'].apply(format_duration)
    
    # Calculate target achievement (assuming 40-hour work week)
    weekly_data['target_hours'] = 40
    weekly_data['target_percentage'] = (weekly_data['hours'] / weekly_data['target_hours'] * 100).round(1)
    weekly_data['target_met'] = weekly_data['hours'] >= weekly_data['target_hours']
    
    # Calculate billable percentage
    weekly_data['billable_percentage'] = (weekly_data['billable_count'] / weekly_data['entry_count'] * 100).round(1).fillna(0)
    
    return weekly_data.sort_values(by=['year', 'week_number'], ascending=False)

def generate_job_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate job summary data with improved calculations"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by job and calculate total hours
    job_data = df.groupby('job_name').agg({
        'duration_seconds': 'sum',
        'id': 'count',
        'date': 'nunique',  # Count unique days
        'billable': lambda x: (x == True).mean() * 100 if 'billable' in df.columns else 0  # Billable percentage
    }).reset_index()
    
    # Rename columns
    job_data.columns = ['Job', 'Total Seconds', 'Entry Count', 'Days Worked', 'Billable Percentage']
    
    # Add formatted hours
    job_data['Hours'] = job_data['Total Seconds'] / 3600
    job_data['Hours Formatted'] = job_data['Total Seconds'].apply(format_duration)
    
    # Calculate percentage of total time
    total_seconds = job_data['Total Seconds'].sum()
    job_data['Percentage'] = (job_data['Total Seconds'] / total_seconds * 100).round(2)
    
    # Calculate average hours per day
    job_data['Avg Hours Per Day'] = (job_data['Hours'] / job_data['Days Worked']).round(2)
    
    # Round billable percentage
    job_data['Billable Percentage'] = job_data['Billable Percentage'].round(1)
    
    return job_data.sort_values(by='Total Seconds', ascending=False)

def generate_client_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate client summary data"""
    if df.empty or 'client_name' not in df.columns:
        return pd.DataFrame()
    
    # Group by client and calculate total hours
    client_data = df.groupby('client_name').agg({
        'duration_seconds': 'sum',
        'id': 'count',
        'date': 'nunique',  # Count unique days
        'billable': lambda x: (x == True).mean() * 100 if 'billable' in df.columns else 0  # Billable percentage
    }).reset_index()
    
    # Rename columns
    client_data.columns = ['Client', 'Total Seconds', 'Entry Count', 'Days Worked', 'Billable Percentage']
    
    # Add formatted hours
    client_data['Hours'] = client_data['Total Seconds'] / 3600
    client_data['Hours Formatted'] = client_data['Total Seconds'].apply(format_duration)
    
    # Calculate percentage of total time
    total_seconds = client_data['Total Seconds'].sum()
    client_data['Percentage'] = (client_data['Total Seconds'] / total_seconds * 100).round(2)
    
    # Calculate average hours per day
    client_data['Avg Hours Per Day'] = (client_data['Hours'] / client_data['Days Worked']).round(2)
    
    # Round billable percentage
    client_data['Billable Percentage'] = client_data['Billable Percentage'].round(1)
    
    # Add estimated billing amount (using client billing rates from client data)
    client_data['Billing Rate'] = 0
    client_data['Estimated Billing'] = 0
    
    for i, row in client_data.iterrows():
        client_name = row['Client']
        for client in st.session_state.clients:
            if client['name'] == client_name:
                billing_rate = client.get('billing_rate', 0)
                client_data.at[i, 'Billing Rate'] = billing_rate
                client_data.at[i, 'Estimated Billing'] = round(row['Hours'] * billing_rate, 2)
                break
    
    return client_data.sort_values(by='Total Seconds', ascending=False)

def generate_project_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate project summary data"""
    if df.empty or 'project_name' not in df.columns:
        return pd.DataFrame()
    
    # Group by project and calculate total hours
    project_data = df.groupby('project_name').agg({
        'duration_seconds': 'sum',
        'id': 'count',
        'date': 'nunique',  # Count unique days
        'billable': lambda x: (x == True).mean() * 100 if 'billable' in df.columns else 0  # Billable percentage
    }).reset_index()
    
    # Rename columns
    project_data.columns = ['Project', 'Total Seconds', 'Entry Count', 'Days Worked', 'Billable Percentage']
    
    # Add formatted hours
    project_data['Hours'] = project_data['Total Seconds'] / 3600
    project_data['Hours Formatted'] = project_data['Total Seconds'].apply(format_duration)
    
    # Calculate percentage of total time
    total_seconds = project_data['Total Seconds'].sum()
    project_data['Percentage'] = (project_data['Total Seconds'] / total_seconds * 100).round(2)
    
    # Calculate average hours per day
    project_data['Avg Hours Per Day'] = (project_data['Hours'] / project_data['Days Worked']).round(2)
    
    # Round billable percentage
    project_data['Billable Percentage'] = project_data['Billable Percentage'].round(1)
    
    # Add project status and completion percentage if available
    project_data['Status'] = "Unknown"
    project_data['Completion'] = 0
    
    for i, row in project_data.iterrows():
        project_name = row['Project']
        for project_id, project in st.session_state.projects.items():
            if project['name'] == project_name:
                project_data.at[i, 'Status'] = project.get('status', 'Unknown')
                
                # Calculate completion percentage based on budget hours
                budget_hours = project.get('budget_hours', 0)
                if budget_hours > 0:
                    completion = min(100, round((row['Hours'] / budget_hours) * 100, 1))
                    project_data.at[i, 'Completion'] = completion
                break
    
    return project_data.sort_values(by='Total Seconds', ascending=False)

def generate_daily_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Generate daily summary data with improved calculations"""
    if df.empty:
        return pd.DataFrame()
    
    # Group by date and calculate total hours
    daily_data = df.groupby(['date', 'date_str', 'day_of_week']).agg({
        'duration_seconds': 'sum',
        'id': 'count',
        'job_name': lambda x: ', '.join(sorted(set(x))),  # List unique jobs
        'billable': lambda x: (x == True).mean() * 100 if 'billable' in df.columns else 0  # Billable percentage
    }).reset_index()
    
    # Rename columns
    daily_data.columns = ['Date', 'Date String', 'Day of Week', 'Total Seconds', 'Entry Count', 'Jobs', 'Billable Percentage']
    
    # Add formatted hours
    daily_data['Hours'] = daily_data['Total Seconds'] / 3600
    daily_data['Hours Formatted'] = daily_data['Total Seconds'].apply(format_duration)
    
    # Calculate target achievement (assuming 8-hour work day)
    daily_data['Target Hours'] = 8
    daily_data['Target Percentage'] = (daily_data['Hours'] / daily_data['Target Hours'] * 100).round(1)
    daily_data['Target Met'] = daily_data['Hours'] >= daily_data['Target Hours']
    
    # Round billable percentage
    daily_data['Billable Percentage'] = daily_data['Billable Percentage'].round(1)
    
    return daily_data.sort_values(by='Date', ascending=False)

def generate_client_timesheet_summary(df: pd.DataFrame, client_id: int = None) -> pd.DataFrame:
    """Generate timesheet summary for a specific client with improved filtering"""
    if df.empty:
        return pd.DataFrame()
    
    # Filter by client ID if provided and client_id column exists
    if client_id is not None and 'client_id' in df.columns:
        df = df[df['client_id'] == client_id]
    
    # If still empty after filtering, return empty DataFrame
    if df.empty:
        return pd.DataFrame()
    
    # Group by date and job
    client_summary = df.groupby(['date_str', 'job_name']).agg({
        'duration_seconds': 'sum',
        'id': 'count',
        'notes': lambda x: ' | '.join(filter(None, x)),  # Combine non-empty notes
        'billable': lambda x: (x == True).mean() * 100 if 'billable' in df.columns else 0  # Billable percentage
    }).reset_index()
    
    # Rename columns
    client_summary.columns = ['Date', 'Job', 'Total Seconds', 'Entry Count', 'Notes', 'Billable Percentage']
    
    # Add formatted hours
    client_summary['Hours'] = client_summary['Total Seconds'] / 3600
    client_summary['Hours Formatted'] = client_summary['Total Seconds'].apply(format_duration)
    
    # Round billable percentage
    client_summary['Billable Percentage'] = client_summary['Billable Percentage'].round(1)
    
    return client_summary.sort_values(by=['Date', 'Hours'], ascending=[False, False])

def get_download_link(df: pd.DataFrame, filename: str, link_text: str) -> str:
    """Generate a download link for a DataFrame with error handling"""
    if df.empty:
        return "No data to download"
    
    try:
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
        return href
    except Exception as e:
        logger.error(f"Error generating download link: {str(e)}")
        return "Error generating download link"

def get_excel_download_link(df: pd.DataFrame, filename: str, link_text: str) -> str:
    """Generate a download link for a DataFrame as Excel with error handling"""
    if df.empty:
        return "No data to download"
    
    try:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Sheet1', index=False)
        
        excel_data = output.getvalue()
        b64 = base64.b64encode(excel_data).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
        return href
    except Exception as e:
        logger.error(f"Error generating Excel download link: {str(e)}")
        return "Error generating Excel download link"

def get_pdf_download_link(df: pd.DataFrame, filename: str, link_text: str) -> str:
    """Generate a download link for a DataFrame as PDF with error handling"""
    if df.empty:
        return "No data to download"
    
    try:
        # This is a simplified version - in a real app, you'd use a PDF library
        # For this example, we'll just convert to HTML and encode it
        html = df.to_html(index=False)
        b64 = base64.b64encode(html.encode()).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}" class="download-link">{link_text}</a>'
        return href
    except Exception as e:
        logger.error(f"Error generating PDF download link: {str(e)}")
        return "Error generating PDF download link"

def get_date_range_presets() -> Dict:
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

def search_clients(query: str, clients: List[Dict]) -> List[Dict]:
    """Search clients by name, contact, or email with improved matching"""
    if not query:
        return clients
    
    query = query.lower()
    results = []
    
    for client in clients:
        # Check for matches in multiple fields
        if (query in client['name'].lower() or 
            query in client['contact'].lower() or 
            query in client['email'].lower() or
            query in client['industry'].lower() or
            query in client.get('notes', '').lower()):
            
            # Calculate a simple relevance score
            score = 0
            if query in client['name'].lower():
                score += 3  # Name matches are most important
            if query in client['contact'].lower():
                score += 2
            if query in client['email'].lower():
                score += 1
            if query in client['industry'].lower():
                score += 1
            if query in client.get('notes', '').lower():
                score += 0.5
                
            # Add score to client object for sorting
            client_with_score = client.copy()
            client_with_score['_search_score'] = score
            results.append(client_with_score)
    
    # Sort by relevance score
    results.sort(key=lambda x: x['_search_score'], reverse=True)
    
    # Remove the temporary score field
    for client in results:
        if '_search_score' in client:
            del client['_search_score']
    
    return results

def get_client_by_id(client_id: int) -> Optional[Dict]:
    """Get client by ID with error handling"""
    if not client_id:
        return None
        
    for client in st.session_state.clients:
        if client['id'] == client_id:
            return client
    return None

def get_client_timesheets(client_id: int) -> List[Dict]:
    """Get timesheets for a specific client with improved mapping"""
    if not client_id or not st.session_state.timesheets:
        return []
    
    # Check if we have a mapping from clients to timesheets
    if hasattr(st.session_state, 'client_timesheet_map') and client_id in st.session_state.client_timesheet_map:
        timesheet_ids = st.session_state.client_timesheet_map[client_id]
        return [ts for ts in st.session_state.timesheets if ts['id'] in timesheet_ids]
    
    # Fallback to the mock implementation if no mapping exists
    client_index = client_id % 7  # Use modulo to distribute timesheets
    return [ts for i, ts in enumerate(st.session_state.timesheets) if i % 7 == client_index]

}

