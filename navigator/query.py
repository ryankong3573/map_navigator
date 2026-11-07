import requests
import json

query = """
[out:json][timeout:240];
way["highway"~"^(motorway|trunk|primary|secondary|tertiary|unclassified|residential|living_street|service|road|motorway_link|trunk_link|primary_link|secondary_link|tertiary_link)$"]
(3.02756,101.68336,3.10803,101.81314);
out geom;
"""

url = "https://overpass-api.de/api/interpreter"
payload = {"data":query}
headers = {"User-Agent":"my_project v0.1"}

try:
    response = requests.post(url, data=payload, headers=headers, timeout=260)
except requests.exceptions.RequestException as e:
    print("Couldnt reach the server", e)
    exit()

if response.status_code == 200:
    print("OK")
    data = response.json() #Turn JSON format into python dictionary
    with open("map_data.json", "w") as f:
        json.dump(data, f)#Save the dictionary into a JSON file 

else:
    print(f"ERROR! {response.status_code}")

