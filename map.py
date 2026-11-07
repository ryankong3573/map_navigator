import folium

def draw_map(node_path, nodes_list):
    node_points = []
    for node_id in node_path:
        coords = nodes_list[node_id]
        node_points.append([coords["lat"],coords["lon"]])
    m = folium.Map(location=node_points[0], zoom_start=16, tiles="https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
        attr="&copy; OpenStreetMap contributors, SRTM | &copy; OpenTopoMap",)
    green = folium.Icon(color="green")
    blue = folium.Icon(color="blue")
    red = folium.Icon(color="red")
    folium.PolyLine(node_points, icon=blue, weight=5, opacity=0.8).add_to(m)
    folium.Marker(node_points[0],icon=green).add_to(m)
    folium.Marker(node_points[-1],icon=red).add_to(m)
    m.save("route.html")

