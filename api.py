from fastapi import FastAPI, HTTPException
import navigator.routing as routing
import navigator.geocode as geocode
import navigator.load as load
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI(title="Map Navigator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],     # allow any page, fine while developing
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/choose_location")
def get_user_locations(user_location:str, user_destination:str):

    location = geocode.return_location_node(user_location)
    if location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    
    destination = geocode.return_location_node(user_destination)
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    
    location_lat, location_lon, location_name = location
    destination_lat, destination_lon, destination_name  = destination

    return (location_lat, location_lon,location_name), (destination_lat,destination_lon,destination_name)

@app.get("/nearest")
def get_nodes(loc_lat: float, loc_lon:float, des_lat:float, des_lon:float):
    location = routing.get_nearest_node(loc_lat,loc_lon,list_of_nodes,node_graphs)
    destination = routing.get_nearest_node(des_lat,des_lon,list_of_nodes,node_graphs)

    #node ids
    if location is None or destination is None:
        raise HTTPException(status_code=404, detail="Could not find location")
    return location, destination

@app.get("/routing")
def get_route(location: int, destination: int):
    path, distance = routing.a_star_search(location,destination,node_graphs,list_of_nodes)

    if path is None:
        raise HTTPException(status_code=404, detail="route not found")

    node_coordinates = []
    for nodes in path:
        node_coordinates.append([list_of_nodes[nodes]["lat"],list_of_nodes[nodes]["lon"]])
    return node_coordinates


