import xml.etree.ElementTree as ET
import json
import os
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def parse_body(body):
    """
    Extracts structured transaction fields from the SMS body text
    using regex patterns matched to the MoMo message format.
    """
    result = {
        "transaction_type": None,
        "amount":           None,
        "currency":         "RWF",
        "sender":           None,
        "receiver":         None,
        "counterpart_phone": None,
        "transaction_date": None,
        "new_balance":      None,
        "transaction_id":   None,
    }

    body_lower = body.lower()

    # --- Transaction type + sender/receiver ---
    if "received" in body_lower:
        result["transaction_type"] = "incoming"
        match = re.search(
            r"received ([\d,]+) RWF from (.+?) \((\*+\d+)\).*?at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
            body
        )
        if match:
            result["amount"]           = int(match.group(1).replace(",", ""))
            result["sender"]           = match.group(2).strip()
            result["counterpart_phone"] = match.group(3)
            result["transaction_date"] = match.group(4)

    elif "payment" in body_lower or "transferred" in body_lower:
        result["transaction_type"] = "outgoing"
        match = re.search(
            r"payment of ([\d,]+) RWF to (.+?) \((\*+\d+)\).*?at (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})",
            body
        )
        if match:
            result["amount"]           = int(match.group(1).replace(",", ""))
            result["receiver"]         = match.group(2).strip()
            result["counterpart_phone"] = match.group(3)
            result["transaction_date"] = match.group(4)

    # --- New balance ---
    balance_match = re.search(r"new balance[:\s]*([\d,]+) RWF", body, re.IGNORECASE)
    if balance_match:
        result["new_balance"] = int(balance_match.group(1).replace(",", ""))

    # --- Financial Transaction ID ---
    txid_match = re.search(r"Financial Transaction Id[:\s]*(\d+)", body, re.IGNORECASE)
    if txid_match:
        result["transaction_id"] = txid_match.group(1)

    return result


def parse_sms_xml(filepath):
    """
    Reads the XML file and converts each <sms> record
    into a Python dictionary. Returns a list of all records.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    transactions = []

    for index, sms in enumerate(root.findall("sms")):
        body   = sms.get("body", "")
        parsed = parse_body(body)

        record = {
            "id":            index + 1,
            "address":       sms.get("address", ""),
            "date":          sms.get("date", ""),
            "readable_date": sms.get("readable_date", ""),
            "type":          sms.get("type", ""),
            "body":          body,
            # Fields extracted from body text
            "transaction_type":  parsed["transaction_type"],
            "amount":            parsed["amount"],
            "currency":          parsed["currency"],
            "sender":            parsed["sender"],
            "receiver":          parsed["receiver"],
            "counterpart_phone": parsed["counterpart_phone"],
            "transaction_date":  parsed["transaction_date"],
            "new_balance":       parsed["new_balance"],
            "transaction_id":    parsed["transaction_id"],
        }
        transactions.append(record)

    return transactions


def save_to_folder(data, output_folder, filename="sms_parsed.json"):
    """
    Saves the parsed data as a JSON file into the specified output folder.
    Creates the folder if it does not already exist.
    """
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, filename)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved to: {output_path}")
    return output_path


if __name__ == "__main__":
    INPUT_FILE    = os.path.join(BASE_DIR, "..", "data", "raw", "modified_sms_v2.xml")
    OUTPUT_FOLDER = os.path.join(BASE_DIR, "..", "data", "processed")

    print("Looking for:", os.path.abspath(INPUT_FILE))
    print("File found: ", os.path.exists(INPUT_FILE))

    data = parse_sms_xml(INPUT_FILE)
    print(f"\nTotal records loaded: {len(data)}")
    print("\nFirst record:")
    print(json.dumps(data[0], indent=2))

    save_to_folder(data, OUTPUT_FOLDER)