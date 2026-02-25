import requests
import json
import os
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
if not HUBSPOT_TOKEN:
    raise ValueError("HUBSPOT_TOKEN not found in .env file or environment variables")

BASE_URL = "https://api.hubapi.com"
CONTACTS_URL = f"{BASE_URL}/crm/v3/objects/contacts"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}


TARGET_EMAIL = "ana.demo.001@example.com"


def find_contact_by_email(email: str):
    """
    HubSpot search endpoint to find a contact by email.
    """
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
    print(f"Search contact -> Status: {response.status_code}")

    if response.status_code != 200:
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)
        return None

    data = response.json()
    results = data.get("results", [])
    if not results:
        print(f"No contact found with email: {email}")
        return None

    return results[0]


def update_contact(contact_id: str, new_firstname: str = None, new_lastname: str = None):
    """
    PATCH contact properties in HubSpot
    """
    url = f"{CONTACTS_URL}/{contact_id}"

    properties = {}
    if new_firstname is not None:
        properties["firstname"] = new_firstname
    if new_lastname is not None:
        properties["lastname"] = new_lastname

    if not properties:
        print("No properties provided to update.")
        return None

    payload = {"properties": properties}

    response = requests.patch(url, headers=HEADERS, json=payload, timeout=30)
    print(f"Update contact -> Status: {response.status_code}")

    try:
        body = response.json()
        print(json.dumps(body, indent=2))
    except Exception:
        print(response.text)

    return response


def main():
    print("\n=== HubSpot Update Demo (PATCH) ===\n")

    contact = find_contact_by_email(TARGET_EMAIL)
    if not contact:
        print("\nTip: If you used the seed script with timestamp emails, copy a real email from HubSpot and replace TARGET_EMAIL.")
        return

    contact_id = contact["id"]
    props = contact.get("properties", {}) or {}

    print("Current contact:")
    print(json.dumps({
        "id": contact_id,
        "firstname": props.get("firstname"),
        "lastname": props.get("lastname"),
        "email": props.get("email")
    }, indent=2))

    # Simple update logic (toggle suffix)
    current_lastname = (props.get("lastname") or "").strip()

    if not current_lastname.endswith("_UPDATED"):
        new_lastname = f"{current_lastname}_UPDATED" if current_lastname else "UPDATED"
    else:
        new_lastname = current_lastname.replace("_UPDATED", "")

    print(f"\nApplying update logic -> new lastname: {new_lastname}\n")
    update_contact(contact_id=contact_id, new_lastname=new_lastname)


if __name__ == "__main__":
    main()