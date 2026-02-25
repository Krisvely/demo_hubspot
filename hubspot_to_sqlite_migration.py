import requests
import sqlite3
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# =========================
# LOAD ENV (token seguro)
# =========================
load_dotenv()

HUBSPOT_TOKEN = os.getenv("HUBSPOT_TOKEN")
if not HUBSPOT_TOKEN:
    raise ValueError("HUBSPOT_TOKEN not found in .env file or environment variables")


# =========================
# CONFIG
# =========================
BASE_URL = "https://api.hubapi.com"
CONTACTS_URL = f"{BASE_URL}/crm/v3/objects/contacts"

HEADERS = {
    "Authorization": f"Bearer {HUBSPOT_TOKEN}",
    "Content-Type": "application/json"
}

DB_FILE = "target_crm_demo.db"

# =========================
# DB SETUP (Target CRM Simulado)
# =========================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS crm_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source_system TEXT NOT NULL,
            source_contact_id TEXT NOT NULL UNIQUE,
            full_name TEXT,
            email TEXT NOT NULL,
            migrated_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

# =========================
# EXTRACT (HubSpot API)
# =========================
def fetch_hubspot_contacts(limit=100):
    params = {
        "limit": limit,
        "properties": "firstname,lastname,email"
    }

    response = requests.get(CONTACTS_URL, headers=HEADERS, params=params, timeout=30)

    print(f"GET /contacts -> Status: {response.status_code}")

    if response.status_code != 200:
        try:
            print(json.dumps(response.json(), indent=2))
        except Exception:
            print(response.text)
        return []

    data = response.json()
    return data.get("results", [])

# =========================
# TRANSFORM
# =========================
def transform_contact(raw_contact):
    props = raw_contact.get("properties", {}) or {}

    first = (props.get("firstname") or "").strip()
    last = (props.get("lastname") or "").strip()
    email = (props.get("email") or "").strip().lower()


    if not email or "@" not in email:
        return None

    full_name = f"{first} {last}".strip()
    if not full_name:
        full_name = "(No Name)"

    transformed = {
        "source_system": "HubSpot",
        "source_contact_id": str(raw_contact.get("id")),
        "full_name": full_name,
        "email": email,
        "migrated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z"
    }

    return transformed

# =========================
# LOAD (SQLite)
# =========================
def insert_contact(conn, contact):
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO crm_contacts (
                source_system,
                source_contact_id,
                full_name,
                email,
                migrated_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            contact["source_system"],
            contact["source_contact_id"],
            contact["full_name"],
            contact["email"],
            contact["migrated_at"]
        ))
        return "inserted"
    except sqlite3.IntegrityError:
        return "duplicate"

# =========================
# RUN MIGRATION
# =========================
def run():
    print("\n=== HubSpot -> SQLite Demo (INSERT only) ===\n")
    init_db()

    raw_contacts = fetch_hubspot_contacts(limit=100)

    if not raw_contacts:
        print("No contacts found in HubSpot. Seed data first.")
        return

    print(f"Raw contacts fetched: {len(raw_contacts)}")

    transformed_contacts = []
    skipped = 0

    for raw in raw_contacts:
        t = transform_contact(raw)
        if t is None:
            skipped += 1
            continue
        transformed_contacts.append(t)

    print(f"Transformed contacts: {len(transformed_contacts)}")
    print(f"Skipped invalid contacts: {skipped}")

    inserted = 0
    duplicates = 0

    conn = sqlite3.connect(DB_FILE)
    try:
        for contact in transformed_contacts:
            result = insert_contact(conn, contact)
            if result == "inserted":
                inserted += 1
            elif result == "duplicate":
                duplicates += 1

        conn.commit()

        cur = conn.cursor()
        cur.execute("""
            SELECT id, source_contact_id, full_name, email, migrated_at
            FROM crm_contacts
            ORDER BY id DESC
            LIMIT 10
        """)
        rows = cur.fetchall()

    finally:
        conn.close()

    print("\n=== Migration Summary ===")
    print(f"Inserted: {inserted}")
    print(f"Duplicates skipped: {duplicates}")
    print(f"Invalid skipped: {skipped}")
    print(f"Target DB: {DB_FILE}")

    print("\n=== Sample rows in target CRM ===")
    for row in rows:
        print(row)

if __name__ == "__main__":
    run()