import json
import os

DATA_FILE = 'data.json'

def load_data():
    if not os.path.exists(DATA_FILE):
        default = {'user_id': None, 'groups': [], 'keywords': []}
        save_data(default)
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)