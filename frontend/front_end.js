// Front end for Map Navigator.
//
// Flow when "Find route" is clicked:
//   1. geocode()           typed text      -> [lat, lon, name]   (Nominatim, in the browser)
//   2. get_nearest_node()  two coordinates -> two road node IDs  (backend /nearest)
//   3. get_route()         two node IDs    -> path + distance    (backend /routing)
//   4. draw_route()        path            -> line, markers and a distance/time label on the map

// --- Settings ---

const API = ["localhost", "127.0.0.1"].includes(window.location.hostname)
    ? "http://localhost:8000"
    : "https://map-navigation-wvis.onrender.com"   // no trailing slash: paths below start with "/"

const NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
const VIEWBOX = "101.68336,3.10803,101.81314,3.02756"   // map area (west, north, east, south); must match the backend
const MAP_CENTER = [3.0738, 101.7350]
const MAP_ZOOM = 14
const AVG_SPEED_KMH = 30   // used for the rough travel-time estimate


// --- API calls ---

// Fetches JSON from a URL. Returns null if the request fails or the server returns an error.
async function fetch_json(url) {
    try {
        const response = await fetch(url)
        if (!response.ok) return null
        return await response.json()
    } catch (error) {
        console.error("Request failed:", url, error)
        return null
    }
}

// Looks up a typed address with Nominatim, limited to the map area.
// Returns [lat, lon, display_name], or null if nothing matched.
async function geocode(place) {
    const params = new URLSearchParams({
        q: place,
        limit: 1,
        countrycodes: "my",
        viewbox: VIEWBOX,
        bounded: 1,
        format: "json",
    })
    const data = await fetch_json(`${NOMINATIM_URL}?${params}`)
    if (!data || data.length === 0) return null
    return [Number(data[0].lat), Number(data[0].lon), data[0].display_name]
}

// Geocodes the start and destination.
// Returns [[lat, lon, name], [lat, lon, name]], or null if either can't be found.
async function choose_location(from, to) {
    const loc = await geocode(from)
    await new Promise(resolve => setTimeout(resolve, 1000))   // Nominatim allows about 1 request per second
    const des = await geocode(to)
    if (!loc || !des) return null
    return [loc, des]
}

// Snaps both points to the nearest drivable road node.
// Returns [location_node_id, destination_node_id], or null.
async function get_nearest_node(loc_lat, loc_lon, des_lat, des_lon) {
    const params = new URLSearchParams({ loc_lat, loc_lon, des_lat, des_lon })
    return fetch_json(`${API}/nearest?${params}`)
}

// Finds the shortest route between two node IDs.
// Returns {coordinates: [[lat, lon], ...], distance: metres}, or null.
async function get_route(location, destination) {
    const params = new URLSearchParams({ location, destination })
    return fetch_json(`${API}/routing?${params}`)
}


// --- Map ---

const map = L.map("map").setView(MAP_CENTER, MAP_ZOOM)

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "&copy; OpenStreetMap contributors",
}).addTo(map)

// Everything drawn for the current route, so it can be cleared before drawing the next one.
let routeLayers = []

function clear_route() {
    routeLayers.forEach(layer => layer.remove())
    routeLayers = []
}

// Draws the route line, start/end markers, and a distance/time label in the middle of the route.
function draw_route(route) {
    clear_route()

    const coords = route.coordinates
    const line = L.polyline(coords, { color: "blue", weight: 5 })
    const start = L.circleMarker(coords[0], { radius: 8, color: "green", fillColor: "green", fillOpacity: 1 }).bindPopup("Start")
    const end = L.circleMarker(coords.at(-1), { radius: 8, color: "red", fillColor: "red", fillOpacity: 1 }).bindPopup("End")

    const distanceKm = route.distance / 1000
    const hours = distanceKm / AVG_SPEED_KMH
    const label = L.tooltip({ permanent: true, direction: "top" })
        .setLatLng(coords[Math.floor(coords.length / 2)])
        .setContent(`${distanceKm.toFixed(2)} km ${hours.toFixed(2)} h`)

    routeLayers = [line, start, end, label]
    routeLayers.forEach(layer => layer.addTo(map))
    map.fitBounds(line.getBounds())
}


// --- Button ---

const fromBox = document.getElementById("from")
const toBox = document.getElementById("to")
const goButton = document.getElementById("go")
const statusText = document.getElementById("status")

async function find_route() {
    statusText.textContent = "Searching...."

    const places = await choose_location(fromBox.value, toBox.value)
    if (!places) {
        statusText.textContent = "Could not find that place"
        return
    }
    const [loc, des] = places
    statusText.textContent = "Location Found"

    const nodes = await get_nearest_node(loc[0], loc[1], des[0], des[1])
    if (!nodes) {
        statusText.textContent = "That place is too far from any road on the map"
        return
    }

    const route = await get_route(nodes[0], nodes[1])
    if (!route) {
        statusText.textContent = "Could not find a route"
        return
    }

    draw_route(route)
}

goButton.addEventListener("click", async () => {
    goButton.disabled = true   // stop double clicks from sending a second search
    try {
        await find_route()
    } finally {
        goButton.disabled = false
    }
})
