import json
import os


DATA_DIR = os.path.expanduser("~/scraping-data/rynekpierwotny")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "wykresy"), exist_ok=True)

NEW_URLS_FILE = os.path.join(DATA_DIR, "new_reverse.json")
DATA_FILE = os.path.join(DATA_DIR, "new.json")


print(DATA_FILE)
reader = {}
if os.path.isfile(DATA_FILE):
    with open(DATA_FILE, "r") as file_handle:
        reader = json.load(file_handle)

print(reader)


list_key_value = [[k, v] for k, v in reader.items()]

reverse_list = list_key_value[::-1]

reverse_dict = dict(reverse_list)

print(reverse_dict)


with open(NEW_URLS_FILE, "w+") as json_file:
    print("SAVING NEW REVERSE URLS", NEW_URLS_FILE)
    json.dump(reverse_dict, json_file, indent=4)
