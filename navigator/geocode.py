"""Turn a typed address or place name into coordinates.

Uses OpenStreetMap's Nominatim search API. Results are limited to Malaysia and
to the map's bounding box, so only places the road graph covers come back.
Nominatim's usage policy allows about one request per second; callers that
make several lookups in a row should pause between them.
"""

import requests

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

#: Map area as "west,north,east,south" (lon,lat,lon,lat), matching query.py.
VIEWBOX = "101.68336,3.10803,101.81314,3.02756"

HEADERS = {"User-Agent": "map_navigator/1.0 (https://github.com/ryankong3573/map_navigator)"}


def return_location_node(user_location):
    """Look up a place and return its coordinates.

    Matching depends on Nominatim and isn't always accurate; street names
    work best typed in OSM's order, e.g. "Jalan Damai Perdana 2/6C".

    Args:
        user_location: Free text typed by the user.

    Returns:
        ``(lat, lon, display_name)`` for the best match, or ``None`` if
        nothing matched or the request failed.
    """
    params = {
        "q": user_location,
        "limit": 1,
        "countrycodes": "my",
        "viewbox": VIEWBOX,
        "bounded": 1,  # only return results inside the viewbox
        "format": "json",
    }

    response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=60)
    if response.status_code != 200:
        print(f"ERROR! Nominatim returned {response.status_code}")
        return None

    results = response.json()
    if not results:
        return None

    best = results[0]
    return float(best["lat"]), float(best["lon"]), best["display_name"]
