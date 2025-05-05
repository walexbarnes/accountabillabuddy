import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# App title and configuration
st.set_page_config(
    page_title="Daily Activity Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Function to load data
@st.cache_data(ttl=10, show_spinner=False)  # Cache data for 10 seconds only and hide spinner
def load_data():
    if os.path.exists('Tracker.csv'):
        df = pd.read_csv('Tracker.csv')
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
        return df
    else:
        # Create a new DataFrame with the correct columns if file doesn't exist
        columns = ['Date', 'Meditation', 'Exercise', 'Frankie', 'Harrison', 'Madi', 
                  'THC', 'Diet', 'Screen', 'Productive', 'Vibe']
        return pd.DataFrame(columns=columns)

# Function to save data
def save_data(df):
    df.to_csv('Tracker.csv', index=False)
    # Invalidate the cache to force reload
    load_data.clear()
    return True

# Function to check if data exists for a specific date
def data_exists_for_date(df, date_str):
    return date_str in df['Date'].values

# Function to get data for a specific date
def get_data_for_date(df, date_str):
    if data_exists_for_date(df, date_str):
        return df[df['Date'] == date_str].iloc[0].to_dict()
    else:
        return {col: '' for col in df.columns}

# Initialize session state for storing original values
if 'original_values' not in st.session_state:
    st.session_state.original_values = {}

# For tracking if data was just saved
if 'just_saved' not in st.session_state:
    st.session_state.just_saved = False

# Custom CSS for styling
st.markdown("""
<style>
    .main-form {
        display: flex;
        flex-direction: column;
    }
    .data-indicator {
        background-color: #4CAF50;
        color: white;
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 0.8em;
        margin-left: 10px;
    }
    .stButton > button {
        width: 100%;
    }
    /* Make form responsive on all devices */
    @media screen and (max-width: 768px) {
        .st-emotion-cache-16txtl3 { /* Target Streamlit column containers */
            flex: 0 0 100% !important;
            width: 100% !important;
            margin-bottom: 10px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load data
df = load_data()

# Get today's date in YYYY-MM-DD format
today = datetime.now().strftime('%Y-%m-%d')

# Title
st.title("Daily Activity Tracker")

# Date selection container at the top
date_col1, date_col2 = st.columns([1, 3])
with date_col1:
    st.write("Select Date:")

with date_col2:
    selected_date = st.date_input("", 
                                 value=datetime.now(), 
                                 key="date_selector",
                                 label_visibility="collapsed")
    selected_date_str = selected_date.strftime('%Y-%m-%d')

# Initialize empty dictionary for new data
new_data = {'Date': selected_date_str}

# Check if we already have data for this date
existing_data = get_data_for_date(df, selected_date_str)
has_data_for_date = data_exists_for_date(df, selected_date_str)

# Store original values when date changes
if selected_date_str not in st.session_state.original_values:
    st.session_state.original_values[selected_date_str] = existing_data.copy()

# Create a container for feedback messages
message_container = st.empty()

# Define categories and their properties
categories = {
    'Meditation': {'type': 'integer', 'unit': 'minutes'},
    'Exercise': {'type': 'integer', 'unit': 'minutes'},
    'Frankie': {'type': 'integer', 'unit': 'minutes'},
    'Harrison': {'type': 'integer', 'unit': 'minutes'},
    'Madi': {'type': 'integer', 'unit': 'minutes'},
    'THC': {'type': 'enum', 'values': ['bad', 'neutral', 'good']},
    'Diet': {'type': 'enum', 'values': ['bad', 'neutral', 'good']},
    'Screen': {'type': 'integer', 'unit': 'minutes'},
    'Productive': {'type': 'integer', 'unit': 'minutes'},
    'Vibe': {'type': 'slider', 'min': 1, 'max': 10}
}

# Main Form View
st.markdown('<div class="main-form">', unsafe_allow_html=True)

form = st.form("data_form", clear_on_submit=False)

with form:
    st.subheader(f"Data for {selected_date_str}")

    if has_data_for_date:
        st.markdown('<span class="data-indicator">Data Exists</span>', unsafe_allow_html=True)

    # Create columns for the form - adjust number based on screen size
    num_cols = 3  # Reduced from 5 for better readability on all devices
    cols = st.columns(num_cols)
    col_idx = 0

    for category, props in categories.items():
        with cols[col_idx]:
            if props['type'] == 'integer':
                default_val = int(existing_data[category]) if existing_data[category] and pd.notna(existing_data[category]) else 0
                new_data[category] = st.number_input(
                    f"{category} ({props['unit']})", 
                    min_value=0, 
                    value=default_val,
                    step=1,
                    key=f"form_{category}"
                )
            
            elif props['type'] == 'enum':
                default_val = existing_data[category] if existing_data[category] and pd.notna(existing_data[category]) else props['values'][0]
                default_idx = props['values'].index(default_val) if default_val in props['values'] else 0
                new_data[category] = st.selectbox(
                    category, 
                    options=props['values'],
                    index=default_idx,
                    key=f"form_{category}"
                )
            
            elif props['type'] == 'slider':
                default_val = int(existing_data[category]) if existing_data[category] and pd.notna(existing_data[category]) else props['min']
                new_data[category] = st.slider(
                    category, 
                    min_value=props['min'], 
                    max_value=props['max'],
                    value=default_val,
                    key=f"form_{category}"
                )
        
        col_idx = (col_idx + 1) % num_cols

    # Submit button
    submit_button = st.form_submit_button("Save All")

    if submit_button:
        # Find changed fields by comparing with original values
        changed_fields = []
        
        if has_data_for_date:
            original = st.session_state.original_values[selected_date_str]
            for category in categories.keys():
                original_value = original.get(category)
                new_value = new_data.get(category)
                # For empty or NaN values in original, convert to appropriate default
                if not original_value or pd.isna(original_value):
                    if categories[category]['type'] == 'integer':
                        original_value = 0
                    elif categories[category]['type'] == 'enum':
                        original_value = categories[category]['values'][0]
                    elif categories[category]['type'] == 'slider':
                        original_value = categories[category]['min']
                
                # Convert both to same type for comparison
                if categories[category]['type'] in ['integer', 'slider']:
                    if original_value and not pd.isna(original_value):
                        original_value = int(original_value)
                    else:
                        original_value = 0
                
                # Check if value has changed
                if new_value != original_value and not pd.isna(new_value):
                    changed_fields.append(category)
            
            # Update only the changed fields
            if changed_fields:
                for category in changed_fields:
                    df.loc[df['Date'] == selected_date_str, category] = new_data[category]
                
                # Save the updated DataFrame
                save_data(df)
                
                # Update original values after saving
                st.session_state.original_values[selected_date_str] = get_data_for_date(df, selected_date_str).copy()
                
                # Show success message
                updated_fields = ", ".join(changed_fields)
                message_container.success(f"Updated fields for {selected_date_str}: {updated_fields}")
                
                # Set the just_saved flag
                st.session_state.just_saved = True
            else:
                # If no fields were changed, don't update anything
                message_container.info("No changes detected. No fields were updated.")
        else:
            # For new entries, add the entire row
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            
            # Save the updated DataFrame
            save_data(df)
            
            # Store the new values as original values
            st.session_state.original_values[selected_date_str] = new_data.copy()
            
            # Show success message
            message_container.success(f"New entry created for {selected_date_str}")
            
            # Set the just_saved flag
            st.session_state.just_saved = True
        
        # Reload data to ensure latest changes are visible
        df = load_data()
        has_data_for_date = data_exists_for_date(df, selected_date_str)

st.markdown('</div>', unsafe_allow_html=True)

# Display recent days at the bottom
st.subheader("Recent Activity")
if not df.empty and 'Date' in df.columns:
    # Force refresh data if we just saved
    if st.session_state.just_saved:
        df = load_data()
        st.session_state.just_saved = False
    
    recent_df = df.sort_values(by='Date', ascending=False).head(5)
    st.dataframe(recent_df, use_container_width=True)
else:
    st.info("No recent activity data available.") 