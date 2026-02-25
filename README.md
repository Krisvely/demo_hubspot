# HubSpot API Migration Demo (Python)

This project demonstrates a simple end-to-end **data migration and sync workflow** using **HubSpot REST APIs** and **Python**.

---

## Overview

This demo simulates a lightweight migration/integration scenario and showcases:

1. **API connection validation** to HubSpot
2. **Seeding test data** into HubSpot contacts
3. **ETL migration** from HubSpot to a simulated target CRM (**SQLite**)
4. **Contact updates** in HubSpot using `PATCH` (incremental sync scenario)

---

## HTTP Methods Covered

- **GET** → Validate connectivity and extract contacts from HubSpot
- **POST** → Create seed contacts and search contacts by email
- **PATCH** → Update contact properties (incremental change simulation)
- **DELETE** → Optional cleanup (manual in HubSpot or via API cleanup script)

---

## Project Files

### `hubspot_test_connection.py`
    **Purpose:** Validates authentication and connectivity to HubSpot before running migration logic.

    **HubSpot API used:**
    - `GET /crm/v3/objects/contacts`

    **What it does:**
    - Loads the Bearer token from `.env`
    - Sends a test request to HubSpot Contacts API
    - Confirms the API is reachable and returns JSON successfully

---

### `hubspot_seed_contacts.py`
    **Purpose:** Seeds sample data into HubSpot so the source CRM contains records for migration testing.

    **HubSpot API used:**
    - `POST /crm/v3/objects/contacts`

    **What it does:**
    - Creates demo contacts in HubSpot via REST API
    - Uses timestamp-based emails to avoid duplicate conflicts
    - Returns the created records and response status for validation

---

### `hubspot_to_sqlite_migration.py`
    **Purpose:** Simulates an ETL migration flow from HubSpot into a lightweight target CRM (SQLite).

    **HubSpot API used:**
    - `GET /crm/v3/objects/contacts`

    **What it does:**
    - **Extract:** Reads contacts from HubSpot
    - **Transform:** Formats full name, normalizes email, validates basic email structure
    - **Load:** Inserts records into SQLite (`target_crm_demo.db`)
    - Prevents duplicates using a unique `source_contact_id`
    - Prints a migration summary (inserted / duplicates / skipped)

---

### `hubspot_update_contact.py`
    **Purpose:** Demonstrates incremental source changes by updating an existing contact in HubSpot.

    **HubSpot APIs used:**
    - `POST /crm/v3/objects/contacts/search` (search by email)
    - `PATCH /crm/v3/objects/contacts/{contactId}` (update contact properties)

    **What it does:**
    - Finds a contact by email using the HubSpot Search API
    - Retrieves the contact ID
    - Updates one or more fields (e.g. last name)
    - Simulates incremental sync/update behavior in a migration pipeline

---

### Notes
- Seeded demo contacts use timestamp-based emails (for example: `ana.demo.20260225...@example.com`)
- Updated contacts can be verified after running the PATCH script (for example, the last name may become `Perez_UPDATED`)

---

## How to Delete Demo Contacts

### Option 2: Delete via API (Python)
A cleanup script can be used to:
- Search a contact by email
- Retrieve its contact ID
- Delete it using the HubSpot `DELETE` endpoint

This is useful to demonstrate cleanup operations and complete the CRUD flow in the API demo.

### Recommended cleanup strategy
Use a recognizable email pattern (e.g. `@example.com`) in seeded contacts so demo records can be found and removed easily.

---

## Why SQLite Was Used

SQLite was used as a **lightweight target CRM simulation** to demonstrate migration logic (ETL) without adding infrastructure complexity.

This keeps the demo focused on:
- API integration
- Transformation logic
- Validation
- Load behavior

---

## Security Notes

- HubSpot credentials are loaded from `.env`
- Secrets are **not hardcoded** in source code
- `.env` and local database files are excluded via `.gitignore`