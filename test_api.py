import requests
import json
import sys

url = "http://localhost:8000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

def test_non_streaming():
    payload = {
        "model": "openrun",
        "messages": [
            {"role": "user", "content": "Hello! Introduce yourself in one sentence."}
        ],
        "stream": False
    }

    print("\n--- Testing Non-Streaming Mode ---")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        print(f"\nResponse Status Code: {response.status_code}")
        try:
            print("Response Body:")
            print(json.dumps(response.json(), indent=4))
        except Exception:
            print("Raw Response Text:")
            print(response.text)
    except Exception as e:
        print(f"\nConnection failed: {e}")
        print("Please make sure the OpenRun server is currently running on port 8000.")

def test_streaming():
    payload = {
        "model": "openrun",
        "messages": [
            {"role": "user", "content": "Hello! Introduce yourself in one sentence."}
        ],
        "stream": True
    }

    print("\n--- Testing Streaming Mode ---")
    print(f"POST {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, headers=headers, json=payload, stream=True, timeout=30)
        print(f"\nResponse Status Code: {response.status_code}")
        print("Stream Content:")
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                print(decoded_line)
    except Exception as e:
        print(f"\nConnection failed: {e}")
        print("Please make sure the OpenRun server is currently running on port 8000.")

if __name__ == "__main__":
    test_non_streaming()
    test_streaming()
