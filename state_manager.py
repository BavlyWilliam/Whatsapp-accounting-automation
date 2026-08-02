import json
import os


def load_state(state_file):
    if not os.path.exists(state_file):
        return set()
    with open(state_file, "r") as f:
        data = json.load(f)
        return set(tuple(item) for item in data)


def save_state(state_file, seen_messages):
    with open(state_file, "w") as f:
        json.dump([list(item) for item in seen_messages], f)
