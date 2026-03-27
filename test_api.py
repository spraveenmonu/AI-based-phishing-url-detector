import requests
import time

def test_api():
    print("Waiting for API to start...")
    url = "http://localhost:8000/predict"
    data = {"url": "http://google.com"}
    
    max_retries = 10
    for i in range(max_retries):
        try:
            response = requests.post(url, json=data)
            if response.status_code == 200:
                print("API is UP!")
                print("Test output for google.com:")
                print(response.json())
                return True
        except requests.exceptions.ConnectionError:
            print(f"Server not ready yet... retry {i+1}")
            time.sleep(2)
    return False

if __name__ == "__main__":
    test_api()
