import xml.etree.ElementTree as ET
import json
import os

# Always resolves paths relative to THIS script's location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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

    # Debug: confirm exactly where Python is looking
    print("Looking for:", os.path.abspath(INPUT_FILE))
    print("File found: ", os.path.exists(INPUT_FILE))

    data = parse_sms_xml(INPUT_FILE)
    print(f"\nTotal records loaded: {len(data)}")
    print("\nFirst record:")
    print(json.dumps(data[0], indent=2))

    save_to_folder(data, OUTPUT_FOLDER)