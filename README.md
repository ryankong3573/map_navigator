# map_navigator

A command-line route finder for a neighbourhood in Cheras, Kuala Lumpur, built from scratch in Python on real OpenStreetMap data.

Type where you are and where you want to go, and it finds the shortest drivable route with **A\* search** and gives you turn-by-turn directions.

```
Where are you currently?: Jalan Damai Perdana 2/6C
OK
Jalan Damai Perdana 2/6C, Bandar Damai Perdana, Cheras, ..., Selangor, Malaysia
Is this your location? [Y/N]: Y
Where do you want to go?: Connaught 2
OK
SJK (C) Connaught 2, Jalan Desa Cahaya 12, Bandar Damai Perdana, Cheras, ..., Malaysia
Is this your destination? [Y/N]: Y
start at Jalan Damai Perdana: 880.22m
turn right at Persiaran Damai Perdana: 349.42m
turn left at unnamed road: 366.67m
distance: 1.60km
```

## Features

- **Real road data** pulled straight from the **Overpass API** and parsed by hand (no OSMnx), then cached locally
- **A road graph** built from OSM ways and nodes, with distances from the haversine formula, **one-way roads** respected, and **non-car roads** (footways, steps, cycleways) filtered out
- **Address search** through OpenStreetMap's **Nominatim** API, limited to the mapped area
- **Snapping** typed places to the nearest drivable road node
- **A\* pathfinding** with a straight-line heuristic, which finds the true shortest route
- **Turn-by-turn directions**: the route is grouped by street, and each turn (left / right / straight / U-turn) is worked out from compass bearings
- **A pytest test suite** on a small hand-checkable map

## How it works

```
1. Fetch     Overpass API ──▶ map_data.json
2. Build     map_data.json ──▶ node lookup + road graph + street names
3. Search    "SJK (C) Connaught 2" ──▶ Nominatim ──▶ (lat, lon)
4. Snap      (lat, lon) ──▶ nearest drivable node
5. Route     A* (start node → goal node) ──▶ path + distance
6. Direct    path ──▶ streets + turns
```

More detail on each module, the data structures and the design choices is in [`navigator/README.md`](navigator/README.md).

## Project structure

```
map_navigator/
├── main.py            # the command-line app: ask → search → route → directions
├── navigator/
│   ├── query.py       # fetch road data from Overpass, save to map_data.json
│   ├── load.py        # build the node lookup, road graph and street names
│   ├── geocode.py     # address → coordinates via Nominatim
│   └── routing.py     # nearest node, A* search, directions
├── testings/          # pytest suite + test_data.json
└── map_data.json      # cached road data for the mapped area
```

## Getting started

Requires Python 3.

```bash
git clone https://github.com/ryankong3573/map_navigator.git
cd map_navigator

python -m venv venv
source venv/bin/activate        # Windows PowerShell: venv\Scripts\Activate.ps1

pip install requests pytest
```

**Run the app:**
```bash
python main.py
```

**Refresh the map data** (only needed to change the area or update the roads):
```bash
python navigator/query.py
```
The public Overpass servers are sometimes busy. If you get a 502 or 504, wait a minute and try again.

**Run the tests:**
```bash
pytest
```

## Limitations and next steps

- Routes by **distance**, not travel time. Adding speed estimates per road type would give more realistic routes.
- Covers **one neighbourhood**. A bigger map would need a faster nearest-node search (e.g. a KD-tree), and possibly the routing rewritten in C++.
- `service` roads (car parks, back lanes) count as drivable, which sometimes adds "unnamed road" stretches.
- Address search depends on how well Nominatim matches the text. Street names work best typed in OSM's order, e.g. "Jalan Damai Perdana 2/6C".
- **Planned:** drawing the route on an interactive map (Folium), and a simple web interface.

## Acknowledgements

- Map data © [OpenStreetMap](https://www.openstreetmap.org/copyright) contributors, available under the Open Database License (ODbL).
- Road data from the [Overpass API](https://overpass-api.de/), and address search from [Nominatim](https://nominatim.org/).
- The test files were generated with help from Claude, then reviewed and approved. All application code was written by me.
