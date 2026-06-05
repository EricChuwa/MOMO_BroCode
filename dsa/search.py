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


def dictionary_lookup(transactions, target_id):
    # This function jumps directly to the record using the ID as a key
    # No scanning needed — it goes straight to the answer
    return transactions.get(target_id, None)


def measure_time(func, *args):
    # This function measures how long another function takes to run
    # We run it 1000 times and take the average to get an accurate reading
    start = time.perf_counter()
    for _ in range(1000):
        func(*args)
    end = time.perf_counter()
    return (end - start) / 1000


# Test IDs — we test early, middle, and late records to be fair
test_ids = [1, 100, 500, 845, 1200, 1500, 1691]

print("DSA Comparison: Linear Search vs Dictionary Lookup")
print("=" * 60)
print(f"{'ID':<10} {'Linear (ms)':<20} {'Dict (ms)':<20} {'Faster by'}")
print("-" * 60)

for target_id in test_ids:
    linear_time = measure_time(linear_search, transactions_list, target_id)
    dict_time = measure_time(dictionary_lookup, transactions_dict, target_id)

    linear_ms = linear_time * 1000
    dict_ms = dict_time * 1000

    if dict_ms > 0:
        speedup = linear_ms / dict_ms
        faster = f"{speedup:.1f}x"
    else:
        faster = "∞"

    print(f"{target_id:<10} {linear_ms:<20.6f} {dict_ms:<20.6f} {faster}")

print("-" * 60)
print("\nConclusion:")
print("Dictionary lookup is faster because Python dictionaries use")
print("a hash table internally. This means finding any record takes")
print("the same amount of time regardless of how many records exist.")
print("Linear search gets slower as the list grows because it may")
print("need to scan every single record before finding the right one.")
 