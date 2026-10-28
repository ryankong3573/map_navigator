import json
import math

#This function converts a json file to a python dictionary
def convert_to_dict(json_file):
    with open(json_file,"r") as file:
        data = json.load(file)
    return data

#This function will create a dictionary of nodes their coordinates as values e.g. node1 : {-321312,421341}
def create_list_of_nodes(data):
    dictionary = {}
    for ways in data["elements"]:
        for node, coordinates in zip(ways["nodes"], ways["geometry"]):
            dictionary[node] = coordinates
    return dictionary

#This function will return the distance of two nodes using haversine's formula
def calculate_distance(node, neighbour_node):
    R =  6371000 #earth's radius in meters
    phi1, phi2 = math.radians(node["lat"]), math.radians(neighbour_node["lat"])
    dphi = math.radians(node["lat"] - neighbour_node["lat"])
    dlambda = math.radians(node["lon"] - neighbour_node["lon"])

    a = (math.sin(dphi/2))**2 + math.cos(phi1)*math.cos(phi2)*((math.sin(dlambda/2))**2)
    b = math.asin(math.sqrt(a))
    c = 2*R*b

    return c

#This 
def get_neighbours(data):
    pass

    


data = convert_to_dict("map_data.json")
nodes_list = create_list_of_nodes(data)

