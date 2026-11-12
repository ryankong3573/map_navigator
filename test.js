async function health_check(){
    const response = await fetch("\health");
    const data = await response.json();
    console.log(data.nodes)
}

async function choose_location(from, to){
    const url = `http://127.0.0.1:8000/choose_location?user_location=${encodeURIComponent(from)}&user_destination=${encodeURIComponent(to)}`;
    const response = await fetch(url);
    if(response.ok){
        const data = await response.json()
        return [data[0], data[1]]
    }
}

async function get_nearest_node(des_lat,des_lon,loc_lat,loc_lon){
    const url = `http://127.0.0.1:8000/nearest?loc_lat=${encodeURIComponent(loc_lat)}&loc_lon=${encodeURIComponent(loc_lon)}&des_lon=${encodeURIComponent(des_lon)}&des_lat=${encodeURIComponent(des_lat)}`;
    const response = await fetch(url)
    if(response.ok){
        const data = await response.json()
        return [data[0],data[1]]
    }
}

async function get_route(location,destination){
    const url = `http://127.0.0.1:8000/routing?location=${encodeURIComponent(location)}&destination=${encodeURIComponent(destination)}`
    const response = await fetch(url)
    if(response.ok){
        const data = response.json()
        return data
    }
}

document.getElementById("go").addEventListener("click", async ()=> {

    //read user's location and destination
    const fromBox = document.getElementById("from")
    const toBox = document.getElementById("to")

    //gets the closest node's coordinates
    const from = fromBox.value;
    const to = toBox.value;
    const result = await choose_location(from,to) //returns (lat,lon,location),(lat,lon,destination)

    //Only runs if the nodes cannot be found
    const resultText = document.getElementById("status")
    if(!result){
        resultText.textContent = "Could not find that place"
        return;
    }

    //Display the name of the actual location and destination
    console.log("done")
    const from_name = result[0][2]
    const to_name = result[1][2]
    resultText.textContent = `Location Found`
    const toText = document.getElementById("to_name")
    const fromText = document.getElementById("from_name")
    toText.innerText = to_name
    document.getElementById("connecter").innerText = "to"
    fromText.innerText = from_name
    

    //get the nodes' id
    const locAnddesNode = await get_nearest_node(result[1][0],result[1][1],result[0][0],result[0][1]) //returns location, destination node id
    const route = await get_route(locAnddesNode[0],locAnddesNode[1])

    document.getElementById("route_status").textContent = route
})



