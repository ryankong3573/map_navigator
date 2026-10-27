import requests

query = """
[out:json];

way["highway"](3.03495,101.73048,3.05507,101.76292);

(._;>;);
out body;
"""
url = "https://overpass-api.de/api/interpreter"
payload = {"data":query}
headers = {"User-Agent":"my_project v0.1"}

response = requests.post(url, data=payload, headers=headers, timeout=60)

if response.status_code == 200:
    print("OK")
    data = response.json()
else:
    print(f"ERROR! {response.status_code}")

