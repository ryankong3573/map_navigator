# navigator/

The core of the route finder. This package downloads the map, builds a road graph from it, turns typed addresses into coordinates, finds the shortest route and describes it street by street.

`main.py` (one folder up) wraps these modules in a FastAPI web server. The tests are in `testings/`.

## How the pieces fit

```
query.py     Overpass API ──▶ map_data.json                  (run once, to download the map)

load.py      map_data.json ──▶ node lookup, road graph, street names

geocode.py   "SJK (C) Connaught 2" ──▶ (lat, lon, name)       (Nominatim)

routing.py   (lat, lon) ──▶ nearest road node
             start node + goal node ──▶ A* ──▶ path + distance
             path ──▶ street-by-street directions with turns
```

A full request goes through the modules in this order:

1. `geocode.return_location_node()` turns the start and destination text into coordinates.
2. `routing.get_nearest_node()` snaps each point to the closest drivable road node.
3. `routing.a_star_search()` finds the shortest path between the two nodes.
4. `routing.street_path()` turns that path into directions such as "turn right onto Persiaran Damai Perdana, 349 m".

## Modules

### `query.py`: download the map

Asks the Overpass API for every drivable road inside the map's bounding box (around Bandar Damai Perdana) and saves the reply to `map_data.json`. The query ends with `out geom`, so each road includes the coordinates of all its points.

You only need to run it when changing the map area or refreshing the data. Run it from the project root, so the file is saved where `main.py` looks for it:

```bash
python -m navigator.query
```

The script exits with code 1 if the server can't be reached or returns an error. Importing the module does nothing.

| Name | What it is |
|---|---|
| `fetch_map_data()` | Sends the query and writes `OUTPUT_FILE` |
| `BBOX` | The map area as south, west, north, east |
| `QUERY` | The Overpass query |
| `OVERPASS_URL`, `OUTPUT_FILE`, `HEADERS` | Where to send the query, where to save the result, and the User-Agent header |

### `load.py`: build the graph

| Function | What it does |
|---|---|
| `convert_to_dict(path)` | Loads a JSON map file into a Python dictionary |
| `create_list_of_nodes(data)` | Builds the node lookup: node ID → `{"lat", "lon"}` |
| `get_neighbours(data, nodes)` | Builds the road graph (see [Key data structures](#key-data-structures)) |
| `get_street_names(data)` | Builds the road-piece → street name lookup |
| `calculate_distance(a, b)` | Haversine distance in metres between two coordinates |
| `calculate_bearing(a, b)` | Compass direction from one coordinate to another, 0–360°, where 0 is north |
| `determine_turn(in, out)` | Turns two bearings into `"continue straight"`, `"turn right"`, `"turn left"` or `"U-turn"` |

`CAR_ROADS` is the set of `highway` types treated as drivable: motorway down to residential, link roads, `living_street`, `service` and `road`. Anything else, such as footways, steps or cycleways, is left out of the graph. Keep this set in step with the road types in `query.py`'s query.

Running `python -m navigator.load` from the project root loads `map_data.json` and prints how many nodes it found, as a quick check.

### `geocode.py`: addresses to coordinates

`return_location_node(text)` sends what the user typed to OpenStreetMap's **Nominatim** search service and returns `(lat, lon, display_name)` for the best match. It returns `None` if nothing matched or the request failed.

The search only covers Malaysia (`countrycodes=my`) and only the map area (`viewbox` with `bounded=1`), so it can't return a place the road graph doesn't cover. `VIEWBOX` has to match `BBOX` in `query.py`.

Nominatim allows about one request per second, which is why `main.py` waits a second between the start and destination lookups.

### `routing.py`: find the route

| Function | What it does |
|---|---|
| `get_nearest_node(lat, lon, nodes, graph)` | Snaps a point to the closest node in the graph, so it always lands on a drivable road. Returns `None` if that node is more than `MAX_SNAP_DISTANCE_M` (800 m) away. |
| `a_star_search(start, goal, graph, nodes)` | A* search. Returns `(path, distance_in_metres)`, or `(None, None)` if there's no route. |
| `reconstruct_path(came_from, goal)` | Follows `came_from` back from the goal to rebuild the path |
| `street_path(path, street_names, graph, nodes)` | Groups the path by street and works out the turn at each change of street |

## Key data structures

**Node lookup** — where each point is:
```python
{7266925564: {"lat": 3.0471911, "lon": 101.7392459}, ...}
```

**Road graph** — an adjacency list of where you can drive from each node, and how far it is in metres:
```python
{222: [(111, 45.0), (333, 120.0)], ...}
```
Two-way roads get an edge in both directions. Roads tagged `oneway=yes` get only the forward edge. Roads connect at intersections automatically because they share node IDs.

**Street names** — which street each piece of road belongs to:
```python
{(111, 222): "Jalan Damai Perdana 2/1", ...}
```
The keys are node pairs rather than single nodes, because an intersection node belongs to several streets at once.

**Directions** — the output of `street_path`:
```python
[["Jalan Damai Perdana 2/6", 115.0, "start"],
 ["Persiaran Damai Perdana", 349.4, "turn right"], ...]
```
If a route leaves a street and later comes back to it, that street appears again as a separate entry.

## Design choices

- **Overpass instead of OSMnx.** The raw OpenStreetMap data is parsed by hand, to understand how nodes, ways and tags work.
- **A\* with a straight-line heuristic.** The straight-line (haversine) distance to the goal is never longer than the real road distance. That means A\* still finds the true shortest route, while checking fewer nodes than Dijkstra's algorithm.
- **Turns from bearings.** The turn at a junction is the difference between the bearing of the last road piece before it and the first one after it. The difference is wrapped into −180° to 180°, so it always measures the short way round. Within ±30° counts as straight, and 150° or more counts as a U-turn.

## Known limitations

- Routes by distance, not travel time, so there are no speed limits or traffic.
- Covers one small area. `get_nearest_node` checks every node in turn, so a bigger map would need a faster search, such as a KD-tree.
- `service` roads (car parks, back lanes) count as drivable, which can produce odd "unnamed road" stretches.
- Address search depends on how well Nominatim matches the text. Street names work best typed the way OpenStreetMap writes them, e.g. "Jalan Damai Perdana 2/6C".
