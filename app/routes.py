from flask import Blueprint, request, jsonify, render_template
import os
import json
import requests
import threading
import time

app = Blueprint('app', __name__)

DATA_FILE = os.path.join('data', 'database.json')
RACE_RESULT_BASE_URL = "http://192.168.0.58:4880/"  # <-- Set your real Race Result server URL here
CONTESTS = {
    {
        "name": "AutoX",
        "id": 1
    }
}

CONTEST_ID = 1


start_number_counter = -1


def fetch_run_counter():
    global start_number_counter

    url = f'http://192.168.0.58:4880/_UPFPQ/api/data/list?lang=en&fields=%5B%22ID%22%2C%22BIB%22%2C%22LASTNAME%22%2C%22FIRSTNAME%22%2C%22CONTEST.NAME%22%5D&filter=matchName(%22%22)&filterbib=0&filtercontest=0&filtersex=&sort=BIB&listformat=jSON&pw=0'
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    raw_data = resp.json()

    start_number_counter = max(raw_data, key=lambda l: l[1])

threading.Thread(target=fetch_run_counter, daemon=True).start()


def add_run(id, vehicle, team, driver, transponder):
    url_new = f'http://192.168.0.58:4880/_UPFPQ/api/part/new?lang=en&firstfree=0&bib={id}&v2=true&pw=0'
    url_create = f'http://192.168.0.58:4880/_UPFPQ/api/part/savefields?lang=en&pid=41&nohistory=1&pw=0'
    data_create = {"Bib":str(id),"Lastname":"","Firstname":driver,"Title":"","DateOfBirth":"","Sex":"","Contest":str(CONTEST_ID),"AgeGroup1":"0","Club":team,"Status":"0","Comment":"","TeamStatus":""}
    url_assign_t = f''
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    raw_data = resp.json()
    vehicles = []
    for line in raw_data:
        vehicles.append({
            'run_id': line[1]
        })


def load_data():
    if not os.path.exists(DATA_FILE):
        return {"teams": [], "vehicles": []}
    with open(DATA_FILE, 'r') as file:
        return json.load(file)

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=2)


@app.route("/")
def index():
    data = load_data()
    teams = data.get("teams", [])
    vehicles = data.get("vehicles", [])
    return render_template("index.html", teams=teams, vehicles=vehicles)

@app.route("/data")
def get_data():
    return load_data()

@app.route('/assign', methods=['POST'])
def assign_driver_to_vehicle():
    # expects: team (name), driver (name), vehicle (name)
    assignment = request.json
    team_name = assignment.get("team")
    driver = assignment.get("driver")
    vehicle_name = assignment.get("vehicle")

    # Increment run counter
    run_id = start_number_counter
    start_number_counter += 1

    # Find team and vehicle remote_ids and transponder
    data = load_data()
    team = next((t for t in data["teams"] if t["name"] == team_name), None)
    vehicle = next((v for v in data["vehicles"] if v["name"] == vehicle_name), None)
    if not team or not vehicle:
        return jsonify({"error": "Team or vehicle not found"}), 400

    payload = {
        "run_id": run_id,
        "team_remote_id": team.get("remote_id", team["name"]),
        "vehicle_remote_id": vehicle.get("remote_id", vehicle["name"]),
        "vehicle_transponder": vehicle["transponder"],
        "driver": driver
    }

    # Push to Race Result server
    try:
        rr_resp = requests.post(RACE_RESULT_URL, json=payload, timeout=5)
        rr_resp.raise_for_status()
    except Exception as e:
        return jsonify({"error": "Failed to push to Race Result server", "details": str(e)}), 502

    return jsonify({"message": "Assignment sent!", "assignment": payload}), 200


@app.route('/add_driver', methods=['POST'])
def add_driver():
    req = request.get_json()
    team_name = req.get('team')
    driver_name = req.get('driver')
    if not team_name or not driver_name:
        return jsonify({"success": False, "error": "Missing team or driver"}), 400

    data = load_data()
    team = next((t for t in data['teams'] if t['name'] == team_name), None)
    if not team:
        return jsonify({"success": False, "error": "Team not found"}), 404

    if 'drivers' not in team:
        team['drivers'] = []
    if driver_name in team['drivers']:
        return jsonify({"success": False, "error": "Driver already assigned to team"}), 400

    team['drivers'].append(driver_name)
    save_data(data)
    return jsonify({"success": True}), 200