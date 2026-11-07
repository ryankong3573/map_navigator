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
'''
json_file = json file fetched from API
'''
def convert_to_dict(json_file):
    with open(json_file,"r") as file:
        data = json.load(file)
    return data

#This function will create a dictionary of nodes their coordinates as values e.g. node1 : {-321312,421341}
'''
data = raw json data fetched from API converted to a python dictionary
'''
def create_list_of_nodes(data):
    dictionary = {}
    for ways in data["elements"]:
        for node, coordinates in zip(ways["nodes"], ways["geometry"]):
            dictionary[node] = coordinates
    return dictionary

#This function will return the distance of two nodes using haversine's formula
'''
node and neighbour node = two keys that contains the lat and lon of one node
'''
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
'''
data = raw data fetched from API
nodes_list = list of nodes from raw_data containing the nodes and their lon and lat
'''
def get_neighbours(data, nodes_list):
    neighbour_graph = {}

    #Iterates through every single road in our database
    for way in data["elements"]:
        if way["tags"].get("highway") not in CAR_ROADS:
            continue

        #create a list of nodes in one single way and pair the up with their neigbouring nodes
        paired_nodes = zip(way["nodes"],way["nodes"][1:])

        #create a dictionary of the node in nodes, in each node key stores its neighbours and each of their distance to the key node
        for node1, node2 in paired_nodes:
            node1_coords = nodes_list[node1]
            node2_coords = nodes_list[node2]

            distance_between_nodes = calculate_distance(node1_coords, node2_coords)

            neighbour_graph.setdefault(node1, [])
            neighbour_graph.setdefault(node2, [])

            #Meaning A->B but not B->A
            if way["tags"].get("oneway") == "yes":
                neighbour_graph[node1].append((node2, distance_between_nodes))

            else:
                neighbour_graph[node1].append((node2, distance_between_nodes))
                neighbour_graph[node2].append((node1,  distance_between_nodes))
                
    return neighbour_graph 

#This function returns a dictionary of paired nodes and the street name the node is on e.g (1,2):Jalan Damai Perdana
'''
data = raw data fetched from API
'''
def get_street_names(data):
    nodes_and_street ={

    }
    for way in data["elements"]:
        if way["tags"].get("highway") in CAR_ROADS:
            street_name = way["tags"].get("name","unnamed road")

            for node1,node2 in zip(way["nodes"], way["nodes"][1:]):
                nodes_and_street[node1,node2] = street_name

                if way["tags"].get("oneway") != "yes":
                    nodes_and_street[node2,node1] = street_name

    return nodes_and_street

#This function calculates the direction to reach one node to the other
def calculate_bearing(node1, node2):
    lon1 = math.radians(node1["lon"])
    lon2 = math.radians(node2["lon"])
    lat1 = math.radians(node1["lat"])
    lat2 = math.radians(node2["lat"])

    x = math.sin(lon2-lon1) * math.cos(lat2)
    y = math.cos(lat1)*math.sin(lat2) - math.sin(lat1)*math.cos(lat2)*math.cos(lon2-lon1)

    return (math.degrees(math.atan2(x,y)) + 360) % 360 

#This function determines whether the direction requires the person to turn left right straight or make a u-turn
'''
in_angle = the bearing of the first street's last and second last node
out_angle = the bearing of the next street's first and second node
'''
def determine_turn(in_angle, out_angle):
    d = out_angle - in_angle
    turn = ((d+540)%360) - 180

    if -30<=turn<30:
        direction = "continue straight"
    elif 30<=turn<150:
        direction = "turn right"
    elif -150<=turn<-30:
        direction = "turn left"
    else:
        direction = "U-turn"

    return direction 

if __name__ == "__main__":
    data = convert_to_dict("map_data.json")
    nodes_list = create_list_of_nodes(data)
    
    print("done")