import xml.etree.ElementTree as ET
import json


def parse_sms_xml(filepath):
    """
    Reads the XML file and converts each <sms> record
    into a Python dictionary. Returns a list of all records.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    transactions = []

    for index, sms in enumerate(root.findall("sms")):
        record = {
            "id": index + 1,
            "address": sms.get("address", ""),
            "date": sms.get("date", ""),
            "type": sms.get("type", ""),
            "body": sms.get("body", ""),
        }
        transactions.append(record)

    return transactions


# Test block — only runs when you run this file directly
if __name__ == "__main__":
    data = parse_sms_xml("../data/raw/modified_sms_v2 (2).xml")
    print(f"Total records loaded: {len(data)}")
    print("\nFirst record:")
    print(json.dumps(data[0], indent=2))
