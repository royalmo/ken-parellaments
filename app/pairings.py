import json

JSON_FILE_PATH = 'data/data.json'

def store_request_to_json(args):
    new_json = {
        "num_days" : args.get("numDays"),
        "num_rounds" : args.get("numRounds"),
        "teams" : args.get("teams").replace('\r', '').split('\n'),
        "sports" : [[s.split(',')[0], [int(x) for x in s.split(',')[1:]]] for s in args.get("sports").replace('\r', '').split('\n')],
        "exclusions" : [s.split(',') for s in args.get("exclusions").replace('\r', '').split('\n')],
        "musts" : [s.split(',') for s in args.get("musthaves").replace('\r', '').split('\n')],
    }
    with open(JSON_FILE_PATH, 'w') as f:
        json.dump(new_json, f, indent=4)

    return new_json
