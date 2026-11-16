"""FastAPI backend for Map Navigator.

Loads the road graph once at startup, then serves nearest-node lookups and
A* routes to the frontend. Run locally with ``fastapi dev main.py`` (docs at
http://localhost:8000/docs).
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import navigator.load as load
import navigator.routing as routing

MAP_FILE = Path(__file__).parent / "map_data.json"

app = FastAPI(title="Map Navigator")

# Browser origins allowed to call this API. An origin is scheme + host + port,
# with no path and no trailing slash, or the browser won't match it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://map-navigation-frontend.onrender.com",
        "http://localhost:5500",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
    ],
)

# --- Load the map once at startup ---
raw_data = load.convert_to_dict(MAP_FILE)
list_of_nodes = load.create_list_of_nodes(raw_data)        # node ID -> {"lat", "lon"}
node_graphs = load.get_neighbours(raw_data, list_of_nodes)  # node ID -> [(neighbour ID, metres), ...]
nodes_and_streets = load.get_street_names(raw_data)         # (node ID, node ID) -> street name


@app.get("/health")
def health():
    """Check that the server is up and report how many road nodes were loaded."""
    return {"status": "ok", "nodes": len(node_graphs)}


@app.get("/nearest")
def get_nodes(loc_lat: float, loc_lon: float, des_lat: float, des_lon: float):
    """Snap the start and destination to their nearest drivable road nodes.

    Returns ``[location_node_id, destination_node_id]``, or 404 if either
    point is more than 800 m from the mapped roads.
    """
    location = routing.get_nearest_node(loc_lat, loc_lon, list_of_nodes, node_graphs)
    destination = routing.get_nearest_node(des_lat, des_lon, list_of_nodes, node_graphs)

    if location is None or destination is None:
        raise HTTPException(status_code=404, detail="Could not find location")
    return location, destination


@app.get("/routing")
def get_route(location: int, destination: int):
    """Find the shortest route between two road node IDs.

    Returns ``{"coordinates": [[lat, lon], ...], "distance": metres}``, or
    404 if a node ID is unknown or no route exists.
    """
    if location not in node_graphs or destination not in node_graphs:
        raise HTTPException(status_code=404, detail="Unknown node ID")

    path, distance = routing.a_star_search(location, destination, node_graphs, list_of_nodes)
    if path is None:
        raise HTTPException(status_code=404, detail="route not found")

    coordinates = [[list_of_nodes[node]["lat"], list_of_nodes[node]["lon"]] for node in path]
    return {"coordinates": coordinates, "distance": distance}
