async function health_check(){
    const response = await fetch("/health");
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
        const data = await response.json()
        return data
    }
}

const map = L.map("map").setView([3.0738,101.7350],14)
let currentLine = null
let startPoint = null
let endPoint = null
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map)


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

    resultText.textContent = `Location Found`
    
    //get the nodes' id
    const locAnddesNode = await get_nearest_node(result[1][0],result[1][1],result[0][0],result[0][1]) //returns location, destination node id
    const route = await get_route(locAnddesNode[0],locAnddesNode[1])

    if(!route){
        resultText.textContent = "Could not find a route"
        return
    }
    if(currentLine || startPoint || endPoint){
        currentLine.remove()
        startPoint.remove()
        endPoint.remove()
    }
    currentLine = L.polyline(route, {color: "blue", weight:5}).addTo(map)
    startPoint = L.circleMarker(route[0], {radius:8, color:"green", fillColor: "green", fillOpacity:1}).addTo(map).bindPopup("Start")
    endPoint = L.circleMarker(route.at(-1), {radius:8, color:"green", fillColor: "red", fillOpacity:1}).addTo(map).bindPopup("End")
    map.fitBounds(currentLine.getBounds())
})


