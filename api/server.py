from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import base64
import sys
import os

sys.path.append(os.path.dirname(__file__))
from parser import parse_sms_xml

XML_PATH = os.path.join(os.path.dirname(__file__), "../data/raw/modified_sms_v2.xml")
transactions = parse_sms_xml(XML_PATH)

transactions_dict = {t["id"]: t for t in transactions}
next_id = max(transactions_dict.keys()) + 1

VALID_USERNAME = "admin"
VALID_PASSWORD = "password123"


def check_auth(handler):
    auth_header = handler.headers.get("Authorization", "")

    if not auth_header.startswith("Basic "):
        return False

    try:
        encoded = auth_header[len("Basic "):]
        decoded = base64.b64decode(encoded).decode("utf-8")
        username, password = decoded.split(":", 1)
        return username == VALID_USERNAME and password == VALID_PASSWORD
    except Exception:
        return False


def send_json(handler, status_code, data):
    body = json.dumps(data, indent=2).encode("utf-8")
    handler.send_response(status_code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def send_unauthorized(handler):
    body = json.dumps({"error": "Unauthorized. Please provide valid credentials."}).encode("utf-8")
    handler.send_response(401)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("WWW-Authenticate", 'Basic realm="MoMo API"')
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class MoMoHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if not check_auth(self):
            send_unauthorized(self)
            return

        if self.path == "/transactions":
            send_json(self, 200, list(transactions_dict.values()))

        elif self.path.startswith("/transactions/"):
            try:
                record_id = int(self.path.split("/")[-1])
                if record_id in transactions_dict:
                    send_json(self, 200, transactions_dict[record_id])
                else:
                    send_json(self, 404, {"error": f"Transaction {record_id} not found."})
            except ValueError:
                send_json(self, 400, {"error": "ID must be a number."})

        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_POST(self):
        if not check_auth(self):
            send_unauthorized(self)
            return

        if self.path == "/transactions":
            global next_id

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                new_record = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {"error": "Invalid JSON body."})
                return

            required_fields = ["amount", "transaction_type", "sender", "receiver"]
            missing = [f for f in required_fields if f not in new_record]
            if missing:
                send_json(self, 400, {"error": f"Missing required fields: {missing}"})
                return

            new_record["id"] = next_id
            transactions_dict[next_id] = new_record
            next_id += 1

            send_json(self, 201, new_record)
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_PUT(self):
        if not check_auth(self):
            send_unauthorized(self)
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

            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                updated_fields = json.loads(body)
            except json.JSONDecodeError:
                send_json(self, 400, {"error": "Invalid JSON body."})
                return

            transactions_dict[record_id].update(updated_fields)
            transactions_dict[record_id]["id"] = record_id

            send_json(self, 200, transactions_dict[record_id])
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def do_DELETE(self):
        if not check_auth(self):
            send_unauthorized(self)
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

            deleted = transactions_dict.pop(record_id)
            send_json(self, 200, {"message": f"Transaction {record_id} deleted.", "deleted": deleted})
        else:
            send_json(self, 404, {"error": "Endpoint not found."})

    def log_message(self, format, *args):
        print(f"  [{self.address_string()}] {format % args}")

    def log_error(self, format, *args):
        pass


if __name__ == "__main__":
    PORT = 8000
    server = HTTPServer(("localhost", PORT), MoMoHandler)
    print(f"MoMo API running at http://localhost:{PORT}")
    print(f"Loaded {len(transactions_dict)} transactions")
    print(f"Press Ctrl+C to stop\n")
    server.serve_forever()