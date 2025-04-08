import requests
import sys
import json

BASE_URL = "http://localhost:8000"

def test_root():
    try:
        response = requests.get(f"{BASE_URL}")
        if response.status_code == 200:
            print(f"✅ Root endpoint: {response.status_code}")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Root endpoint error: {str(e)}")

def test_statistics():
    try:
        response = requests.get(f"{BASE_URL}/placement/statistics")
        if response.status_code == 200:
            print(f"✅ Statistics endpoint: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Statistics endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Statistics endpoint error: {str(e)}")

def test_items():
    try:
        response = requests.get(f"{BASE_URL}/placement/items/")
        if response.status_code == 200:
            print(f"✅ Items endpoint: {response.status_code}")
            print(f"Number of items: {len(response.json())}")
        else:
            print(f"❌ Items endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Items endpoint error: {str(e)}")

def test_containers():
    try:
        response = requests.get(f"{BASE_URL}/placement/containers/")
        if response.status_code == 200:
            print(f"✅ Containers endpoint: {response.status_code}")
            print(f"Number of containers: {len(response.json())}")
        else:
            print(f"❌ Containers endpoint failed: {response.status_code}")
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ Containers endpoint error: {str(e)}")

if __name__ == "__main__":
    print("Testing API endpoints...")
    print("-" * 50)
    test_root()
    print("-" * 50)
    test_statistics()
    print("-" * 50)
    test_items()
    print("-" * 50)
    test_containers() 