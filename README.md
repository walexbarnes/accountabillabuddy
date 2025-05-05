# Accountabillabuddy: Daily Activity Tracker

A responsive web application to track daily activities and metrics, built with Streamlit. The app allows users to update their daily logs throughout the day from both mobile and desktop devices, with data stored in a CSV file.

## Features

- Track multiple daily metrics (meditation, exercise, social interactions, etc.)
- Mobile-friendly interface with individual activity cards
- Desktop interface with tabular data entry
- Date selection to view and edit past entries
- Visual indicators for days with existing data
- Recent activity overview

## Setup Instructions

### Prerequisites

- Python 3.7+ installed
- pip (Python package manager)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/accountabillabuddy.git
   cd accountabillabuddy
   ```

2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Running the App Locally

Run the Streamlit app:
```
streamlit run app.py
```

The app will be available at http://localhost:8501 in your web browser.

## Deployment on Render

The app can be deployed on [Render](https://render.com) by following these steps:

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Configure the service with:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py`
   - Select a Python 3 environment
4. For data persistence, add a disk:
   - Mount path: `/data` 
   - Size: 1GB (minimum size, can be increased later)

The app is configured to automatically detect and use the mounted disk path on Render for data storage, while still working correctly on your local machine.

## Data Structure

The application uses a CSV file (Tracker.csv) with the following columns:

- **Date**: YYYY-MM-DD format
- **Meditation**: Integer (minutes)
- **Exercise**: Integer (minutes)
- **Frankie**: Integer (minutes spent with Frankie)
- **Harrison**: Integer (minutes spent with Harrison)
- **Madi**: Integer (minutes spent with Madi)
- **THC**: String enum ("bad", "neutral", "good")
- **Diet**: String enum ("bad", "neutral", "good")
- **Screen**: Integer (minutes)
- **Productive**: Integer (minutes)
- **Vibe**: Integer (1-10 scale)

## Usage

1. When you open the app, it defaults to the current date
2. Update metrics for the day:
   - On desktop, fill out the form and click "Save All"
   - On mobile, update individual cards and click "Save" on each card
3. Use the date selector to view or update past entries
4. The "Recent Activity" section shows your 5 most recent entries

## Deployment Options

### Streamlit Community Cloud
You can deploy this app on Streamlit Community Cloud, but be aware that file-based storage (CSV) will not persist between app restarts. Data entered will be lost when the app restarts.

### Render
The repository includes configuration for deploying on Render with persistent storage:
- The `render.yaml` file configures a 1GB persistent disk mounted at `/data`
- The app is set up to automatically store data in this persistent location
- This ensures your data persists between app restarts and deployments

For deployment:
1. On Render dashboard, create a new Web Service from your repository
2. Use the Blueprint configuration (which will use our render.yaml settings)
3. Select a paid plan to enable persistent disk storage
4. No additional configuration is needed - the app will handle the storage path automatically

### Alternative Solutions
For better data persistence in cloud environments:
1. Use a database backend (SQLite, PostgreSQL, etc.)
2. Integrate with cloud storage (AWS S3, Google Cloud Storage, etc.)
3. Use GitHub as a data store (requires additional implementation)

## Usage

1. Select the date
2. Enter your daily metrics
3. Click "Save" to record your data 