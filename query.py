import requests
import json

query = """
[out:json][timeout:60];
way["highway"](3.03495,101.73048,3.05507,101.76292);
out geom;
"""
url = "https://overpass-api.de/api/interpreter"
payload = {"data":query}
headers = {"User-Agent":"my_project v0.1"}

response = requests.get(url, params=payload, headers=headers, timeout=60)

if response.status_code == 200:
    print("OK")
    data = response.json()
    with open("map_data.json", "w") as f:
        json.dump(data, f, indent=2)

else:
    print(f"ERROR! {response.status_code}")

