import requests
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
if not HUBSPOT_TOKEN:
    raise ValueError("HUBSPOT_TOKEN not found in .env file or environment variables")

BASE_URL = "https://api.hubapi.com"
URL = f"{BASE_URL}/crm/v3/objects/contacts"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

# Timestamp para emails únicos
suffix = datetime.now().strftime("%Y%m%d%H%M%S")

sample_contacts = [
    {"firstname": "Ana", "lastname": "Perez", "email": f"ana.demo.{suffix}@example.com"},
    {"firstname": "Luis", "lastname": "Gomez", "email": f"luis.demo.{suffix}@example.com"},
    {"firstname": "Maria", "lastname": "Silva", "email": f"maria.demo.{suffix}@example.com"}
]

for idx, item in enumerate(sample_contacts, start=1):
    payload = {
        "properties": {
            "firstname": item["firstname"],
            "lastname": item["lastname"],
            "email": item["email"]
        }
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=30)
        print(f"\nContact #{idx} | Status: {response.status_code}")

        try:
            body = response.json()
            print(json.dumps(body, indent=2))
        except Exception:
            print(response.text)

    except requests.RequestException as e:
        print(f"Request failed for contact #{idx}: {e}")