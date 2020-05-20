import requests
import json
import sys
import os
import time
import atexit
from parsers import parse_developer_links, parse_developer_details


DATA_DIR = os.path.expanduser("~/scraping-data/rynekpierwotny")
os.makedirs(DATA_DIR, exist_ok=True)


DATA_FILE = os.path.join(DATA_DIR, "old.json")
NEW_URLS_FILE = os.path.join(DATA_DIR, "new.json")
START_URL = "https://rynekpierwotny.pl/deweloperzy/?page=1"


UA = (
    "Mozilla/5.0 (X1k; Linux x86_64) AppleWebKit/537.36"
    "(KHTML, like Gecko) Chrome/80.0.3987.87 Safari/537.36"
)


session = requests.Session()
session.headers.update({"User-agent": UA})

pending_urls = [
    {"url": START_URL, "details": False},
]

ALL_INVESTMENTS = {
    "investments": [],
    "known_urls": {},
}


def save_investments():
    global ALL_INVESTMENTS
    with open(DATA_FILE, "w+") as json_file:
        print("SAVING RESULTS", DATA_FILE)
        json.dump(ALL_INVESTMENTS, json_file, indent=4)

    with open(NEW_URLS_FILE, "w+") as json_file:
        print("SAVING NEW INVESTMENT URLS", NEW_URLS_FILE)
        json.dump(ALL_INVESTMENTS["new_investment_urls"], json_file, indent=4)


atexit.register(save_investments)


if os.path.isfile(DATA_FILE):
    with open(DATA_FILE, "r") as file_handle:
        ALL_INVESTMENTS = json.load(file_handle)


#ALL_INVESTMENTS["new_investment_urls"] = {}


while len(pending_urls):
    task = pending_urls.pop(0)
    current_url = task["url"]

    try:
        response = session.get(current_url, timeout=20)
        if task.get("details"):
            print("GET (developer)", current_url)
            try:
                # PROCESS DEVELOPER DETAILS
                new_investments = parse_developer_details(
                    response.text, task
                )

                ALL_INVESTMENTS["investments"].extend(new_investments)
                for new_inv in new_investments:
                    new_url = new_inv["url"]
                    if new_url not in ALL_INVESTMENTS["known_urls"]:
                        print("\t+++", new_url)
                        ALL_INVESTMENTS["new_investment_urls"][new_url] = {
                            "time": time.strftime("%F"),
                            "investment_name": new_inv["name"],
                            "developer_name": new_inv["task"]["developer_name"],
                            "developer_url": new_inv["task"]["url"],
                            "city": new_inv["city_name"],
                            "amount": new_inv["amount"]

                        }
                    ALL_INVESTMENTS["known_urls"][new_url] = time.time()

            except Exception as e:
                print("CANNOT PROCESS DEVELOPER DETAILS")
                print(e)
                print(pending_urls)
                continue
        else:
            print("GET (page)", current_url)
            try:
                # EXTRACT DEVELOPER LINKS
                new_urls = parse_developer_links(response.text, current_url)
                pending_urls.extend(new_urls)
            except Exception as e:
                print("EXTRACT DEVELOPER LINKS ERROR")
                print(e)
    except Exception as e:
        print("ERROR", e)
        print("SKIP", current_url)
        continue
