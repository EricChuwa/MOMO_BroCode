import sys
import os
import time

# Import our parser to get real data
sys.path.append(os.path.join(os.path.dirname(__file__), "../api"))
from parser import parse_sms_xml

# Load all transactions as a list
XML_PATH = os.path.join(os.path.dirname(__file__), "../data/raw/modified_sms_v2 (2).xml")
transactions_list = parse_sms_xml(XML_PATH)

# Build a dictionary version for fast lookup
transactions_dict = {t["id"]: t for t in transactions_list}


def linear_search(transactions, target_id):
    # This function scans every record one by one from the beginning
    # until it finds the one with the matching ID
    for transaction in transactions:
        if transaction["id"] == target_id:
            return transaction
    return None


