# MoMo API Documentation

**Base URL:** `http://localhost:8000`  
**Authentication:** Basic Auth (see section below)  
**Response Format:** JSON  

---

## Authentication

All endpoints require Basic Authentication. Include the following header with every request:

```
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

Or pass credentials directly with curl:

```
-u admin:password123
```

Requests with missing or incorrect credentials will receive a `401 Unauthorized` response.

---

## Endpoints

### 1. GET /transactions

Returns all transactions in the dataset.

**Request**
```
GET /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**curl example**
```bash
curl.exe -u admin:password123 http://localhost:8000/transactions
```

**Response — 200 OK**
```json
[
  {
    "id": 1,
    "address": "M-Money",
    "date": "1715351458724",
    "readable_date": "10 May 2024 4:30:58 PM",
    "type": "1",
    "body": "You have received 2000 RWF from Jane Smith...",
    "transaction_type": "incoming",
    "amount": 2000,
    "currency": "RWF",
    "sender": "Jane Smith",
    "receiver": null,
    "counterpart_phone": "*********013",
    "transaction_date": "2024-05-10 16:30:51",
    "new_balance": 2000,
    "transaction_id": "76662021700"
  }
]
```

**Error Responses**

| Code | Meaning |
|------|---------|
| 401  | Missing or invalid credentials |

---

### 2. GET /transactions/{id}

Returns a single transaction matching the given ID.

**Request**
```
GET /transactions/1
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**curl example**
```bash
curl.exe -u admin:password123 http://localhost:8000/transactions/1
```

**Response — 200 OK**
```json
{
  "id": 1,
  "address": "M-Money",
  "date": "1715351458724",
  "readable_date": "10 May 2024 4:30:58 PM",
  "type": "1",
  "body": "You have received 2000 RWF from Jane Smith...",
  "transaction_type": "incoming",
  "amount": 2000,
  "currency": "RWF",
  "sender": "Jane Smith",
  "receiver": null,
  "counterpart_phone": "*********013",
  "transaction_date": "2024-05-10 16:30:51",
  "new_balance": 2000,
  "transaction_id": "76662021700"
}
```

**Error Responses**

| Code | Meaning |
|------|---------|
| 400  | ID is not a number |
| 401  | Missing or invalid credentials |
| 404  | No transaction found with that ID |

---

### 3. POST /transactions

Adds a new transaction record to the dataset.

**Request**
```
POST /transactions
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json
```

**Required fields**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | number | Transaction amount |
| `transaction_type` | string | `"incoming"` or `"outgoing"` |
| `sender` | string | Name of the sender |
| `receiver` | string | Name of the receiver |

**curl example**
```bash
curl.exe -u admin:password123 -X POST http://localhost:8000/transactions -H "Content-Type: application/json" -d '{\"amount\": 5000, \"transaction_type\": \"incoming\", \"sender\": \"John Doe\", \"receiver\": \"Me\", \"currency\": \"RWF\"}'
```

**Response — 201 Created**
```json
{
  "amount": 5000,
  "transaction_type": "incoming",
  "sender": "John Doe",
  "receiver": "Me",
  "currency": "RWF",
  "id": 1692
}
```

**Error Responses**

| Code | Meaning |
|------|---------|
| 400  | Invalid JSON body or missing required fields |
| 401  | Missing or invalid credentials |

---

### 4. PUT /transactions/{id}

Updates one or more fields on an existing transaction.

**Request**
```
PUT /transactions/1
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
Content-Type: application/json
```

**curl example**
```bash
curl.exe -u admin:password123 -X PUT http://localhost:8000/transactions/1 -H "Content-Type: application/json" -d '{\"amount\": 9999, \"sender\": \"Updated Sender\"}'
```

**Response — 200 OK**
```json
{
  "id": 1,
  "address": "M-Money",
  "date": "1715351458724",
  "readable_date": "10 May 2024 4:30:58 PM",
  "type": "1",
  "body": "You have received 2000 RWF from Jane Smith...",
  "transaction_type": "incoming",
  "amount": 9999,
  "currency": "RWF",
  "sender": "Updated Sender",
  "receiver": null,
  "counterpart_phone": "*********013",
  "transaction_date": "2024-05-10 16:30:51",
  "new_balance": 2000,
  "transaction_id": "76662021700"
}
```

**Error Responses**

| Code | Meaning |
|------|---------|
| 400  | ID is not a number or invalid JSON body |
| 401  | Missing or invalid credentials |
| 404  | No transaction found with that ID |

---

### 5. DELETE /transactions/{id}

Removes a transaction from the dataset and returns the deleted record.

**Request**
```
DELETE /transactions/1
Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
```

**curl example**
```bash
curl.exe -u admin:password123 -X DELETE http://localhost:8000/transactions/1
```

**Response — 200 OK**
```json
{
  "message": "Transaction 1 deleted.",
  "deleted": {
    "id": 1,
    "address": "M-Money",
    "date": "1715351458724",
    "readable_date": "10 May 2024 4:30:58 PM",
    "type": "1",
    "body": "You have received 2000 RWF from Jane Smith...",
    "transaction_type": "incoming",
    "amount": 2000,
    "currency": "RWF",
    "sender": "Jane Smith",
    "receiver": null,
    "counterpart_phone": "*********013",
    "transaction_date": "2024-05-10 16:30:51",
    "new_balance": 2000,
    "transaction_id": "76662021700"
  }
}
```

**Error Responses**

| Code | Meaning |
|------|---------|
| 400  | ID is not a number |
| 401  | Missing or invalid credentials |
| 404  | No transaction found with that ID |

---

## Error Code Summary

| Code | Status | Triggered When |
|------|--------|----------------|
| 200  | OK | Successful GET, PUT, or DELETE |
| 201  | Created | Successful POST |
| 400  | Bad Request | Non-numeric ID or malformed JSON body |
| 401  | Unauthorized | Missing, incorrect, or malformed credentials |
| 404  | Not Found | Transaction ID does not exist or endpoint does not exist |
