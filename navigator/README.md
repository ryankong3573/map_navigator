# navigator/

The core of the route finder: fetching map data, building a road graph, finding addresses, routing between them and turning the route into directions.

`main.py` (one folder up) ties these modules together into the command-line app.

## How the pieces fit

```
query.py      Overpass API ──▶ map_data.json             (run once, to fetch the map)

load.py       map_data.json ──▶ node lookup, road graph, street names

geocode.py    "SJK (C) Connaught 2" ──▶ (lat, lon)        (Nominatim)

routing.py    (lat, lon) ──▶ nearest road node
              start node + goal node ──▶ A* ──▶ path + distance
              path ──▶ street-by-street directions with turns
```

## Modules

### `query.py`: fetch the map

Sends an Overpass API query for every road (`way["highway"]`) inside a bounding box around Bandar Damai Perdana, and saves the reply to `map_data.json`. It uses `out geom`, so each way carries its own node coordinates.

Only needs to be run when changing the map area or refreshing the data. Everything else works from the saved file.

### `load.py`: build the graph

| Function | What it does |
|---|---|
| `convert_to_dict(path)` | Loads a JSON map file into a Python dictionary |
| `create_list_of_nodes(data)` | Builds the node lookup: node ID → `{"lat", "lon"}` |
| `calculate_distance(a, b)` | Haversine distance in metres between two coordinates |
| `get_neighbours(data, nodes)` | Builds the road graph (see below) |
| `get_street_names(data)` | Builds the edge → street name lookup |
| `calculate_bearing(a, b)` | Compass direction (0–360°, 0 = north) from one coordinate to another |
| `determine_turn(in, out)` | Turns two bearings into `"turn left"`, `"turn right"`, `"continue straight"` or `"U-turn"` |

`CAR_ROADS` is the set of `highway` values treated as drivable (motorway down to residential, link roads, `living_street`, `service`, `road`). Footways, steps, cycleways and so on are left out of the graph.

### `geocode.py`: addresses to coordinates

Uses OpenStreetMap's **Nominatim** search API to turn what the user types into `(lat, lon, display_name)`. The search is limited to Malaysia (`countrycodes=my`) and to the map's bounding box (`viewbox` + `bounded=1`), so it can only return places the graph covers. Returns `None` when nothing matches.

### `routing.py`: find the route

| Function | What it does |
|---|---|
| `get_nearest_node(lat, lon, nodes, graph)` | Snaps a point to the closest node **in the graph**, so it always lands on a drivable road |
| `a_star_search(start, goal, graph, nodes)` | A* search; returns `(path, distance_in_metres)`, or `None` if there's no route |
| `reconstruct_path(came_from, goal)` | Follows `came_from` back from the goal to rebuild the path |
| `street_path(path, street_names, graph, nodes)` | Groups the path by street and works out the turn at each street change |

## Key data structures

**Node lookup**: where each point is:
```python
{7266925564: {"lat": 3.0471911, "lon": 101.7392459}, ...}
```

**Road graph**: an adjacency list, where you can go from each node and how far it is:
```python
{222: [(111, 45.0), (333, 120.0)], ...}
```
Two-way roads get an edge in both directions, and `oneway = yes` roads get only the forward one. Roads join at intersections automatically, because they share node IDs.

**Street names**: which street each piece of road belongs to:
```python
{(111, 222): "Jalan Damai Perdana 2/1", ...}
```
Keyed by node **pairs** rather than single nodes, because an intersection node belongs to several streets at once.

**Directions**: the output of `street_path`:
```python
[["Jalan Damai Perdana 2/6", 115.0, "start"],
 ["Persiaran Damai Perdana", 349.4, "turn right"], ...]
```

## Design choices

- **Overpass instead of OSMnx**: parsing the raw OpenStreetMap data by hand, to understand nodes, ways and tags properly.
- **A\* with a straight-line heuristic**: the haversine distance to the goal never overestimates the road distance, so A* still finds the true shortest route while exploring fewer nodes than Dijkstra.
- **Turns from bearings**: the turn at a junction is the difference between the bearing of the last road piece before it and the first one after it, wrapped into −180° to 180° so it takes the short way round.

## Known limitations

- Routes by **distance**, not travel time (no speed limits or traffic).
- Covers one small area. A bigger map would need a faster nearest-node search (e.g. a KD-tree).
- `service` roads (car parks, back lanes) are drivable, which can produce odd "unnamed road" stretches.
- Address search depends on Nominatim's matching. Street names like `2/6C` work best typed in OSM's order, e.g. "Jalan Damai Perdana 2/6C".

Tests for all of this live in `testings/`.
