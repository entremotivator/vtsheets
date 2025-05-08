"""
This file contains the new Python functions and integration
instructions for enhancing the TSheets CRM Manager Pro Streamlit application.

Due to limitations in reading the entirety of your original large code file,
I cannot provide a single, fully merged file. You will need to integrate
these components into your existing script (`pasted_content.txt`).

Instructions:
1.  Copy the new functions provided below into your main Python script.
    A logical place would be alongside other data processing or display functions.
2.  Modify the main application layout section (where tabs are defined and handled)
    as shown in the 'TAB INTEGRATION EXAMPLE' section.
3.  Ensure all necessary libraries are imported (Plotly, pandas, datetime, calendar
    are likely already in your script).
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import calendar
import plotly.express as px

# Assume these helper functions exist in your original code:
# format_duration(seconds) -> str (e.g., "10:30:00")
# format_duration_hours(seconds) -> str (e.g., "10.50")

# Placeholder for original helper functions if you need to run this standalone for testing parts
# def format_duration(seconds):
#     if pd.isna(seconds) or seconds < 0:
#         return "0:00:00"
#     hours = int(seconds // 3600)
#     minutes = int((seconds % 3600) // 60)
#     secs = int(seconds % 60)
#     return f"{hours:02d}:{minutes:02d}:{secs:02d}"

# def format_duration_hours(seconds):
#     if pd.isna(seconds) or seconds < 0:
#         return "0.00"
#     return f"{seconds / 3600:.2f}"

# --- NEW FUNCTION: Calculate Employee Performance Metrics ---
def calculate_employee_performance_metrics(df: pd.DataFrame, standard_workday_hours: float = 8.0, standard_workweek_hours: float = 40.0) -> dict:
    """Calculates detailed employee performance metrics from the timesheet DataFrame."""
    if df.empty:
        return {
            "total_hours_logged_seconds": 0,
            "total_hours_logged_formatted": "0:00:00",
            "total_hours_logged_decimal": "0.00",
            "num_days_worked": 0,
            "num_weeks_worked": 0,
            "avg_daily_hours_decimal": "0.00",
            "avg_weekly_hours_decimal": "0.00",
            "billable_hours_seconds": 0,
            "billable_hours_decimal": "0.00",
            "non_billable_hours_seconds": 0,
            "non_billable_hours_decimal": "0.00",
            "billable_percentage": 0,
            "daily_overtime_hours_decimal": "0.00",
            "weekly_overtime_hours_decimal": "0.00",
            "job_code_distribution_percent": {},
            "job_code_distribution_hours": {},
            "avg_entries_per_day": "0.00",
            "avg_entries_per_week": "0.00",
            "utilization_rate_vs_logged": 0,
            "utilization_rate_vs_standard": 0,
        }

    df_copy = df.copy() # Avoid modifying original DataFrame if passed by reference
    total_seconds = df_copy['duration_seconds'].sum()
    num_days_worked = df_copy['date'].nunique()

    if 'week_number' not in df_copy.columns or 'year' not in df_copy.columns:
        # Ensure 'date' column is datetime type
        if not pd.api.types.is_datetime64_any_dtype(df_copy['date']):
             df_copy['date'] = pd.to_datetime(df_copy['date'])
        df_copy['week_number'] = df_copy['date'].dt.isocalendar().week
        df_copy['year'] = df_copy['date'].dt.isocalendar().year
        
    num_weeks_worked = df_copy[['year', 'week_number']].drop_duplicates().shape[0]

    avg_daily_seconds = total_seconds / num_days_worked if num_days_worked > 0 else 0
    avg_weekly_seconds = total_seconds / num_weeks_worked if num_weeks_worked > 0 else 0

    # Billable hours: (Example: jobs containing 'Development' or 'Consulting')
    df_copy['is_billable'] = df_copy['job_name'].astype(str).str.contains('Development|Consulting', case=False, na=False)
    billable_seconds = df_copy[df_copy['is_billable']]['duration_seconds'].sum()
    non_billable_seconds = total_seconds - billable_seconds
    billable_percentage = (billable_seconds / total_seconds * 100) if total_seconds > 0 else 0

    # Overtime hours
    daily_total_seconds = df_copy.groupby(df_copy['date'].dt.date)['duration_seconds'].sum()
    daily_hours = daily_total_seconds / 3600
    daily_overtime_hours = daily_hours[daily_hours > standard_workday_hours].apply(lambda x: x - standard_workday_hours).sum()

    weekly_total_seconds = df_copy.groupby(['year', 'week_number'])['duration_seconds'].sum()
    weekly_hours = weekly_total_seconds / 3600
    weekly_overtime_hours = weekly_hours[weekly_hours > standard_workweek_hours].apply(lambda x: x - standard_workweek_hours).sum()

    job_distribution_seconds = df_copy.groupby('job_name')['duration_seconds'].sum()
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

# --- NEW FUNCTION: Display Performance Analytics Tab ---
def display_performance_analytics_tab(df_timesheets: pd.DataFrame):
    """Displays the employee performance analytics tab with KPIs and charts."""
    st.markdown("<h2 class='section-header'>Employee Performance Analytics</h2>", unsafe_allow_html=True)

    if df_timesheets.empty:
        st.warning("No timesheet data available for the selected period to calculate performance metrics.")
        return

    col1, col2 = st.columns(2)
    with col1:
        standard_workday = st.number_input("Standard Workday Hours", min_value=1.0, max_value=24.0, value=8.0, step=0.5, key="perf_workday")
    with col2:
        standard_workweek = st.number_input("Standard Workweek Hours", min_value=1.0, max_value=168.0, value=40.0, step=1.0, key="perf_workweek")

    metrics = calculate_employee_performance_metrics(df_timesheets, standard_workday_hours=standard_workday, standard_workweek_hours=standard_workweek)

    st.markdown("---_</h3_><h3 class='subsection-header'>Key Performance Indicators (KPIs)</h3>", unsafe_allow_html=True)
    cols_kpi1 = st.columns(3)
    cols_kpi1[0].metric("Total Hours Logged", metrics["total_hours_logged_decimal"] + " hrs", delta=metrics["total_hours_logged_formatted"])
    cols_kpi1[1].metric("Average Daily Hours", metrics["avg_daily_hours_decimal"] + " hrs", help=f"{metrics['num_days_worked']} days worked")
    cols_kpi1[2].metric("Average Weekly Hours", metrics["avg_weekly_hours_decimal"] + " hrs", help=f"{metrics['num_weeks_worked']} weeks worked")

    cols_kpi2 = st.columns(3)
    cols_kpi2[0].metric("Billable Hours", metrics["billable_hours_decimal"] + " hrs", delta=f"{metrics['billable_percentage']}% of Total")
    cols_kpi2[1].metric("Non-Billable Hours", metrics["non_billable_hours_decimal"] + " hrs")
    cols_kpi2[2].metric("Utilization (vs Logged)", f"{metrics['utilization_rate_vs_logged']}%", help="Billable Hours / Total Logged Hours")

    cols_kpi3 = st.columns(3)
    cols_kpi3[0].metric("Daily Overtime", metrics["daily_overtime_hours_decimal"] + " hrs")
    cols_kpi3[1].metric("Weekly Overtime", metrics["weekly_overtime_hours_decimal"] + " hrs")
    cols_kpi3[2].metric("Utilization (vs Standard)", f"{metrics['utilization_rate_vs_standard']}%", help=f"Billable Hours / ({metrics['num_days_worked']} days * {standard_workday} hrs/day)")

    st.markdown("---_</h3_><h3 class='subsection-header'>Work Distribution & Patterns</h3>", unsafe_allow_html=True)
    col_dist1, col_dist2 = st.columns(2)
    with col_dist1:
        st.markdown("<h4>Hours per Job Code</h4>", unsafe_allow_html=True)
        if metrics["job_code_distribution_hours"]:
            job_df_data = [{'Job Code': k, 'Hours': v, 'Percentage': metrics["job_code_distribution_percent"].get(k,0)} for k,v in metrics["job_code_distribution_hours"].items()]
            job_df = pd.DataFrame(job_df_data).sort_values("Hours", ascending=False)
            st.dataframe(job_df, height=300)
            if not job_df.empty:
                fig_job_pie = px.pie(job_df, values='Hours', names='Job Code', title='Job Code Hours Distribution')
                fig_job_pie.update_layout(legend_orientation="h")
                st.plotly_chart(fig_job_pie, use_container_width=True)
        else:
            st.info("No job code data to display.")

    with col_dist2:
        st.metric("Avg. Entries per Day", metrics["avg_entries_per_day"])
        st.metric("Avg. Entries per Week", metrics["avg_entries_per_week"])
        st.markdown("<h4>Billable vs. Non-Billable Hours</h4>", unsafe_allow_html=True)
        billable_data = pd.DataFrame({
            "Category": ["Billable", "Non-Billable"],
            "Hours": [float(metrics["billable_hours_decimal"]), float(metrics["non_billable_hours_decimal"])]
        })
        if billable_data["Hours"].sum() > 0:
            fig_billable_bar = px.bar(billable_data, x="Category", y="Hours", color="Category", title="Billable vs. Non-Billable Hours", text_auto=True)
            fig_billable_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_billable_bar, use_container_width=True)
        else:
            st.info("No billable/non-billable data to display.")

    st.markdown("---_</h3_><h3 class='subsection-header'>Trends Over Time (Last 12 Weeks)</h3>", unsafe_allow_html=True)
    if not df_timesheets.empty and 'week_number' in df_timesheets.columns and 'year' in df_timesheets.columns:
        df_copy = df_timesheets.copy()
        if not pd.api.types.is_datetime64_any_dtype(df_copy['date']):
             df_copy['date'] = pd.to_datetime(df_copy['date'])
        if 'week_number' not in df_copy.columns:
            df_copy['week_number'] = df_copy['date'].dt.isocalendar().week
        if 'year' not in df_copy.columns:
            df_copy['year'] = df_copy['date'].dt.isocalendar().year
            
        weekly_summary = df_copy.groupby(['year', 'week_number'])['duration_seconds'].sum().reset_index()
        weekly_summary['hours'] = weekly_summary['duration_seconds'] / 3600
        weekly_summary['week_label'] = weekly_summary['year'].astype(str) + "-W" + weekly_summary['week_number'].astype(str).str.zfill(2)
        weekly_summary = weekly_summary.sort_values(by='week_label', ascending=True).tail(12)

        if not weekly_summary.empty:
            fig_weekly_trend = px.line(weekly_summary, x='week_label', y='hours', title='Weekly Hours Logged (Last 12 Weeks)', markers=True)
            fig_weekly_trend.update_layout(xaxis_title="Week", yaxis_title="Total Hours")
            st.plotly_chart(fig_weekly_trend, use_container_width=True)
        else:
            st.info("Not enough data for weekly trend chart (need 'week_number' and 'year' in timesheets). Ensure timesheet data is processed correctly.")
    else:
        st.info("Weekly trend data requires 'week_number' and 'year' in timesheet details. Ensure timesheet data is processed by 'get_timesheet_dataframe'.")


# --- NEW FUNCTION: Get Timesheets for Calendar Display ---
def get_timesheets_for_month_display(df_timesheets: pd.DataFrame, year: int, month: int) -> dict:
    """Processes timesheets for a given month and groups them by day for calendar display."""
    if df_timesheets.empty:
        return {}
    
    df_copy = df_timesheets.copy()
    if not pd.api.types.is_datetime64_any_dtype(df_copy['date']):
        df_copy['date'] = pd.to_datetime(df_copy['date'])

    month_timesheets = df_copy[
        (df_copy['date'].dt.year == year) & (df_copy['date'].dt.month == month)
    ]

    entries_by_day = {}
    for index, ts in month_timesheets.iterrows():
        day = ts['date'].day
        if day not in entries_by_day:
            entries_by_day[day] = []
        
        notes_preview = str(ts.get('notes', ''))
        if len(notes_preview) > 50:
            notes_preview = notes_preview[:47] + "..."

        start_time_str = ts['start_time'].strftime('%H:%M') if pd.notnull(ts.get('start_time')) and hasattr(ts['start_time'], 'strftime') else ''
        end_time_str = ts['end_time'].strftime('%H:%M') if pd.notnull(ts.get('end_time')) and hasattr(ts['end_time'], 'strftime') else ''

        entries_by_day[day].append({
            "id": ts['id'],
            "job_name": ts.get('job_name', 'N/A'),
            "duration_formatted": ts.get('duration_formatted', format_duration(ts.get('duration_seconds',0))),
            "notes_preview": notes_preview,
            "start_time_str": start_time_str,
            "end_time_str": end_time_str,
        })
    return entries_by_day

# --- NEW FUNCTION: Display Timesheet Calendar Tab ---
def display_timesheet_calendar_tab(df_timesheets: pd.DataFrame):
    """Displays an interactive monthly calendar with timesheet entries."""
    st.markdown("<h2 class='section-header'>Timesheet Calendar</h2>", unsafe_allow_html=True)

    if 'calendar_current_month_view' not in st.session_state:
        st.session_state.calendar_current_month_view = datetime.now().date().replace(day=1)
    if 'calendar_selected_day_entries' not in st.session_state:
        st.session_state.calendar_selected_day_entries = None
    if 'calendar_selected_date_for_details' not in st.session_state:
        st.session_state.calendar_selected_date_for_details = None

    current_month_view = st.session_state.calendar_current_month_view
    
    cal_col1, cal_col2, cal_col3 = st.columns([1,2,1])
    with cal_col1:
        if st.button("⬅️ Previous Month", key="cal_prev_month"):
            st.session_state.calendar_current_month_view = (current_month_view - timedelta(days=1)).replace(day=1)
            st.session_state.calendar_selected_day_entries = None
            st.session_state.calendar_selected_date_for_details = None
            st.experimental_rerun()
    with cal_col2:
        st.markdown(f"<h3 style='text-align: center;'>{current_month_view.strftime('%B %Y')}</h3>", unsafe_allow_html=True)
    with cal_col3:
        if st.button("Next Month ➡️", key="cal_next_month"):
            st.session_state.calendar_current_month_view = (current_month_view + timedelta(days=32)).replace(day=1)
            st.session_state.calendar_selected_day_entries = None
            st.session_state.calendar_selected_date_for_details = None
            st.experimental_rerun()
            
    st.markdown("---_</h3_>")

    month_entries = get_timesheets_for_month_display(df_timesheets, current_month_view.year, current_month_view.month)
    
    cal_obj = calendar.Calendar()
    month_days_cal = cal_obj.monthdayscalendar(current_month_view.year, current_month_view.month)
    
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    cols_weekdays = st.columns(7)
    for i, day_name in enumerate(days_of_week):
        cols_weekdays[i].markdown(f"<div class='calendar-weekday'>{day_name}</div>", unsafe_allow_html=True)

    for week_row in month_days_cal:
        cols_days = st.columns(7)
        for i, day_num in enumerate(week_row):
            with cols_days[i]:
                if day_num == 0:
                    st.markdown("<div class='calendar-day other-month' style='height: 80px; text-align: center; padding: 5px; border: 1px solid #eee;'>&nbsp;</div>", unsafe_allow_html=True)
                else:
                    day_date_obj = date(current_month_view.year, current_month_view.month, day_num)
                    day_html_class = "calendar-day"
                    if day_date_obj == datetime.now().date(): day_html_class += " today"
                    if day_num in month_entries: day_html_class += " has-entries"
                    if st.session_state.get('calendar_selected_date_for_details') == day_date_obj: day_html_class += " selected"

                    button_label = str(day_num)
                    button_key = f"day_btn_{current_month_view.year}_{current_month_view.month}_{day_num}"
                    
                    # Construct HTML for the button content for better display control
                    day_display_content = f"{day_num}<br>"
                    if day_num in month_entries:
                        day_display_content += f"<span style='font-size:0.7em; color: #555;'>{len(month_entries[day_num])} entr{'y' if len(month_entries[day_num]) == 1 else 'ies'}</span>"
                    else:
                        day_display_content += "<span style='font-size:0.7em;'>&nbsp;</span>"

                    # Using st.markdown to create a styled, clickable div as Streamlit buttons are hard to style extensively
                    # This is a common workaround: use markdown + query_params or session_state for click handling
                    # For simplicity with existing CSS, we'll try to make the button itself the styled container.
                    # The user's CSS for `.calendar-day` needs to be effective on `.stButton button` or its parent.
                    # We will use a simple button and rely on the CSS being general enough.
                    # Or, provide a container with the class around the button.
                    st.markdown(f"<div class='{day_html_class}' style='height: 80px; text-align: center; padding: 5px; border: 1px solid #eee; border-radius: 5px;'>", unsafe_allow_html=True)
                    if st.button(button_label, key=button_key, help=f"View entries for {day_date_obj.strftime('%B %d, %Y')}"):
                        st.session_state.calendar_selected_date_for_details = day_date_obj
                        st.session_state.calendar_selected_day_entries = month_entries.get(day_num, [])
                        # No rerun here, let the details section update below based on session_state
                        # st.experimental_rerun() # Rerun can be disruptive if overused.
                    st.markdown(day_display_content.replace(f"{day_num}<br>",""), unsafe_allow_html=True) # Display entry count below button
                    st.markdown("</div>", unsafe_allow_html=True)
                        
    st.markdown("---_</h3_>")
    if st.session_state.calendar_selected_date_for_details:
        selected_date_str = st.session_state.calendar_selected_date_for_details.strftime("%A, %B %d, %Y")
        st.markdown(f"<h3 class='subsection-header'>Entries for {selected_date_str}</h3>", unsafe_allow_html=True)
        
        selected_entries = st.session_state.calendar_selected_day_entries
        if selected_entries:
            for entry in selected_entries:
                with st.expander(f"{entry['job_name']} - {entry['duration_formatted']}"):
                    st.markdown(f"**Job:** {entry['job_name']}")
                    st.markdown(f"**Duration:** {entry['duration_formatted']}")
                    if entry['start_time_str'] and entry['end_time_str']:
                        st.markdown(f"**Time:** {entry['start_time_str']} - {entry['end_time_str']}")
                    st.markdown(f"**Notes:** {entry['notes_preview']}")
                    # Add a button to view full timesheet details if needed (links to main timesheet editor)
        elif st.session_state.calendar_selected_date_for_details:
             st.info("No timesheet entries for this day.")
    else:
        st.info("Click on a day in the calendar to view its timesheet entries.")


# --- TAB INTEGRATION EXAMPLE --- 
"""
Locate the section in your main script where Streamlit tabs or navigation is handled.
It might look something like this (this is an illustrative example):

