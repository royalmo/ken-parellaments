import json
import random
from collections import defaultdict, Counter
from itertools import combinations, cycle

JSON_FILE_PATH = 'data/data.json'

def store_request_to_json(args):
    new_json = {
        "num_days" : args.get("numDays"),
        "num_rounds" : args.get("numRounds"),
        "start_day" : args.get("startDay"),
        "start_time_hour" : args.get("startHour"),
        "start_time_min" : args.get("startMin"),
        "teams" : [s for s in args.get("teams").replace('\r', '').split('\n') if s != ""],
        "sports" : [[s.split(',')[0], [int(x) for x in s.split(',')[1:]]] for s in args.get("sports").replace('\r', '').split('\n')],
        "exclusions" : [s.split(',') for s in args.get("exclusions").replace('\r', '').split('\n') if s != ""],
        "musts" : [s.split(',') for s in args.get("musthaves").replace('\r', '').split('\n') if s != ""],
    }
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(new_json, f, indent=4)

    return new_json

def generate_multiple_rounds(teams, banned_pairs, num_rounds):
    banned_set = {frozenset(pair) for pair in banned_pairs}
    team_usage = {team: 0 for team in teams}
    pair_usage = {}

    random.shuffle(teams)

    def score_pair(a, b):
        pair = frozenset([a, b])
        return (
            team_usage[a] + 
            team_usage[b] + 
            pair_usage.get(pair, 0) * 2  # penalize repeated pairs more
        )

    def get_valid_pairings(teams):
        used = set()
        available = [t for t in teams]
        pairings = []

        # Try greedy pairing based on usage scores
        available.sort(key=lambda t: team_usage[t])  # prioritize less-used
        while available:
            a = available.pop(0)
            best_b = None
            best_score = float('inf')
            for b in available:
                if frozenset([a, b]) in banned_set:
                    continue
                score = score_pair(a, b)
                if score < best_score:
                    best_score = score
                    best_b = b
            if best_b is not None:
                available.remove(best_b)
                pairings.append((a, best_b))
            else:
                # if no pair found for a, put back and try different order next round
                return None
        return pairings

    rounds = []
    retries = 0
    max_retries = 1000

    while len(rounds) < num_rounds:
        pairings = get_valid_pairings(teams)
        if pairings:
            rounds.append(pairings)
            # update usage stats
            for a, b in pairings:
                team_usage[a] += 1
                team_usage[b] += 1
                key = frozenset([a, b])
                pair_usage[key] = pair_usage.get(key, 0) + 1
        else:
            retries += 1
            if retries > max_retries:
                raise RuntimeError("Couldn't find enough diverse rounds.")
            random.shuffle(teams)

    return rounds

def assign_sports_to_rounds(rounds, sports, favorite_sports):
    team_sport_history = defaultdict(set)
    sport_assignments = []

    for rnd_index, round_pairings in enumerate(rounds):
        available_sports = sports[:]
        random.shuffle(available_sports)

        round_assignment = []
        used_sports = set()

        for team1, team2 in round_pairings:
            best_sport = None
            best_score = float('-inf')

            for sport in available_sports:
                if sport in used_sports:
                    continue

                # Scoring function: +2 for satisfying a missing group
                def satisfaction(team):
                    count = 0
                    for group in favorite_sports:
                        if not any(s in team_sport_history[team] for s in group):
                            if sport in group:
                                count += 1
                    return count

                score = satisfaction(team1) + satisfaction(team2)

                if score > best_score:
                    best_score = score
                    best_sport = sport

            if best_sport is None:
                best_sport = next(s for s in available_sports if s not in used_sports)

            round_assignment.append((team1, team2, best_sport))
            used_sports.add(best_sport)
            team_sport_history[team1].add(best_sport)
            team_sport_history[team2].add(best_sport)

        sport_assignments.append(round_assignment)

    return sport_assignments


def generate_pairings(strict=False):
    with open(JSON_FILE_PATH, 'r') as f:
        json_contents = json.load(f)

    teams = json_contents["teams"]
    sports = json_contents["sports"]
    exclusions = json_contents["exclusions"]

    num_days = int(json_contents["num_days"])
    num_rounds = int(json_contents["num_rounds"])
    musts = json_contents["musts"]

    rounds = generate_multiple_rounds(teams, exclusions, num_rounds=num_rounds*num_days)
    assigned = []

    start_days = 0
    if num_days >= 2:
        # First two days go as a group
        start_days=2
        todays_sports = [x[0] for x in sports if 1 in x[1]]
        todays_rounds = rounds[:2*num_rounds]
        todays_musts = [x for x in musts if x[0] in todays_sports]
        assigned += assign_sports_to_rounds(todays_rounds, todays_sports, todays_musts)

    for day_num in range(start_days, num_days):
        todays_sports = [x[0] for x in sports if day_num+1 in x[1]]
        todays_rounds = rounds[day_num*num_rounds:(day_num+1)*num_rounds]
        todays_musts = [x for x in musts if x[0] in todays_sports]
        assigned += assign_sports_to_rounds(todays_rounds, todays_sports, todays_musts)

    return assigned, get_penalization(assigned, musts, strict=strict)

def get_penalization(assigned, musts, strict=False, do_print=False):
    team_sport_history = defaultdict(set)
    for r in assigned:
        for t1, t2, sport in r:
            team_sport_history[t1].add(sport)
            team_sport_history[t2].add(sport)

    penalization = 0

    for team, history in team_sport_history.items():
        for group in musts:
            if not any(s in history for s in group):
                if strict: raise ValueError(f"Team {team} did not play any sport from group {group}")
                if do_print: print(f"Team {team} did not play any sport from group {group}")
                penalization += 1

    return penalization

def print_rounds(assigned):
    for i, r in enumerate(assigned, 1):
        print(f"Round {i}:")
        for t1, t2, sport in r:
            print(f"  {t1} vs {t2} in {sport}")

def generate_best_pairings():
    assigneds = []
    penalizations = []

    for i in range(1000):
        assigned, penalization = generate_pairings()
        assigneds.append(assigned)
        penalizations.append(penalization)

    return assigneds[penalizations.index(min(penalizations))], min(penalizations)

if __name__=="__main__":
    random.seed(42)   
    with open(JSON_FILE_PATH, 'r') as f:
        json_contents = json.load(f)
    musts = json_contents["musts"]

    best_assigned, best_penalization = generate_best_pairings()
    print(f"Best penalization: {best_penalization}")
    get_penalization(best_assigned, musts, do_print=True)
    #print_rounds(best_assigned)
