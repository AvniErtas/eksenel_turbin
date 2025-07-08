import json

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_input_bounds(filepath):
    raw_data = load_json(filepath)
    bounds = [(item['min'], item['max']) for item in raw_data]
    names = [item['name'] for item in raw_data]
    return names, bounds

def load_output_constraints(filepath):
    raw_data = load_json(filepath)
    constraints = {}
    for key, value in raw_data.items():
        constraints[key] = (value['min'], value['max'])
    return constraints