# if st.session_state.authenticated:
#   # --- MODIFICATION START ---
#   # Original tabs:
#   # main_tabs = ["Dashboard", "Timesheets", "Analytics", "Clients", "Reports", "Settings"]
#   # New tabs:
#   main_tabs = ["Dashboard", "Timesheets", "Timesheet Calendar", 
#                "Analytics", "Performance Analytics", "Clients", "Reports", "Settings"]
#   
#   if 'active_tab' not in st.session_state or st.session_state.active_tab not in main_tabs:
#       st.session_state.active_tab = "Dashboard"
# 
#   st.session_state.active_tab = st.sidebar.radio(
#       "Navigation", 
#       main_tabs, 
#       index=main_tabs.index(st.session_state.active_tab),
#       key="navigation_radio"
#   )
#   # --- MODIFICATION END ---
# 
#   # Ensure timesheet_df is available. It's usually generated after loading timesheets.
#   # timesheet_df = get_timesheet_dataframe(st.session_state.timesheets) 
# 
#   if st.session_state.active_tab == "Dashboard":
#       display_dashboard(timesheet_df) # Assuming this function exists
#   elif st.session_state.active_tab == "Timesheets":
#       display_timesheets_manager(timesheet_df) # Assuming this function exists
#   # --- NEW TAB HANDLING START ---
#   elif st.session_state.active_tab == "Timesheet Calendar":
#       display_timesheet_calendar_tab(timesheet_df) # Pass the timesheet_df
#   # --- NEW TAB HANDLING END ---
#   elif st.session_state.active_tab == "Analytics":
#       display_timesheet_analytics(timesheet_df) # Assuming this function exists (original analytics)
#   # --- NEW TAB HANDLING START ---
#   elif st.session_state.active_tab == "Performance Analytics":
#       display_performance_analytics_tab(timesheet_df) # Pass the timesheet_df
#   # --- NEW TAB HANDLING END ---
#   elif st.session_state.active_tab == "Clients":
#       display_clients_tab() # Assuming this function exists
#   # ... and so on for other existing tabs

"""
