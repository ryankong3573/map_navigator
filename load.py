import json
import math

CAR_ROADS = {
    "motorway", "trunk", "primary", "secondary", "tertiary",
    "unclassified", "residential",
    "motorway_link", "trunk_link", "primary_link",
    "secondary_link", "tertiary_link",
    "living_street", "service", "road",
}

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

#This function will return a dictionary of each node as a key and its neigbouring nodes' id and distance as values
def get_neighbours(data, nodes_list):
    neighbour_graph = {}

    #Iterates through every single road in our database
    for way in data["elements"]:

        if way["tags"]["highway"] not in CAR_ROADS:
            continue

        #create a list of nodes in one single way and pair the up with their neigbouring nodes
        nodes = []
        for node in way["nodes"]:
            nodes.append(node)
        paired_nodes = list(zip(nodes,nodes[1:]))

        #create a dictionary of the node in nodes, in each node key stores its neighbours and each of their distance to the key node
        for pairs in paired_nodes:
            node1 = pairs[0]
            node2 = pairs[1]

            node1_coords = nodes_list[node1]
            node2_coords = nodes_list[node2]

            distance_between_nodes = calculate_distance(node1_coords, node2_coords)

            if node1 not in neighbour_graph.keys():
                neighbour_graph[node1] = []
            if node2 not in neighbour_graph.keys():
                neighbour_graph[node2] = []

            if way["tags"].get("oneway") == "yes":
                neighbour_graph[node1].append((node2, distance_between_nodes))

            else:
                neighbour_graph[node1].append((node2, distance_between_nodes))
                neighbour_graph[node2].append((node1,  distance_between_nodes))
                
    return neighbour_graph


if __name__ == "__main__":
    data = convert_to_dict("map_data.json")
    nodes_list = create_list_of_nodes(data)

    for elements in data["elements"]:
        if elements["type"] != "way":
            print(elements["type"])
    print("done")