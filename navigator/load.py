"""Load OpenStreetMap road data and turn it into a routable graph.

The input is the JSON returned by the Overpass API (see ``query.py``), where
each element is a *way* (a road) carrying its node IDs and, thanks to
``out geom``, the coordinates of those nodes.

This module also holds the small geometry helpers (distance, bearing, turn
classification) shared by ``routing.py``.
"""

import json
import math

#: OSM ``highway`` values treated as drivable. Anything else (footway, steps,
#: cycleway, path, ...) is left out of the graph.
CAR_ROADS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential",
    "motorway_link", "trunk_link", "primary_link",
    "secondary_link", "tertiary_link",
    "living_street", "service", "road",
}

#: Mean radius of the Earth in metres, used by the haversine formula.
EARTH_RADIUS_M = 6371000


def convert_to_dict(json_file):
    """Load a JSON map file into a Python dictionary.

    Args:
        json_file: Path to a JSON file saved from the Overpass API.

    Returns:
        The parsed JSON, with the ways under the ``"elements"`` key.
    """
    with open(json_file, "r") as file:
        return json.load(file)


def create_list_of_nodes(data):
    """Build a lookup from node ID to its coordinates.

    Every way is included, not just drivable ones, so any node can be
    looked up.

    Args:
        data: The parsed Overpass data (see ``convert_to_dict``).

    Returns:
        ``{node_id: {"lat": float, "lon": float}, ...}``
    """
    nodes = {}
    for way in data["elements"]:
        # ``nodes`` and ``geometry`` are parallel lists: the n-th coordinate
        # belongs to the n-th node ID.
        for node_id, coordinates in zip(way["nodes"], way["geometry"]):
            nodes[node_id] = coordinates
    return nodes


def calculate_distance(node, neighbour_node):
    """Return the great-circle distance between two points, in metres.

    Uses the haversine formula, which is accurate for the short distances
    found on a city map.

    Args:
        node: ``{"lat": ..., "lon": ...}`` of the first point.
        neighbour_node: ``{"lat": ..., "lon": ...}`` of the second point.

    Returns:
        Distance in metres (float).
    """
    phi1 = math.radians(node["lat"])
    phi2 = math.radians(neighbour_node["lat"])
    dphi = math.radians(node["lat"] - neighbour_node["lat"])
    dlambda = math.radians(node["lon"] - neighbour_node["lon"])

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def get_neighbours(data, nodes_list):
    """Build the road graph as an adjacency list.

    Each pair of consecutive nodes on a drivable way becomes an edge weighted
    by its length. Two-way roads get an edge in both directions; roads tagged
    ``oneway=yes`` only get the forward edge. Roads join up at intersections
    automatically because they share node IDs.

    Args:
        data: The parsed Overpass data.
        nodes_list: The node lookup from ``create_list_of_nodes``.

    Returns:
        ``{node_id: [(neighbour_id, distance_m), ...], ...}``. Only nodes on
        drivable roads appear as keys.
    """
    graph = {}

    for way in data["elements"]:
        if way["tags"].get("highway") not in CAR_ROADS:
            continue

        is_oneway = way["tags"].get("oneway") == "yes"

        # Walk the way one segment at a time: (n0, n1), (n1, n2), ...
        for node1, node2 in zip(way["nodes"], way["nodes"][1:]):
            distance = calculate_distance(nodes_list[node1], nodes_list[node2])

            graph.setdefault(node1, [])
            graph.setdefault(node2, [])

            graph[node1].append((node2, distance))
            if not is_oneway:
                graph[node2].append((node1, distance))

    return graph


def get_street_names(data):
    """Build a lookup from road segment to street name.

    Keyed by node *pairs* rather than single nodes, because an intersection
    node belongs to several streets at once. One-way roads only get the
    forward pair, matching the graph.

    Args:
        data: The parsed Overpass data.

    Returns:
        ``{(node1, node2): "Street name", ...}``. Ways without a ``name`` tag
        are labelled ``"unnamed road"``.
    """
    street_names = {}

    for way in data["elements"]:
        if way["tags"].get("highway") not in CAR_ROADS:
            continue

        name = way["tags"].get("name", "unnamed road")
        is_oneway = way["tags"].get("oneway") == "yes"

        for node1, node2 in zip(way["nodes"], way["nodes"][1:]):
            street_names[node1, node2] = name
            if not is_oneway:
                street_names[node2, node1] = name

    return street_names


def calculate_bearing(node1, node2):
    """Return the compass bearing from one point to another.

    Args:
        node1: ``{"lat": ..., "lon": ...}`` of the starting point.
        node2: ``{"lat": ..., "lon": ...}`` of the end point.

    Returns:
        Degrees in ``[0, 360)``, where 0 is north and 90 is east.
    """
    lat1, lon1 = math.radians(node1["lat"]), math.radians(node1["lon"])
    lat2, lon2 = math.radians(node2["lat"]), math.radians(node2["lon"])

    x = math.sin(lon2 - lon1) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(lon2 - lon1)

    return (math.degrees(math.atan2(x, y)) + 360) % 360


def determine_turn(in_angle, out_angle):
    """Classify the turn between two bearings.

    The difference is wrapped into ``[-180, 180)`` so it always takes the
    short way round; positive means clockwise (right).

    Args:
        in_angle: Bearing of the last segment before the junction.
        out_angle: Bearing of the first segment after the junction.

    Returns:
        ``"continue straight"`` (within 30°), ``"turn right"``,
        ``"turn left"`` or ``"U-turn"`` (150° or more either way).
    """
    turn = ((out_angle - in_angle + 540) % 360) - 180

    if -30 <= turn < 30:
        return "continue straight"
    if 30 <= turn < 150:
        return "turn right"
    if -150 <= turn < -30:
        return "turn left"
    return "U-turn"


if __name__ == "__main__":
    # Quick sanity check: build the graph from the real map file.
    data = convert_to_dict("map_data.json")
    nodes = create_list_of_nodes(data)
    graph = get_neighbours(data, nodes)
    print(f"Loaded {len(nodes)} nodes, {len(graph)} of them on drivable roads.")
