const API = "https://map-navigator-fs5f.onrender.com"

async function health_check(){
    const response = await fetch("/health");
    const data = await response.json();
    console.log(data.nodes)
}

//Returns two tuples, containing the location and destination details (lat,lon,name)
async function choose_location(from, to){
    const url = `API/choose_location?user_location=${encodeURIComponent(from)}&user_destination=${encodeURIComponent(to)}`;
    const response = await fetch(url);
    if(response.ok){
        const data = await response.json()
        return [data[0], data[1]]
    }
}

//Will get the nearest nodes's id that best matches the intended location and destination
async function get_nearest_node(des_lat,des_lon,loc_lat,loc_lon){
    const url = `API/nearest?loc_lat=${encodeURIComponent(loc_lat)}&loc_lon=${encodeURIComponent(loc_lon)}&des_lon=${encodeURIComponent(des_lon)}&des_lat=${encodeURIComponent(des_lat)}`;
    const response = await fetch(url)
    if(response.ok){
        const data = await response.json()
        return [data[0],data[1]]
    }
}

//Will return a path from location to destination in a dictionary {"coordinates": contains all ids of each node in path,"distance":distance required to travel in meters}
async function get_route(location,destination){
    const url = `API/routing?location=${encodeURIComponent(location)}&destination=${encodeURIComponent(destination)}`
    const response = await fetch(url)
    if(response.ok){
        const data = await response.json()
        return data 
    }
}

//MAP VIEWS
const map = L.map("map").setView([3.0738,101.7350],14)
const AVG_SPEED = 30
let currentLine = null
let startPoint = null
let endPoint = null
let routeLabel = null

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors"
}).addTo(map)


//Runs when frontend button is clicked
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
    if(currentLine || startPoint || endPoint || routeLabel){
        currentLine.remove()
        startPoint.remove()
        endPoint.remove()
        routeLabel.remove()
    }
    currentLine = L.polyline(route["coordinates"], {color: "blue", weight:5}).addTo(map)
    startPoint = L.circleMarker(route['coordinates'][0], {radius:8, color:"green", fillColor: "green", fillOpacity:1}).addTo(map).bindPopup("Start")
    endPoint = L.circleMarker(route['coordinates'].at(-1), {radius:8, color:"red", fillColor: "red", fillOpacity:1}).addTo(map).bindPopup("End")

    //Place the distance and time in the center of path
    const coords = route["coordinates"]
    const middle = coords[Math.floor(coords.length / 2)]

    let distance_km = (route["distance"] / 1000).toFixed(2)
    let estimate_time = (km / AVG_SPEED).toFixed(2)

    routeLabel = L.tooltip({permanent: true, direction:"top"}).setLatLng(middle).setContent(`${distance_km} km ${estimate_time} h `).addTo(map)
    map.fitBounds(currentLine.getBounds())
})


