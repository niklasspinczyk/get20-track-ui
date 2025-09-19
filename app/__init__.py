from flask import Flask, render_template
import json
import os

app = Flask(__name__)

# Load configuration from a JSON file if needed
if os.path.exists('data/database.json'):
    with open('data/database.json', 'r') as f:
        data = json.load(f)
else:
    data = {
        "teams": [],
        "drivers": [],
        "vehicles": []
    }
from app.routes import init as init_blueprint
init_blueprint()

from app.routes import app as routes_blueprint
app.register_blueprint(routes_blueprint)
