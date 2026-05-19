# MOMO_BroCode
---
By: BroCode 

## Project Description
MoMo Data Analytics Dashboard
A fullstack data pipeline and analytics application that processes MTN Mobile Money (MoMo) SMS transaction data exported in XML format. The system parses, cleans, categorizes, and stores transaction records in a relational database, then exposes the data through a frontend dashboard with charts and summaries for financial analysis.
Core features:

- XML ETL pipeline (parse → clean → categorize → load)
- SQLite database for structured transaction storage
- JSON export layer for frontend consumption
- Interactive dashboard with transaction analytics and visualizations

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
## Database Design (Week 2)

This week the team moved from a flat XML-parsing script into a fully structured relational database. The goal was to design a schema that can store every MoMo transaction type found in the SMS data, enforce data integrity automatically, and serve clean data to the API and JSON layers being built in parallel.

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

### File structure (Week 2 additions)

```
MOMO_BroCode/
├── database/
│   └── database_setup.sql      ← Full DDL + DML + triggers + views
├── docs/
│   └── erd_diagram.png         ← Entity Relationship Diagram
├── examples/
│   └── json_schemas.json       ← JSON schema examples for each entity
└── README.md
```

