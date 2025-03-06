import requests
import json

def test_health():
    response = requests.get('http://localhost:5000/api/health')
    print("Health Check Response:", response.json())

def test_recommend():
    data = {'text': 'I am feeling happy and energetic today!'}
    response = requests.post('http://localhost:5000/api/recommend', json=data)
    print("Status Code:", response.status_code)
    print("Response Headers:", response.headers)
    print("Response Text:", response.text)
    try:
        print("Response JSON:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print("Error parsing JSON:", str(e))

if __name__ == '__main__':
    print("Testing API endpoints...")
    test_health()
    print("\nTesting recommendation endpoint...")
    test_recommend() 