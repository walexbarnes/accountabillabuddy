import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Accountabillabuddy")

# App title and configuration
logger.info("Starting Accountabillabuddy app")
st.set_page_config(
    page_title="Daily Activity Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define data directory - use /data on Render, or current directory locally
is_render = os.environ.get('RENDER', 'false').lower() == 'true'
DATA_DIR = os.environ.get('DATA_DIR', '/data' if is_render else '.')

# Create a dedicated subfolder for data files
DATA_FOLDER = os.path.join(DATA_DIR, 'data')
TRACKER_FILE = os.path.join(DATA_FOLDER, 'Tracker.csv')

logger.info(f"Running on Render: {is_render}")
logger.info(f"Using DATA_DIR: {DATA_DIR}")
logger.info(f"Using DATA_FOLDER: {DATA_FOLDER}")
logger.info(f"Using TRACKER_FILE path: {TRACKER_FILE}")

# Check for disk configuration issues
if is_render and DATA_DIR == '.':
    logger.warning("WARNING: Running on Render but DATA_DIR is set to current directory!")
    logger.warning("This means disk persistence may not be working correctly.")
    logger.warning("Check that you've added the DATA_DIR environment variable and configured the disk in Render.")

# Ensure the data directory and folder exist
logger.info(f"Checking if data directory exists: {DATA_DIR}")
if not os.path.exists(DATA_DIR):
    logger.info(f"Creating data directory: {DATA_DIR}")
    os.makedirs(DATA_DIR, exist_ok=True)
else:
    logger.info(f"Data directory already exists: {DATA_DIR}")

# Ensure data subfolder exists
logger.info(f"Checking if data subfolder exists: {DATA_FOLDER}")
if not os.path.exists(DATA_FOLDER):
    logger.info(f"Creating data subfolder: {DATA_FOLDER}")
    os.makedirs(DATA_FOLDER, exist_ok=True)
else:
    logger.info(f"Data subfolder already exists: {DATA_FOLDER}")
    
# Log directory contents
try:
    dir_contents = os.listdir(DATA_DIR)
    logger.info(f"Contents of {DATA_DIR}: {dir_contents}")
    
    if os.path.exists(DATA_FOLDER):
        folder_contents = os.listdir(DATA_FOLDER)
        logger.info(f"Contents of {DATA_FOLDER}: {folder_contents}")
except Exception as e:
    logger.error(f"Error listing directory contents: {e}")

# Function to load data
@st.cache_data(ttl=10, show_spinner=False)  # Cache data for 10 seconds only and hide spinner
def load_data():
    logger.info(f"Attempting to load data from {TRACKER_FILE}")
    
    # Check for data in old location and migrate if needed
    old_tracker_file = os.path.join(DATA_DIR, 'Tracker.csv')
    if os.path.exists(old_tracker_file) and not os.path.exists(TRACKER_FILE):
        logger.info(f"Found data in old location: {old_tracker_file}")
        logger.info(f"Migrating data to new location: {TRACKER_FILE}")
        try:
            # Read from old location
            old_df = pd.read_csv(old_tracker_file)
            # Save to new location
            old_df.to_csv(TRACKER_FILE, index=False)
            logger.info(f"Data successfully migrated from {old_tracker_file} to {TRACKER_FILE}")
            # Optionally, create a backup of the old file
            backup_file = os.path.join(DATA_DIR, 'Tracker.csv.bak')
            import shutil
            shutil.copy2(old_tracker_file, backup_file)
            logger.info(f"Created backup of old file at {backup_file}")
        except Exception as e:
            logger.error(f"Error migrating data: {e}")
    
    if os.path.exists(TRACKER_FILE):
        logger.info(f"File exists, reading from {TRACKER_FILE}")
        try:
            df = pd.read_csv(TRACKER_FILE)
            logger.info(f"Successfully loaded data with shape: {df.shape}")
            if 'Date' in df.columns:
                logger.info("Converting date column to proper format")
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            logger.info(f"First few rows: {df.head().to_dict()}")
            return df
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            return pd.DataFrame(columns=['Date', 'Meditation', 'Exercise', 'Frankie', 'Harrison', 'Madi', 
                          'THC', 'Diet', 'Screen', 'Productive', 'Vibe'])
    else:
        logger.info(f"File does not exist: {TRACKER_FILE}")
        # Create a new DataFrame with the correct columns if file doesn't exist
        columns = ['Date', 'Meditation', 'Exercise', 'Frankie', 'Harrison', 'Madi', 
                  'THC', 'Diet', 'Screen', 'Productive', 'Vibe']
        logger.info(f"Creating new DataFrame with columns: {columns}")
        return pd.DataFrame(columns=columns)

# Function to save data
def save_data(df):
    logger.info(f"Attempting to save data to {TRACKER_FILE}")
    logger.info(f"DataFrame shape: {df.shape}")
    logger.info(f"First few rows to save: {df.head().to_dict()}")
    
    try:
        # Get the directory of the file to create it if necessary
        file_dir = os.path.dirname(TRACKER_FILE)
        if file_dir and not os.path.exists(file_dir):
            logger.info(f"Creating directory: {file_dir}")
            os.makedirs(file_dir, exist_ok=True)
        
        # Save the DataFrame to the CSV file
        df.to_csv(TRACKER_FILE, index=False)
        logger.info(f"Successfully saved data to {TRACKER_FILE}")
        
        # Verify the file was created
        if os.path.exists(TRACKER_FILE):
            file_size = os.path.getsize(TRACKER_FILE)
            logger.info(f"File saved with size: {file_size} bytes")
            
            # Read the first few lines to verify
            with open(TRACKER_FILE, 'r') as f:
                first_few_lines = [next(f) for _ in range(min(5, len(df) + 1))]
            logger.info(f"File contents verification (first few lines): {first_few_lines}")
        else:
            logger.error(f"File was not created at {TRACKER_FILE}")
        
        # Invalidate the cache to force reload
        load_data.clear()
        logger.info("Cache cleared for data reload")
        return True
    except Exception as e:
        logger.error(f"Error saving data: {e}")
        return False

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
    /* Ensure proper column layout on all devices */
    @media screen and (max-width: 768px) {
        /* Force 3 columns layout */
        [data-testid="column"] {
            flex: 0 0 33.33% !important;
            width: 33.33% !important;
            min-width: 33.33% !important;
        }
        /* Make input fields and text smaller on mobile */
        .stNumberInput input, .stSelectbox, .stSlider {
            font-size: 14px !important;
        }
        [data-testid="stVerticalBlock"] {
            gap: 0.5rem !important;
        }
    }
</style>
""", unsafe_allow_html=True)

# Load data
logger.info("Loading initial data")
df = load_data()
logger.info(f"Initial data loaded with {len(df)} rows")

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

    # Create columns for the form - always use 3 columns for better mobile layout
    num_cols = 3  # Fixed to 3 columns for consistent layout on all devices
    cols = st.columns(num_cols)
    col_idx = 0

    for category, props in categories.items():
        with cols[col_idx]:
            if props['type'] == 'integer':
                default_val = int(existing_data[category]) if existing_data[category] and pd.notna(existing_data[category]) else 0
                new_data[category] = st.number_input(
                    f"{category} (min)" if 'unit' in props and props['unit'] == 'minutes' else f"{category}", 
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
        logger.info(f"Save button clicked for date: {selected_date_str}")
        # Find changed fields by comparing with original values
        changed_fields = []
        
        if has_data_for_date:
            logger.info(f"Updating existing data for date: {selected_date_str}")
            original = st.session_state.original_values[selected_date_str]
            logger.info(f"Original values: {original}")
            logger.info(f"New values: {new_data}")
            
            for category in categories.keys():
                original_value = original.get(category)
                new_value = new_data.get(category)
                logger.info(f"Comparing '{category}': original={original_value}, new={new_value}")
                
                # For empty or NaN values in original, convert to appropriate default
                if not original_value or pd.isna(original_value):
                    if categories[category]['type'] == 'integer':
                        original_value = 0
                    elif categories[category]['type'] == 'enum':
                        original_value = categories[category]['values'][0]
                    elif categories[category]['type'] == 'slider':
                        original_value = categories[category]['min']
                    logger.info(f"  Converted empty/NaN original value to default: {original_value}")
                
                # Convert both to same type for comparison
                if categories[category]['type'] in ['integer', 'slider']:
                    if original_value and not pd.isna(original_value):
                        original_value = int(original_value)
                    else:
                        original_value = 0
                    logger.info(f"  Converted to integer for comparison: {original_value}")
                
                # Check if value has changed
                if new_value != original_value and not pd.isna(new_value):
                    changed_fields.append(category)
                    logger.info(f"  *** Value changed for '{category}': {original_value} -> {new_value}")
            
            # Update only the changed fields
            if changed_fields:
                logger.info(f"Fields changed: {changed_fields}")
                for category in changed_fields:
                    logger.info(f"Updating '{category}' to {new_data[category]}")
                    df.loc[df['Date'] == selected_date_str, category] = new_data[category]
                
                # Save the updated DataFrame
                logger.info("Saving updated data")
                save_success = save_data(df)
                logger.info(f"Save result: {'Success' if save_success else 'Failed'}")
                
                # Update original values after saving
                st.session_state.original_values[selected_date_str] = get_data_for_date(df, selected_date_str).copy()
                logger.info(f"Updated original values in session state")
                
                # Show success message
                updated_fields = ", ".join(changed_fields)
                logger.info(f"Displaying success message for updated fields: {updated_fields}")
                message_container.success(f"Updated fields for {selected_date_str}: {updated_fields}")
                
                # Set the just_saved flag
                st.session_state.just_saved = True
            else:
                # If no fields were changed, don't update anything
                logger.info("No fields were changed, not saving")
                message_container.info("No changes detected. No fields were updated.")
        else:
            logger.info(f"Creating new entry for date: {selected_date_str}")
            logger.info(f"New data: {new_data}")
            
            # For new entries, add the entire row
            df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
            logger.info(f"Added new row to DataFrame, new shape: {df.shape}")
            
            # Save the updated DataFrame
            logger.info("Saving DataFrame with new row")
            save_success = save_data(df)
            logger.info(f"Save result: {'Success' if save_success else 'Failed'}")
            
            # Store the new values as original values
            st.session_state.original_values[selected_date_str] = new_data.copy()
            logger.info(f"Updated original values in session state")
            
            # Show success message
            logger.info(f"Displaying success message for new entry")
            message_container.success(f"New entry created for {selected_date_str}")
            
            # Set the just_saved flag
            st.session_state.just_saved = True
        
        # Reload data to ensure latest changes are visible
        logger.info("Reloading data to refresh display")
        df = load_data()
        has_data_for_date = data_exists_for_date(df, selected_date_str)
        logger.info(f"Data reloaded, has_data_for_date: {has_data_for_date}")

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
    
    # Add export button for the full CSV file
    if os.path.exists(TRACKER_FILE):
        logger.info(f"Creating export button for file: {TRACKER_FILE}")
        try:
            with open(TRACKER_FILE, 'r') as f:
                csv_contents = f.read()
            logger.info(f"File read successfully for export, size: {len(csv_contents)} bytes")
            logger.info(f"File preview (first 100 chars): {csv_contents[:100]}")
            st.download_button(
                label="Export Full CSV Data",
                data=csv_contents,
                file_name="Tracker.csv",
                mime="text/csv"
            )
            logger.info("Export button created successfully")
        except Exception as e:
            logger.error(f"Error creating export button: {e}")
            st.error(f"Could not create export button: {e}")
    else:
        st.info("No recent activity data available.") 