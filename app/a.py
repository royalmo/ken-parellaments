import random
from itertools import combinations

def generate_multiple_rounds(teams, banned_pairs, num_rounds):
    banned_set = {frozenset(pair) for pair in banned_pairs}
    team_usage = {team: 0 for team in teams}
    pair_usage = {}

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


import random
from collections import defaultdict

def assign_sports_to_rounds(rounds, sports, favorite_sports):
    team_sport_history = defaultdict(set)
    sport_assignments = []

    for rnd_index, round_pairings in enumerate(rounds):
        available_sports = sports[:]
        random.shuffle(available_sports)  # randomize for diversity

        # For each pairing, pick a sport that's not overused
        round_assignment = []
        used_sports = set()
        for team1, team2 in round_pairings:
            best_sport = None
            min_total_play = float('inf')

            for sport in available_sports:
                if sport in used_sports:
                    continue
                # Prioritize sports that help satisfy favorite requirements
                score = (
                    (sport in favorite_sports and sport not in team_sport_history[team1]) +
                    (sport in favorite_sports and sport not in team_sport_history[team2])
                )
                total_play = (
                    len(team_sport_history[team1]) +
                    len(team_sport_history[team2])
                ) - score  # reward underplayed favorites

                if total_play < min_total_play or best_sport is None:
                    min_total_play = total_play
                    best_sport = sport

            if best_sport is None:
                # Fallback to any unused sport
                best_sport = next(s for s in available_sports if s not in used_sports)

            round_assignment.append((team1, team2, best_sport))
            used_sports.add(best_sport)
            team_sport_history[team1].add(best_sport)
            team_sport_history[team2].add(best_sport)

        sport_assignments.append(round_assignment)

    # Validation step: ensure each team played all favorite_sports at least once
    for team in team_sport_history:
        for fav in favorite_sports:
            if fav not in team_sport_history[team]:
                raise ValueError(f"Team {team} did not play favorite sport {fav}")

    return sport_assignments



teams = ["A", "B", "C", "D"]
sports = ["Basketball", "Tennis"]  # 2 sports * 2 = 4 teams
favorite_sports = ["Basketball"]

rounds = generate_multiple_rounds(teams, [], num_rounds=4)
assigned = assign_sports_to_rounds(rounds, sports, favorite_sports)

for i, r in enumerate(assigned, 1):
    print(f"Round {i}:")
    for t1, t2, sport in r:
        print(f"  {t1} vs {t2} in {sport}")


