!!! THIS IS VIBECODED !!!

Don't ask.

See get-racing.de/get20

# Track Marshal Application

This is a Flask web application designed for track marshals to assign drivers to vehicles for specific runs, manage teams, and configure contest settings. The app communicates with a Race Result 12 server and stores all data in JSON files.

## Project Structure

```
get20-track-ui
├── app
│   ├── __init__.py          # Initializes the Flask application and registers routes
│   ├── routes.py            # Defines the routes and API endpoints for the web application
│   ├── static               # Directory for static files (CSS, JS, images)
│   └── templates
│       ├── index.html       # Main HTML template for the user interface
│       └── admin.html       # Admin panel for contest configuration
├── data
│   ├── database.json        # JSON file to store data about teams and vehicles
│   └── admin.json           # JSON file to store admin settings (e.g., contest id)
├── requirements.txt         # Lists the dependencies required for the application
└── README.md                # Documentation for the project
```

## Features

- **Assign drivers to vehicles for a specific run** using a mobile-friendly web UI.
- **Edit teams and drivers**: Add drivers to teams via a collapsible admin pane.
- **Contest configuration**: Set the active contest via the `/admin` panel; the contest id is stored in `data/admin.json`.
- **REST API integration**: Assignments trigger a REST call to a Race Result 12 server.
- **All data is stored in JSON files** for easy backup and editing.

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd get20-track-ui
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```
   flask run
   ```

## Usage

- Navigate to `http://127.0.0.1:5000` in your web browser to access the main application.
- Use the main interface to assign drivers to vehicles for a run.
- Use the collapsible pane to add drivers to teams.
- Visit `/admin` to set the active contest.
