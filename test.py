import requests
import json

url = "https://nzn6xl9x7e.execute-api.us-east-1.amazonaws.com/choose"

payload = {
    "self_fighter": {
        "position": "guard",
        "fatigue": 50,
        "stats": {
            "grappling_iq": 65,
            "strength": 60,
            "agility": 70
        }
    },
    "opponent": {
        "position": "top",
        "fatigue": 70,
        "stats": {
            "grappling_iq": 60,
            "strength": 55,
            "agility": 60
        }
    }
}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, data=json.dumps(payload), headers=headers)
print(response.status_code)
print(response.text)
