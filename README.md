# Track Marshal Application

This is a Flask web application designed for track marshals to enter and manage information about drivers, vehicles, and teams.

## Project Structure

```
track-marshal-app
├── app
│   ├── __init__.py          # Initializes the Flask application
│   ├── routes.py            # Defines the routes for the web application
│   ├── models.py            # Contains data models for Team, Driver, and Vehicle
│   ├── static               # Directory for static files (CSS, JS, images)
│   └── templates
│       └── index.html       # Main HTML template for the user interface
├── data
│   └── database.json        # JSON file to store data about teams, vehicles, and drivers
├── requirements.txt         # Lists the dependencies required for the application
└── README.md                # Documentation for the project
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd track-marshal-app
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

- Navigate to `http://127.0.0.1:5000` in your web browser to access the application.
- Use the interface to enter information about drivers, vehicles, and teams.

## Contributing

Contributions are welcome! Please submit a pull request or open an issue for any suggestions or improvements.