import requests
import json

base_url = "http://localhost:8000"

def query_route(endpoint):
    url = f"{base_url}{endpoint}"
    print(f"\n--- Querying {endpoint} ---")
    try:
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        try:
            print("Response Payload:")
            print(json.dumps(response.json(), indent=4))
        except Exception:
            print("Response Text:")
            print(response.text)
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    query_route("/")
    query_route("/models/status")
    query_route("/models/catalog")
