import load, routing, geocode

def confirm_locations():
    done = False
    while(not done):
        location_found = False
        while(not location_found):
            user_location = geocode.get_user_location()
            result = geocode.return_location_node(user_location)

            if result != None:
                loc_lat,loc_lon,location = result
                print(location)
                if (input("Is this your location? [Y/N]: ")).upper() == "Y":
                    location_found = True
            else:
                print("Couldn't find that place please try again")

        destination_found = False
        while(not destination_found):
            user_location = geocode.get_user_destination()
            result = geocode.return_location_node(user_location)

            if result != None:
                des_lat,des_lon,destination = result
                print(destination)
                if (input("Is this your destination? [Y/N]: ")).upper() == "Y":
                    destination_found = True
            else:
                print("Couldn't find that place please try again")           

        a_to_b = (loc_lat, loc_lon), (des_lat, des_lon)
        return a_to_b
        

    

if __name__ == "__main__":
    location, destination = confirm_locations()

    #Data setup for route navigation 
    raw_data = load.convert_to_dict("map_data.json") 
    list_of_nodes = load.create_list_of_nodes(raw_data) #Contains every single node with the latitudes and longitudes of each node
    node_graphs = load.get_neighbours(raw_data, list_of_nodes) #Contains each node's neigbouring nodes and the distance between them
    nodes_and_streets = load.get_street_names(raw_data) #Contains pairs of nodes and the street that they are on

    #Form the routing path from location to destination
    location = routing.get_nearest_node(location[0],location[1],list_of_nodes,node_graphs)
    destination = routing.get_nearest_node(destination[0], destination[1],list_of_nodes,node_graphs)

    path, distance = routing.a_star_search(location,destination,node_graphs,list_of_nodes)
    street_path = routing.street_path(path,nodes_and_streets,node_graphs,list_of_nodes)

    for street_name, distance_to_travel, turn in street_path:
        print(f"{turn} at {street_name}:{distance_to_travel:.2f}m")
    print(f"distance:{(distance/1000):.2f}km")