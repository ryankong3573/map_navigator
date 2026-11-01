import load
import heapq

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

def reconstruct_path(came_from, target):
    path = []
    current = target

    while current != None:
        path.append(current)
        current = came_from[current]

    path.reverse()
    return path


def a_star_search(start,target,graph,nodes_list):
    queue = [(load.calculate_distance(nodes_list[start],nodes_list[target]), start)]
    visited = set()
    came_from = {
        start:None
    }
    g_score ={
        start:0
    }

    while len(queue) != 0:
        _ , node = heapq.heappop(queue)

        if node == target:
            return reconstruct_path(came_from, target), g_score[target]
        
        if node not in visited:
            visited.add(node)

            for neighbour, edge_distance in graph[node]:
                new_g = g_score[node] + edge_distance

                if new_g < g_score.get(neighbour,float("inf")):
                    came_from[neighbour] = node
                    g_score[neighbour] = new_g
                    f = new_g + load.calculate_distance(nodes_list[neighbour],nodes_list[target])
                    heapq.heappush(queue, (f,neighbour))

    return None

    