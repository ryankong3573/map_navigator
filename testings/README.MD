testings/

This folder holds the test suite for load.py.

About these files

test_load.py and test_data.json were generated with the help of Claude (Anthropic's AI assistant) to save time on writing test boilerplate.

All code in this folder has been read, understood, and approved by me before use. The functions being tested (load.py, query.py) were written by me.

What's here
File	Purpose
test_data.json	A tiny 7-node, 5-way map in the same format as the real Overpass data, small enough to check every answer by hand
test_load.py	pytest tests for loading, the node lookup, distance (haversine), neighbours, and one-way handling
Test map
            7
            :  (footway)
            3 -- 6
            |    ^  (one-way, 4 -> 6 only)
       5 -- 2 -- 4
            |
            1

Each gap is about 55.5 m.

Running the tests

From the map_navigator folder, with the virtual environment active:

source venv/bin/activate
pytest

Use pytest -v to see each test by name.