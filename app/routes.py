from flask import Blueprint, request, jsonify, render_template
import os
import json
import requests
import threading
import time
from pprint import pprint

app = Blueprint('app', __name__)

DATA_FILE = os.path.join('data', 'database.json')
RACE_RESULT_BASE_URL = "http://192.168.0.58:4880"  # <-- Set your real Race Result server URL here
CONTESTS = [
    {
        "name": "AutoX",
        "id": 1
    }
]

CONTEST_ID = 1


start_number_counter = -1


def fetch_run_counter():
    global start_number_counter

    url = f'{RACE_RESULT_BASE_URL}/_UPFPQ/api/data/list?lang=en&fields=%5B%22ID%22%2C%22BIB%22%2C%22LASTNAME%22%2C%22FIRSTNAME%22%2C%22CONTEST.NAME%22%5D&filter=matchName(%22%22)&filterbib=0&filtercontest=0&filtersex=&sort=BIB&listformat=jSON&pw=0'
    resp = requests.get(url, timeout=5)
    resp.raise_for_status()
    raw_data = resp.json()

    start_number_counter = max(raw_data, key=lambda l: l[1])[1] + 1

threading.Thread(target=fetch_run_counter, daemon=True).start()


def add_run(id, vehicle, team, driver, transponder):
    url_new = f'{RACE_RESULT_BASE_URL}/_UPFPQ/api/part/new?lang=en&firstfree=0&bib={id}&v2=true&pw=0'
    data_create = {"Bib":str(id),"Lastname":vehicle,"Firstname":driver,"Title":"","DateOfBirth":"","Sex":"","Contest":str(CONTEST_ID),"AgeGroup1":"0","Club":team,"Status":"0","Comment":"","TeamStatus":""}
    url_load = f'{RACE_RESULT_BASE_URL}/_UPFPQ/api/chipfile/get?lang=en&pw=0'
    url_save = f'{RACE_RESULT_BASE_URL}/_UPFPQ/api/chipfile/save?lang=en&pw=0'
    
    try:
        print('calling new')
        new_resp = requests.get(url_new, timeout=5)
        new_resp.raise_for_status()
        pid = new_resp.json()['ID']

        url_create = f'{RACE_RESULT_BASE_URL}/_UPFPQ/api/part/savefields?lang=en&pid={pid}&nohistory=1&pw=0'

        print('calling create')
        create_resp = requests.post(
            url_create,
            data=json.dumps(data_create).encode('utf-8'),
            headers={"Content-Type": "text/plain; charset=utf-8"},
            timeout=5
        )
        create_resp.raise_for_status()

        print('calling load')
        load_resp = requests.get(url_load)
        load_resp.raise_for_status()
        load_str = load_resp.text
        # print(load_str.replace('\n', '\\n').replace('\r', '\\r'))

        # check chip file
        load_lines = load_str.splitlines()
        if len(load_lines) <= 0 or len(load_lines[0]) < 11:
            raise Exception("invalid chip file")

        print('calling save')
        load_str += f"\r\n{transponder};{id}"
        save_resp = requests.post(url_save, data=load_str.encode('utf-8'))
        save_resp.raise_for_status()
    except Exception as e:
        print(e)
        raise

    return "added!"


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
    discipline = next(iter(c['name'] for c in CONTESTS if c['id'] == CONTEST_ID))
    return render_template("index.html", teams=teams, vehicles=vehicles, discipline=discipline)

@app.route("/data")
def get_data():
    return load_data()

@app.route('/assign', methods=['POST'])
def assign_driver_to_vehicle():
    global start_number_counter
    assignment = request.json
    team_name = assignment.get("team")
    driver = assignment.get("driver")
    vehicle_name = assignment.get("vehicle")

    # Increment run counter
    run_id = start_number_counter
    start_number_counter += 1

    # Find team and vehicle, get transponder
    data = load_data()
    team = next((t for t in data["teams"] if t["name"] == team_name), None)
    vehicle = next((v for v in data["vehicles"] if v["name"] == vehicle_name), None)
    if not team or not vehicle:
        return jsonify({"error": "Team or vehicle not found"}), 400

    transponder = vehicle.get("transponder", "")
    try:
        result = add_run(run_id, vehicle_name, team_name, driver, transponder)
    except Exception as e:
        return jsonify({"error": "Failed to push to Race Result server", "details": str(e)}), 502

    return jsonify({"message": "Assignment sent!", "result": result}), 200


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