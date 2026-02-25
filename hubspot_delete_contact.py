import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
if not HUBSPOT_TOKEN:
    raise ValueError("HUBSPOT_TOKEN not found in .env file or environment variables")

BASE_URL = "https://api.hubapi.com"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

TARGET_EMAIL = "maria.demo.20260225130105@example.com"


def find_contact_by_email(email: str):
    search_url = f"{BASE_URL}/crm/v3/objects/contacts/search"

    payload = {
        "filterGroups": [
            {
                "filters": [
                    {
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email
                    }
                ]
            }
        ],
        "properties": ["firstname", "lastname", "email"],
        "limit": 1
    }

    response = requests.post(search_url, headers=HEADERS, json=payload, timeout=30)
    print(f"Search -> Status: {response.status_code}")

    if response.status_code != 200:
        print(response.text)
        return None

    data = response.json()
    results = data.get("results", [])
    return results[0] if results else None


def delete_contact(contact_id: str):
    url = f"{BASE_URL}/crm/v3/objects/contacts/{contact_id}"
    response = requests.delete(url, headers=HEADERS, timeout=30)

    print(f"Delete -> Status: {response.status_code}")
    if response.status_code == 204:
        print("Contact deleted successfully.")
    else:
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)


def main():
    contact = find_contact_by_email(TARGET_EMAIL)
    if not contact:
        print("No contact found with that email.")
        return

    print("Found contact:")
    print(json.dumps({
        "id": contact["id"],
        "email": contact.get("properties", {}).get("email"),
        "firstname": contact.get("properties", {}).get("firstname"),
        "lastname": contact.get("properties", {}).get("lastname"),
    }, indent=2))

    delete_contact(contact["id"])


if __name__ == "__main__":
    main()