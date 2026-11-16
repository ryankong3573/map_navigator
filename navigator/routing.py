"""Find routes on the road graph and turn them into directions.

All functions work on the structures built in ``load.py``:

* ``nodes_list``  -- ``{node_id: {"lat", "lon"}}``
* ``graph``       -- ``{node_id: [(neighbour_id, distance_m), ...]}``
* ``node_and_street`` -- ``{(node1, node2): "Street name"}``
"""

import heapq

import navigator.load as load

#: A point further than this (in metres) from every road node is treated as
#: outside the map, and ``get_nearest_node`` returns ``None`` for it.
MAX_SNAP_DISTANCE_M = 800


def get_nearest_node(lat, lon, nodes_list, graph):
    """Snap a coordinate to the closest node on a drivable road.

    Only nodes in ``graph`` are considered, so the result is always somewhere
    a car can start or finish. This is a linear scan, which is fine for one
    small area; a bigger map would want a spatial index such as a KD-tree.

    Args:
        lat, lon: The point to snap, e.g. from ``geocode.return_location_node``.
        nodes_list: Node lookup (includes non-road nodes).
        graph: Road graph; its keys are the candidate nodes.

    Returns:
        The nearest node ID, or ``None`` if it is more than
        ``MAX_SNAP_DISTANCE_M`` away.
    """
    target = {"lat": lat, "lon": lon}
    nearest_node = None
    nearest_distance = float("inf")

    for node in graph:
        distance = load.calculate_distance(target, nodes_list[node])
        if distance < nearest_distance:
            nearest_node = node
            nearest_distance = distance

    if nearest_distance > MAX_SNAP_DISTANCE_M:
        return None
    return nearest_node


def reconstruct_path(came_from, target):
    """Rebuild a path by following ``came_from`` back from the target.

    Args:
        came_from: ``{node: previous_node}``, with the start mapped to ``None``.
        target: The node the search ended on.

    Returns:
        List of node IDs from start to target.
    """
    path = []
    current = target

    while current is not None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path


def a_star_search(start, target, graph, nodes_list):
    """Find the shortest route between two nodes with A*.

    The heuristic is the straight-line (haversine) distance to the target.
    It never overestimates the road distance, so the route found is the true
    shortest one, while exploring fewer nodes than Dijkstra would.

    Args:
        start: Starting node ID (must be in ``graph``).
        target: Goal node ID.
        graph: Road graph from ``load.get_neighbours``.
        nodes_list: Node lookup from ``load.create_list_of_nodes``.

    Returns:
        ``(path, distance_m)`` where ``path`` is a list of node IDs, or
        ``(None, None)`` if the target can't be reached.
    """
    def heuristic(node):
        return load.calculate_distance(nodes_list[node], nodes_list[target])

    # Priority queue of (estimated total distance, node).
    queue = [(heuristic(start), start)]
    visited = set()
    came_from = {start: None}
    g_score = {start: 0}  # best known distance from start to each node

    while queue:
        _, node = heapq.heappop(queue)

        if node == target:
            return reconstruct_path(came_from, target), g_score[target]

        # A node can be queued several times; only expand it the first time
        # it comes off the queue (that's when its distance is smallest).
        if node in visited:
            continue
        visited.add(node)

        for neighbour, edge_distance in graph[node]:
            new_g = g_score[node] + edge_distance

            if new_g < g_score.get(neighbour, float("inf")):
                came_from[neighbour] = node
                g_score[neighbour] = new_g
                heapq.heappush(queue, (new_g + heuristic(neighbour), neighbour))

    return None, None


def street_path(path, node_and_street, graph, nodes_list):
    """Turn a node path into street-by-street directions.

    Consecutive segments on the same street are merged and their lengths
    added up. Whenever the street changes, the turn is worked out from the
    bearing of the segment just before the junction and the one just after.
    If the route leaves a street and later returns to it, that street appears
    again as a separate entry.

    Args:
        path: Node IDs from ``a_star_search``.
        node_and_street: Segment-to-street lookup from ``load.get_street_names``.
        graph: Road graph, used to look up each segment's length.
        nodes_list: Node lookup, used to compute bearings.

    Returns:
        ``[[street_name, distance_m, turn], ...]``. The first entry's turn is
        ``"start"``; the rest are values from ``load.determine_turn``.
    """
    directions = []
    previous = None

    for node1, node2 in zip(path, path[1:]):
        street_name = node_and_street.get((node1, node2))
        distance = next(
            (length for neighbour, length in graph[node1] if neighbour == node2),
            0,
        )

        if not directions:
            directions.append([street_name, distance, "start"])
        elif directions[-1][0] == street_name:
            directions[-1][1] += distance
        else:
            angle_in = load.calculate_bearing(nodes_list[previous], nodes_list[node1])
            angle_out = load.calculate_bearing(nodes_list[node1], nodes_list[node2])
            directions.append([street_name, distance, load.determine_turn(angle_in, angle_out)])

        previous = node1

    return directions
