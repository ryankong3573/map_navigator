"""
Tests for turn-by-turn directions: calculate_bearing, determine_turn,
and street_path (now returning [street, distance, turn] entries).

Map layout (each gap is about 55.5 m), north is up:

            7
            :  (footway, filtered out of the graph)
            3 -- 6
            |    ^  (one-way, 4 -> 6 only)
       5 -- 2 -- 4
            |
            1

Run with:  pytest
"""

import os
import sys

import pytest

# --- Make load.py, routing.py and test_data.json findable ---
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE) if os.path.basename(HERE) == "testings" else HERE
sys.path.insert(0, PROJECT)

import load  # noqa: E402
import routing  # noqa: E402


def find_test_data():
    for folder in (HERE, PROJECT):
        path = os.path.join(folder, "test_data.json")
        if os.path.exists(path):
            return path
    raise FileNotFoundError("Put test_data.json in map_navigator/ or map_navigator/testings/")


# --- Shared setup ---
@pytest.fixture(scope="module")
def data():
    return load.convert_to_dict(find_test_data())


@pytest.fixture(scope="module")
def nodes(data):
    return load.create_list_of_nodes(data)


@pytest.fixture(scope="module")
def graph(data, nodes):
    return load.get_neighbours(data, nodes)


@pytest.fixture(scope="module")
def street_names(data):
    return load.get_street_names(data)


# --- calculate_bearing ---
@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 0),     # north
    (2, 4, 90),    # east
    (2, 1, 180),   # south
    (2, 5, 270),   # west
    (6, 3, 270),   # west (along Test Lane)
    (3, 2, 180),   # south
    (1, 4, 45),    # diagonal, north-east
])
def test_bearing_compass_directions(nodes, a, b, expected):
    assert load.calculate_bearing(nodes[a], nodes[b]) == pytest.approx(expected, abs=0.2)


def test_bearing_is_between_0_and_360(nodes):
    for a in nodes:
        for b in nodes:
            if a != b:
                bearing = load.calculate_bearing(nodes[a], nodes[b])
                assert 0 <= bearing < 360, f"bearing {a}->{b} is {bearing}"


def test_bearing_reverse_is_opposite(nodes):
    forward = load.calculate_bearing(nodes[1], nodes[4])
    backward = load.calculate_bearing(nodes[4], nodes[1])
    assert (backward - forward) % 360 == pytest.approx(180, abs=0.2)


# --- determine_turn ---
@pytest.mark.parametrize("angle_in, angle_out, expected", [
    (0, 90, "turn right"),           # north, then east
    (90, 0, "turn left"),            # east, then north
    (270, 180, "turn left"),         # west, then south
    (180, 270, "turn right"),        # south, then west
    (0, 0, "continue straight"),
    (350, 10, "continue straight"),  # small turn across north
    (10, 350, "continue straight"),
    (0, 45, "turn right"),
    (0, 315, "turn left"),
    (0, 180, "U-turn"),
    (90, 270, "U-turn"),
])
def test_determine_turn(angle_in, angle_out, expected):
    assert load.determine_turn(angle_in, angle_out) == expected


# --- street_path with turns ---
def test_directions_left_then_left(graph, street_names, nodes):
    # 6 -> 3 heads west, turns south at 3 (left), then east at 2 (left)
    result = routing.street_path([6, 3, 2, 4], street_names, graph, nodes)
    assert [(s, t) for s, _, t in result] == [
        ("Test Lane", "start"),
        ("Test Road North-South", "turn left"),
        ("Test Road East-West", "turn left"),
    ]
    for _, metres, _ in result:
        assert metres == pytest.approx(55.5, abs=0.2)


def test_directions_right_turn(graph, street_names, nodes):
    # 5 -> 2 heads east, then south to 1 (right)
    result = routing.street_path([5, 2, 1], street_names, graph, nodes)
    assert [(s, t) for s, _, t in result] == [
        ("Test Road East-West", "start"),
        ("Test Road North-South", "turn right"),
    ]


def test_directions_right_from_north(graph, street_names, nodes):
    # 1 -> 2 heads north, then east to 4 (right)
    result = routing.street_path([1, 2, 4], street_names, graph, nodes)
    assert result[1][0] == "Test Road East-West"
    assert result[1][2] == "turn right"


def test_directions_left_from_north(graph, street_names, nodes):
    # 1 -> 2 heads north, then west to 5 (left)
    result = routing.street_path([1, 2, 5], street_names, graph, nodes)
    assert result[1][0] == "Test Road East-West"
    assert result[1][2] == "turn left"


def test_directions_same_street_merges(graph, street_names, nodes):
    result = routing.street_path([1, 2, 3], street_names, graph, nodes)
    assert len(result) == 1
    street, metres, turn = result[0]
    assert street == "Test Road North-South"
    assert metres == pytest.approx(111.2, abs=0.3)
    assert turn == "start"


def test_directions_single_edge(graph, street_names, nodes):
    result = routing.street_path([4, 6], street_names, graph, nodes)
    assert len(result) == 1
    assert result[0][0] == "Test One-Way"
    assert result[0][2] == "start"


def test_directions_no_movement(graph, street_names, nodes):
    assert routing.street_path([2], street_names, graph, nodes) == []


def test_directions_total_matches_a_star(graph, street_names, nodes):
    path, distance = routing.a_star_search(6, 4, graph, nodes)
    result = routing.street_path(path, street_names, graph, nodes)
    assert sum(metres for _, metres, _ in result) == pytest.approx(distance)


def test_directions_only_first_entry_is_start(graph, street_names, nodes):
    for start in range(1, 7):
        for target in range(1, 7):
            path, _ = routing.a_star_search(start, target, graph, nodes)
            result = routing.street_path(path, street_names, graph, nodes)
            for i, (street, _, turn) in enumerate(result):
                if i == 0:
                    assert turn == "start"
                else:
                    assert turn != "start", f"{start}->{target}: entry {i} says 'start'"


def test_directions_no_repeated_streets(graph, street_names, nodes):
    for start in range(1, 7):
        for target in range(1, 7):
            path, _ = routing.a_star_search(start, target, graph, nodes)
            result = routing.street_path(path, street_names, graph, nodes)
            for (a, _, _), (b, _, _) in zip(result, result[1:]):
                assert a != b, f"{start}->{target}: '{a}' listed twice in a row"