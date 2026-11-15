import requests

url = "https://nominatim.openstreetmap.org/search"

#This function returns the lat, lon and name of the user's typed location ("NOT ALWAYS ACCURATE")
def return_location_node(user_location):
    params ={
        "q":user_location,
        "limit":1,
        "countrycodes":"my",
        "viewbox":"101.68336,3.10803,101.81314,3.02756",
        "bounded":1,
        "format":"json"
    }

    headers = {"User-Agent":"my_project v0.1"}

    response = requests.get(url=url, params=params, headers=headers, timeout=60)
    if response.status_code == 200:
        print("OK")
        data = response.json()

        if data == []:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"]), data[0]["display_name"]

    else:
        print(f"ERROR! {response.status_code}")  

if __name__ == "__main__":
    pass