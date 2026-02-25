import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
if not HUBSPOT_TOKEN:
    raise ValueError("HUBSPOT_TOKEN not found in .env file or environment variables")

url = "https://api.hubapi.com/crm/v3/objects/contacts"

headers = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

params = {
    "limit": 5,
    "properties": "firstname,lastname,email"
}

response = requests.get(url, headers=headers, params=params)

print("Status Code:", response.status_code)

if response.status_code == 200:
    print(json.dumps(response.json(), indent=4))
else:
    print("Error:", response.text)