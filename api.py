from fastapi import FastAPI, HTTPException
import navigator.routing as routing
import navigator.geocode as geocode
import navigator.load as load
from fastapi.middleware.cors import CORSMiddleware
import time

app = FastAPI(title="Map Navigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "https://map-navigator-3.onrender.com",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
]
)

raw_data = load.convert_to_dict("map_data.json") 
list_of_nodes = load.create_list_of_nodes(raw_data) #Contains every single node with the latitudes and longitudes of each node
node_graphs = load.get_neighbours(raw_data, list_of_nodes) #Contains each node's neigbouring nodes and the distance between them
nodes_and_streets = load.get_street_names(raw_data) #Contains pairs of nodes and the street that they are on

@app.get("/health")
def info():
    return {
        "status": "ok",
        "nodes": len(node_graphs)
    }

#Returns two tuples, containing the location and destination details (lat,lon,name)
@app.get("/choose_location")
def get_user_locations(user_location:str, user_destination:str):

    location = geocode.return_location_node(user_location)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    time.sleep(1)
    destination = geocode.return_location_node(user_destination)
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    location_lat, location_lon, location_name = location
    destination_lat, destination_lon, destination_name  = destination

    return (location_lat, location_lon,location_name), (destination_lat,destination_lon,destination_name)

#Will get the nearest nodes's id that best matches the intended location and destination
@app.get("/nearest")
def get_nodes(loc_lat: float, loc_lon:float, des_lat:float, des_lon:float):
    location = routing.get_nearest_node(loc_lat,loc_lon,list_of_nodes,node_graphs)
    time.sleep(1)
    destination = routing.get_nearest_node(des_lat,des_lon,list_of_nodes,node_graphs)

    #node ids
    if location is None or destination is None:
        raise HTTPException(status_code=404, detail="Could not find location")
    return location, destination

#Will return a path from location to destination in a dictionary {"coordinates": contains all ids of each node in path,"distance":distance required to travel in meters}
@app.get("/routing")
def get_route(location: int, destination: int):
    path, distance = routing.a_star_search(location,destination,node_graphs,list_of_nodes)

    if path is None:
        raise HTTPException(status_code=404, detail="route not found")

    node_coordinates = []
    for nodes in path:
        node_coordinates.append([list_of_nodes[nodes]["lat"],list_of_nodes[nodes]["lon"]])
    return {"coordinates": node_coordinates, "distance":distance}


