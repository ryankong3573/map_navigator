"""
Tests for load.py using the tiny map in test_data.json.

Map layout (each gap is about 55.5 m):

            7
            :  (footway)
            3 -- 6
            |    ^  (one-way, 4 -> 6 only)
       5 -- 2 -- 4
            |
            1

Run from the map_navigator folder with:  pytest
"""

import os
import sys
import pytest

# --- Make load.py and test_data.json findable, wherever this file lives ---
sys.path.append("..")

import load  

@pytest.fixture(scope="module")
def data():
    path = os.path.join(os.path.dirname(__file__), "test_data.json")
    return load.convert_to_dict(path)

# --- Shared setup: load the test map once for every test ---
@pytest.fixture(scope="module")
def nodes(data):
    return load.create_list_of_nodes(data)


@pytest.fixture(scope="module")
def graph(data, nodes):
    return load.get_neighbours(data, nodes)


def neighbour_ids(graph, node):
    """Just the IDs from a node's (neighbour, distance) list."""
    return [n for n, _ in graph.get(node, [])]


# --- Loading ---
def test_loads_all_five_ways(data):
    assert len(data["elements"]) == 5


# --- Node lookup ---
def test_node_lookup_has_exactly_seven_nodes(nodes):
    assert set(nodes.keys()) == {1, 2, 3, 4, 5, 6, 7}


def test_node_coordinates_are_correct(nodes):
    assert nodes[2]["lat"] == pytest.approx(3.0405)
    assert nodes[2]["lon"] == pytest.approx(101.7400)


# --- Distance ---
def test_distance_north_south(nodes):
    # 0.0005 degrees of latitude is about 55.6 m
    assert load.calculate_distance(nodes[1], nodes[2]) == pytest.approx(55.6, abs=0.1)


def test_distance_east_west(nodes):
    # longitude gaps are very slightly shorter away from the equator
    assert load.calculate_distance(nodes[5], nodes[2]) == pytest.approx(55.52, abs=0.1)


def test_distance_is_same_both_ways(nodes):
    assert load.calculate_distance(nodes[1], nodes[2]) == pytest.approx(
        load.calculate_distance(nodes[2], nodes[1])
    )


def test_distance_to_itself_is_zero(nodes):
    assert load.calculate_distance(nodes[3], nodes[3]) == pytest.approx(0)


def test_distance_known_value():
    # 0.005 degrees of latitude is about 556 m
    a = {"lat": 3.040, "lon": 101.74}
    b = {"lat": 3.045, "lon": 101.74}
    assert load.calculate_distance(a, b) == pytest.approx(556, abs=1)


# --- Graph ---
EXPECTED = {
    1: {2},
    2: {1, 3, 4, 5},   # crossroads
    3: {2, 6, 7},      # joins three ways
    4: {2, 6},         # can drive 4 -> 6
    5: {2},
    6: {3},            # can NOT drive 6 -> 4 (one-way)
    7: {3},
}


@pytest.mark.parametrize("node, expected", EXPECTED.items())
def test_each_node_has_correct_neighbours(graph, node, expected):
    assert set(neighbour_ids(graph, node)) == expected


@pytest.mark.parametrize("node", EXPECTED.keys())
def test_no_duplicate_neighbours(graph, node):
    ids = neighbour_ids(graph, node)
    assert len(ids) == len(set(ids)), f"node {node} has a neighbour listed twice: {ids}"


def test_oneway_allows_forward(graph):
    assert 6 in neighbour_ids(graph, 4)


def test_oneway_blocks_backward(graph):
    assert 4 not in neighbour_ids(graph, 6)


def test_all_edge_distances_are_about_55m(graph):
    for node, edges in graph.items():
        for neighbour, dist in edges:
            assert 55 < dist < 56, f"edge {node} -> {neighbour} is {dist:.1f} m"


