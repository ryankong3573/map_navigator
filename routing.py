import load

#This function will obtain get the lat and lon of a user's desired location through our API fetch in nominatim then we will get the node existing in our graph
#to find the best match to our desired location according to the distance.
"""
lat, lon = the location of the destination from API fetch
nodes_list = list containing all nodes' location in our bbox (including non roads)
graph = list containing all road nodes' id and  distance to its neigbouring nodes
"""
def get_nearest_node(lat,lon,nodes_list,graph):
    nearest_node = None
    nearest_node_distance = float("inf")
    node_to_match = {
        "lat":lat,
        "lon":lon
    }

    for node in graph:
        distance_to_target = load.calculate_distance(node_to_match,nodes_list[node])
        if nearest_node_distance > distance_to_target:
            nearest_node = node
            nearest_node_distance = distance_to_target
    return nearest_node

