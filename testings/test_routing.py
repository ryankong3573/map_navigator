"""
Tests for routing.py using the tiny map in test_data.json.

Map layout (each gap is about 55.5 m):

            7
            :  (footway, filtered out of the graph)
            3 -- 6
            |    ^  (one-way, 4 -> 6 only)
       5 -- 2 -- 4
            |
            1

Assumes a_star_search returns (path, distance) when a route exists,
and None when there is no route.

Run with:  pytest
"""

import os
import sys

import pytest

# --- Make load.py, routing.py and test_data.json findable ---
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE) if os.path.basename(HERE) == "testings" else HERE
sys.path.insert(0, PROJECT)

import load 
import routing 


def find_test_data():
    for folder in (HERE, PROJECT):
        path = os.path.join(folder, "test_data.json")
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Put test_data.json in map_navigator/ or map_navigator/testings/")


# --- Shared setup: build the test graph once ---
@pytest.fixture(scope="module")
def data():
    return load.convert_to_dict(find_test_data())


@pytest.fixture(scope="module")
def nodes(data):
    return load.create_list_of_nodes(data)


@pytest.fixture(scope="module")
def graph(data, nodes):
    return load.get_neighbours(data, nodes)


def edge_length(graph, a, b):
    """Distance of the road a -> b, or None if there is no such road."""
    for neighbour, dist in graph.get(a, []):
        if neighbour == b:
            return dist
    return None


# --- reconstruct_path ---
def test_reconstruct_path_simple():
    came_from = {1: None, 2: 1, 3: 2}
    assert routing.reconstruct_path(came_from, 3) == [1, 2, 3]


def test_reconstruct_path_start_only():
    assert routing.reconstruct_path({5: None}, 5) == [5]


# --- A* routes with a single correct answer ---
ROUTES = [
    # (start, target, expected path, expected metres)
    (5, 1, [5, 2, 1], 111.1),
    (5, 3, [5, 2, 3], 111.1),
    (4, 6, [4, 6], 55.6),
    (6, 4, [6, 3, 2, 4], 166.6),   # one-way forces the long way round
]


@pytest.mark.parametrize("start, target, expected_path, expected_m", ROUTES)
def test_route_path(graph, nodes, start, target, expected_path, expected_m):
    result = routing.a_star_search(start, target, graph, nodes)
    assert result is not None, f"no route found from {start} to {target}"
    path, _ = result
    assert path == expected_path


@pytest.mark.parametrize("start, target, expected_path, expected_m", ROUTES)
def test_route_distance(graph, nodes, start, target, expected_path, expected_m):
    _, distance = routing.a_star_search(start, target, graph, nodes)
    assert distance == pytest.approx(expected_m, abs=0.5)


def test_route_to_itself(graph, nodes):
    path, distance = routing.a_star_search(2, 2, graph, nodes)
    assert path == [2]
    assert distance == pytest.approx(0)


def test_no_route_to_filtered_node(graph, nodes):
    # node 7 is only on a footway, so a car can't reach it
    assert routing.a_star_search(1, 7, graph, nodes) is None


def test_tied_route_has_correct_distance(graph, nodes):
    # 1 -> 6 has two equally short routes (via 3 or via 4); either is fine
    path, distance = routing.a_star_search(1, 6, graph, nodes)
    assert path in ([1, 2, 3, 6], [1, 2, 4, 6])
    assert distance == pytest.approx(166.7, abs=0.5)


# --- Every returned route should be a real, drivable route ---
ALL_PAIRS = [(a, b) for a in range(1, 7) for b in range(1, 7)]


@pytest.mark.parametrize("start, target", ALL_PAIRS)
def test_every_route_is_valid(graph, nodes, start, target):
    result = routing.a_star_search(start, target, graph, nodes)
    assert result is not None, f"no route found from {start} to {target}"
    path, distance = result

    assert path[0] == start
    assert path[-1] == target

    total = 0
    for a, b in zip(path, path[1:]):
        length = edge_length(graph, a, b)
        assert length is not None, f"route uses {a} -> {b}, which isn't a drivable road"
        total += length

    assert distance == pytest.approx(total), "returned distance doesn't match the roads used"


# --- get_nearest_node ---
def test_nearest_node_right_next_to_node_2(graph, nodes):
    assert routing.get_nearest_node(3.04051, 101.74001, nodes, graph) == 2


def test_nearest_node_exactly_on_node_4(graph, nodes):
    assert routing.get_nearest_node(3.0405, 101.7405, nodes, graph) == 4


def test_nearest_node_skips_footway_node(graph, nodes):
    # right on top of node 7, but 7 isn't drivable, so it should snap to 3
    assert routing.get_nearest_node(3.0415, 101.7400, nodes, graph) == 3