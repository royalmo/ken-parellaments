from flask import Flask, render_template, request, redirect
from pairings import store_request_to_json, JSON_FILE_PATH, generate_best_pairings
import random, json
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def index():
    with open(JSON_FILE_PATH, 'r') as f:
        json_contents = json.load(f)

    if "pairings" not in json_contents:
        return redirect('/pairings')
    
    team_contents = {}
    for team in json_contents["teams"]:
        rounds = []
        for round_pairs in json_contents["pairings"]:
            my_pair = next(filter(lambda r: team in r, round_pairs), None)
            opponent = my_pair[1] if my_pair[0] == team else my_pair[0]
            rounds.append({"adversary": opponent, "sport": my_pair[2]})
        team_contents[team] = rounds

    sport_contents = {}
    for sport_list in json_contents["sports"]:
        sport = sport_list[0] # We don't care about days here
        rounds = []
        for round_pairs in json_contents["pairings"]:
            my_pair = next(filter(lambda r: sport in r, round_pairs), ['---', '---'])
            rounds.append({"team_1": my_pair[0], "team_2": my_pair[1]})
        sport_contents[sport] = rounds

    num_rounds = int(json_contents["num_rounds"])

    # CONSTANTS (FOR NOW)
    day_names = [f"{i} de Juliol" for i in [7,8,9]]
    ROUND_DURATION = 10 # minutes
    TIME_BETWEEN_ROUNDS = 5 # minutes
    START_TIME = [19, 30]
    
    start_dt = datetime(2000, 1, 1, START_TIME[0], START_TIME[1])
    round_names = []

    for _ in range(num_rounds):
        end_dt = start_dt + timedelta(minutes=ROUND_DURATION)
        round_names.append(f"{start_dt.strftime('%H:%M')} - {end_dt.strftime('%H:%M')}")
        start_dt = end_dt + timedelta(minutes=TIME_BETWEEN_ROUNDS)
    
    return render_template('schedule.html',
                           team_contents=team_contents,
                           sport_contents=sport_contents,
                           num_rounds = num_rounds,
                           num_days = int(json_contents["num_days"]),
                           day_names = day_names,
                           round_names = round_names,
                           )

@app.route("/pairings")
def pairings_index():
    return render_template('pairings.html')

@app.route("/data.json")
def data():
    with open(JSON_FILE_PATH) as f:
        return f.read()
    
@app.route("/make-pairings", methods=["POST"])
def make_pairings():
    new_json = store_request_to_json(request.form)

    random.seed(42)
    pairings, penalization = generate_best_pairings()
    new_json["pairings"] = pairings
    new_json["penalization"] = penalization

    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(new_json, f, indent=4)

    return redirect('/')

if __name__=="__main__":
    app.run(debug=True, port=5000)
