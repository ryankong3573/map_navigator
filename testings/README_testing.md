# testings/

The test suite for the `navigator` package, written with [pytest](https://docs.pytest.org/).

## About these files

The test files and `test_data.json` were generated with the help of **Claude** (Anthropic's AI assistant) to save time on writing test boilerplate. All code in this folder has been read, understood and approved by me before use. The code being tested (everything in `navigator/` and `main.py`) was written by me.

## What's here

| File | What it tests |
|---|---|
| `test_data.json` | A tiny hand-checkable map: 7 nodes, 5 ways, in the same format as the real Overpass data |
| `test_load.py` | Loading the JSON, the node lookup, haversine distance, building the graph (neighbours, one-way roads, filtering out non-car roads) and the edge → street-name lookup |
| `test_routing.py` | `get_nearest_node` (snapping a point to the closest drivable node), `reconstruct_path` and A* search: known shortest routes, the one-way detour, no-route cases, and a check that every route between every pair of nodes only uses real roads |
| `test_directions.py` | `calculate_bearing` (compass direction between two points), `determine_turn` (left / right / straight / U-turn) and `street_path` (turning a node path into street-by-street directions with turns) |

## The test map

North is up. Each gap is about 55.5 m.

```
            7
            :  (footway, filtered out of the graph)
            3 -- 6
            |    ^  (one-way, 4 -> 6 only)
       5 -- 2 -- 4
            |
            1
```

| Way | Nodes | Name | Type | Notes |
|---|---|---|---|---|
| 101 | 1, 2, 3 | Test Road North-South | residential | |
| 102 | 5, 2, 4 | Test Road East-West | residential | crosses 101 at node 2 |
| 103 | 4, 6 | Test One-Way | residential | `oneway = yes` |
| 104 | 6, 3 | Test Lane | unclassified | |
| 105 | 3, 7 | (none) | footway | not drivable, so excluded |

It's small enough to work out every expected answer by hand, but it still covers a crossroads, dead ends, a one-way road that forces a detour (6 → 4 has to go 6 → 3 → 2 → 4), and a node a car can't reach (7).

## Running the tests

From the `map_navigator` folder, with the virtual environment active:

```
source venv/bin/activate
pytest
```

Useful options:

```
pytest -v                      # list every test by name
pytest testings/test_routing.py   # run just one file
pytest -k oneway               # run only tests with "oneway" in the name
```

A dot means a test passed, `F` means it ran and gave the wrong answer, and `E` means it couldn't start (usually a setup problem, like a missing file or a broken import).
