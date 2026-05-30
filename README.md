# MOMO_BroCode
---
By: BroCode 

## Project Description
MoMo Transaction API
A Python REST API that parses MTN Mobile Money (MoMo) SMS transaction data from an XML file
and exposes it through a set of authenticated CRUD endpoints built with Python's standard
`http.server` library. No external frameworks are used.

Core features:
- XML parsing that converts SMS records into JSON objects (list of dictionaries)
- REST API with full CRUD support across 5 endpoints
- Basic Authentication protecting all endpoints (401 returned for invalid credentials)
- In-memory dictionary store for fast transaction lookup
- DSA comparison: linear search vs. dictionary lookup benchmarked across 20+ records

## Scrum Board
Link:: https://trello.com/invite/b/6a008b4a3593a69f4fd9612a/ATTIe362f9a87252009efe3efea66aefc9f153C01865/brocode

## High-Level System Architecture Diagram
<img width="764" height="659" alt="image" src="https://github.com/user-attachments/assets/7ce959c3-321c-46d8-9e6f-df7f902bc158" />



Link:: https://miro.com/welcomeonboard/RXQ2RUtJWkV6U3A4ek1LbFFEdEp5alJVV0Y1cHQzVG1KZHp3d0FkcXdlMk5xLzc4WHhnazhENW9DOUk2YVI1TDNUaFVsc1VsR0hBVDVTSkloMGMzQWhYdmg4cW5IcDJ4dHovcFFXL3FYdDJrWkVCZnVQcXV6czR1VlBIOXpnd09zVXVvMm53MW9OWFg5bkJoVXZxdFhRPT0hdjE=?share_link_id=30492649637

## Team Members: 
- Eric Chuwa
- Albert Afiti
- Raphael Mumo

---

## API Endpoints

All endpoints require Basic Authentication. See [`docs/api_docs.md`](docs/api_docs.md)
for full request/response examples and error codes.

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/transactions` | List all SMS transactions |
| `GET` | `/transactions/{id}` | Retrieve a single transaction by ID |
| `POST` | `/transactions` | Add a new transaction record |
| `PUT` | `/transactions/{id}` | Update an existing transaction |
| `DELETE` | `/transactions/{id}` | Delete a transaction |

---

## Data Structures & Algorithms

The `dsa/` folder implements and benchmarks two search strategies against the parsed
transaction dataset:

- **Linear Search** — iterates through the full list of transactions to find a record by ID. O(n).
- **Dictionary Lookup** — stores transactions in a `{id: transaction}` dictionary and retrieves
  by key directly. O(1) average case.

Both approaches are timed across a minimum of 20 records. Results and a written reflection
on why dictionary lookup outperforms linear search — and suggestions for further improvement —
are included in the PDF report.

---
## Database Design

During week 2 the team moved from a flat XML-parsing script into a fully structured relational database. The goal was to design a schema that can store every MoMo transaction type found in the SMS data, enforce data integrity automatically, and serve clean data to the API and JSON layers being built in parallel.

---

### Schema overview

The database (`momo_brocode`) has six tables organized around a central fact table.

```
Users ──────────────┐
                    ├──► Transactions ──► Transaction_Tags ──► Tags
TransactionCats ────┘         │
                              └──────────────────────────────► SystemLogs
