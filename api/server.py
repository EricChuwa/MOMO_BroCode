from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64
import sys
import os

# Import our XML parser from the same folder
sys.path.append(os.path.dirname(__file__))
from parser import parse_sms_xml

# Load all transactions from the XML file into memory when the server starts
XML_PATH = os.path.join(
    os.path.dirname(__file__), "../data/raw/modified_sms_v2.xml"
)
transactions = parse_sms_xml(XML_PATH)

# Store transactions in a dictionary so we can find any record instantly by its ID
transactions_dict = {t["id"]: t for t in transactions}

# Track what the next new ID should be when someone adds a record
next_id = max(transactions_dict.keys()) + 1

# These are the only valid login credentials for our API
VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"


def check_auth(handler):
    # This function checks if the request includes the correct username and password
    # It reads the Authorization header, decodes it, and compares to our credentials
    auth_header = handler.headers.get("Authorization", "")

    if not auth_header.startswith("Basic "):
        return False

    encoded = auth_header[len("Basic ") :]
    decoded = base64.b64decode(encoded).decode("utf-8")
    username, password = decoded.split(":", 1)

    return username == VALID_USERNAME and password == VALID_PASSWORD


def send_json(handler, status_code, data):
    # This function sends a JSON response back to the client
    # Every endpoint uses this to return data
    body = json.dumps(data, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class MoMoHandler(BaseHTTPRequestHandler):
    # This class handles every incoming request to our server
    # Each method below handles a different HTTP verb: GET, POST, PUT, DELETE

    def do_GET(self):
        # Reject the request immediately if credentials are wrong
        if not check_auth(self):
            send_json(
                self, 401, {"error": "Unauthorized. Please provide valid credentials."}
            )
            return

        if self.path == "/transactions":
            # Return all transactions as a list
            send_json(self, 200, list(transactions_dict.values()))

        elif self.path.startswith("/transactions/"):
            # Return one transaction matching the ID in the URL
            try:
                record_id = int(self.path.split("/")[-1])
                if record_id in transactions_dict:
                    send_json(self, 200, transactions_dict[record_id])
                else:
                    send_json(
                        self, 404, {"error": f"Transaction {record_id} not found."}
                    )
            except ValueError:
                send_json(self, 400, {"error": "ID must be a number."})

        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_POST(self):
        # Reject if credentials are wrong
        if not check_auth(self):
            send_json(
                self, 401, {"error": "Unauthorized. Please provide valid credentials."}
            )
            return

        if self.path == "/transactions":
            global next_id

            # Read the request body and parse it as JSON
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                new_record = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {"error": "Invalid JSON body."})
                return

            # Assign a unique ID and save the new record
            new_record["id"] = next_id
            transactions_dict[next_id] = new_record
            next_id += 1

            send_json(self, 201, new_record)
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_PUT(self):
        # Reject if credentials are wrong
        if not check_auth(self):
            send_json(
                self, 401, {"error": "Unauthorized. Please provide valid credentials."}
            )
            return

        if self.path.startswith("/transactions/"):
            try:
                record_id = int(self.path.split("/")[-1])
            except ValueError:
                send_json(self, 400, {"error": "ID must be a number."})
                return

            if record_id not in transactions_dict:
                send_json(self, 404, {"error": f"Transaction {record_id} not found."})
                return

            # Read and parse the update data from the request body
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                updated_fields = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {"error": "Invalid JSON body."})
                return

            # Apply the updates to the existing record
            transactions_dict[record_id].update(updated_fields)
            transactions_dict[record_id]["id"] = record_id

            send_json(self, 200, transactions_dict[record_id])
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_DELETE(self):
        # Reject if credentials are wrong
        if not check_auth(self):
            send_json(
                self, 401, {"error": "Unauthorized. Please provide valid credentials."}
            )
            return

        if self.path.startswith("/transactions/"):
            try:
                record_id = int(self.path.split("/")[-1])
            except ValueError:
                send_json(self, 400, {"error": "ID must be a number."})
                return

            if record_id not in transactions_dict:
                send_json(self, 404, {"error": f"Transaction {record_id} not found."})
                return

            # Remove the record and return it as confirmation
            deleted = transactions_dict.pop(record_id)
            send_json(
                self,
                200,
                {"message": f"Transaction {record_id} deleted.", "deleted": deleted},
            )
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def log_message(self, format, *args):
        # Print a clean log line each time a request comes in
        print(f"  [{self.address_string()}] {format % args}")


# Start the server on port 8000 and keep it running until Ctrl+C
if __name__ == "__main__":
    PORT = 8000
    server = HTTPServer(("localhost", PORT), MoMoHandler)
    print(f"MoMo API running at http://localhost:{PORT}")
    print(f"Loaded {len(transactions_dict)} transactions")
    print(f"Press Ctrl+C to stop\n")
    server.serve_forever()
