"""Download the road network for the map area and save it to map_data.json.

Run this once (from the project root) when changing the map area or
refreshing the data; everything else works from the saved file:

    python -m navigator.query

It sends an Overpass API query for every drivable road inside the bounding
box around Bandar Damai Perdana. ``out geom`` makes each way carry its own
node coordinates, so no separate node lookup is needed.
"""

import json
import sys

import requests

OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OUTPUT_FILE = "map_data.json"

#: (south, west, north, east), matching the viewbox in geocode.py.
BBOX = "3.02756,101.68336,3.10803,101.81314"

# The highway types listed here should match load.CAR_ROADS.
QUERY = f"""
[out:json][timeout:240];
way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|road|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"]
({BBOX});
out geom;
"""

HEADERS = {"User-Agent": "map_navigator/1.0 (https://github.com/ryankong3573/map_navigator)"}


def fetch_map_data():
    """Query Overpass and write the result to ``OUTPUT_FILE``."""
    try:
        response = requests.post(OVERPASS_URL, data={"data": QUERY}, headers=HEADERS, timeout=260)
    except requests.exceptions.RequestException as e:
        print("Couldn't reach the server:", e)
        sys.exit(1)

    if response.status_code != 200:
        print(f"ERROR! Overpass returned {response.status_code}")
        sys.exit(1)

    with open(OUTPUT_FILE, "w") as f:
        json.dump(response.json(), f)
    print(f"OK, saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    fetch_map_data()
