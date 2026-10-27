import json

def convert_to_dict(json_file):
    with open(json_file,"r") as file:
        data = json.load(file)
    return data

def create_list_of_nodes(data):
    dictionary = {}
    for ways in data["elements"]:
        for node, coordinates in zip(ways["nodes"], ways["geometry"]):
            dictionary[node] = coordinates
    return dictionary

data = convert_to_dict("map_data.json")
nodes_list = create_list_of_nodes(data)