```

| Table | Purpose | Rows (seed) |
|---|---|---|
| `Users` | Every counterparty in the SMS data — account owner, contacts, merchants, agents, banks | 20 |
| `TransactionCategories` | Lookup table of 11 transaction types discovered in the XML | 11 |
| `Transactions` | Main fact table — one row per parsed SMS transaction | 12 |
| `Tags` | Reusable labels for free-form classification | 6 |
| `Transaction_Tags` | Junction table resolving the many-to-many between Transactions and Tags | 8 |
| `SystemLogs` | Pipeline audit log — captures parser events, errors, and trigger-fired warnings | 7 |

**Relationships:**
- A `User` can be the sender on many transactions, and the receiver on many transactions (two separate FK relationships to the same `Users` table)
- A `Transaction` belongs to exactly one `TransactionCategory`
- A `Transaction` can carry many `Tags`, and a `Tag` can apply to many `Transactions` — resolved through `Transaction_Tags`
- A `Transaction` can produce many `SystemLogs` entries

---

### Transaction types supported

Analysis of all 1,691 SMS messages in the dataset identified **11 distinct transaction categories**:

| Category code | Direction | Example SMS pattern |
|---|---|---|
| `INCOMING_TRANSFER` | CREDIT | *"You have received X RWF from..."* |
| `PAYMENT_TO_CODE` | DEBIT | *"TxId: X. Your payment of X RWF to [Name] [Code]..."* |
| `TRANSFER_TO_MOBILE` | DEBIT | *"\*165\*S\*X RWF transferred to [Name] (250...)..."* |
| `BANK_DEPOSIT` | CREDIT | *"\*113\*R\*A bank deposit of X RWF..."* |
| `BANK_TRANSFER_OUT` | DEBIT | *"You have transferred X RWF... imbank.bank..."* |
| `MERCHANT_PAYMENT` | DEBIT | *"\*164\*S\*Y'ello, A transaction of X RWF by [Company]..."* |
| `AIRTIME_PURCHASE` | DEBIT | *"\*162\*TxId:X\*S\*Your payment of X RWF to Airtime..."* |
| `DATA_BUNDLE` | DEBIT | *"Yello!Umaze kugura X(YGB)..."* |
| `CASH_WITHDRAWAL` | DEBIT | *"...via agent: [Agent], withdrawn X RWF..."* |
| `REVERSAL` | NEUTRAL | *"...has been reversed at..."* |
| `FAILED_TRANSACTION` | NEUTRAL | *"\*143\*R\*...failed at..."* |

---

### Data integrity rules

Beyond standard foreign keys, the schema enforces accuracy and security through four custom triggers:

**`trg_validate_tx_parties`** — Rejects any transaction with no counterparty, or where sender and receiver are the same user. This replaces a multi-column CHECK constraint (which MySQL/MariaDB handles more reliably in a trigger).

**`trg_log_failed_or_reversed`** — Automatically writes a `WARNING` entry to `SystemLogs` whenever a transaction with status `FAILED` or `REVERSED` is inserted. No application code needs to remember to log these.

**`trg_validate_tx_date_insert`** — Rejects transaction dates more than 30 days in the future, guarding against SMS parser bugs and clock-skew errors.

**`trg_protect_raw_message`** — Makes the `raw_message` column immutable after insert. This field is the forensic record of the original SMS and must not be editable.

---

### Running the database

```bash
# Clone the repo
git clone https://github.com/EricChuwa/MOMO_BroCode.git
cd MOMO_BroCode

# Run the setup script (creates the database automatically)
mysql -u root -p < database/database_setup.sql

# Verify the setup
mysql -u root -p momo_brocode -e "SHOW TABLES;"
```

> **Requires:** MySQL 8.0+ or MariaDB 10.6+. The script drops and recreates `momo_brocode` on every run — do not point it at a production instance.

---

### Current File structure

```
MOMO_BroCode/
├── api/                        ← REST API server (http.server)
├── dsa/                        ← XML parsing + linear search vs dict lookup
├── database/
│   └── database_setup.sql      ← Full DDL + DML + triggers + views
├── docs/
│   ├── erd_diagram.png         ← Entity Relationship Diagram
│   └── api_docs.md             ← Required endpoint documentation
├── screenshots/            ← curl/Postman test evidence
├── examples/
│   └── json_schemas.json       ← JSON schema examples for each entity
└── README.md
```

---

## Setup & Running Instructions

### Prerequisites
- Python **3.8 or higher** (no external libraries required — uses standard library only)
- The `modified_sms_v2.xml` file placed in the project root

Check your Python version:
```bash
python --version
```

---

### 1. Clone the Repository
```bash
git clone https://github.com/EricChuwa/MOMO_BroCode.git
cd MOMO_BroCode
```

---

### 2. Parse the XML Data
Run the parser to read `modified_sms_v2.xml` and convert SMS records into JSON:
```bash
python dsa/parse_xml.py
```
This will output the parsed transactions and run the DSA comparison (linear search vs. dictionary lookup) with performance measurements.

---

### 3. Start the API Server
```bash
python api/server.py
```
The server starts on **`http://localhost:8000`** by default.

You should see:
```
Server running on http://localhost:8000
Press Ctrl+C to stop.
```

---

### 4. Test the API

All endpoints require **Basic Authentication**.

| Field | Value |
|---|---|
| Username | `admin` |
| Password | `brocode123` |

**Example request using curl:**
```bash
curl -u admin:brocode123 http://localhost:8000/transactions
```

**Example request using Postman:**
- Set Authorization type to **Basic Auth**
- Enter the username and password above
- Send a `GET` request to `http://localhost:8000/transactions`

> NOTE! These are test credentials for development only. See `docs/api_docs.md` for full endpoint documentation and `screenshots/` for test case evidence.
