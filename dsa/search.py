import sys
import os
import time

sys.path.append(os.path.join(os.path.dirname(__file__), "../api"))
from parser import parse_sms_xml

XML_PATH = os.path.join(os.path.dirname(__file__), "../data/raw/modified_sms_v2.xml")
transactions_list = parse_sms_xml(XML_PATH)

transactions_dict = {t["id"]: t for t in transactions_list}


def linear_search(transactions, target_id):
    # Scans every record one by one until it finds the matching ID
    for transaction in transactions:
        if transaction["id"] == target_id:
            return transaction
    return None


def dictionary_lookup(transactions, target_id):
    # Jumps directly to the record using the ID as a key
    return transactions.get(target_id, None)


def measure_time(func, *args):
    # Runs the function 1000 times and returns the average duration
    start = time.perf_counter()
    for _ in range(1000):
        func(*args)
    end = time.perf_counter()
    return (end - start) / 1000


# 20 test IDs spread across early, middle, and late records
test_ids = [
    1, 50, 100, 150, 200, 250, 300, 350, 400, 450,
    500, 600, 700, 800, 900, 1000, 1100, 1200, 1400, 1691
]

print("DSA Comparison: Linear Search vs Dictionary Lookup")
print("=" * 60)
print(f"{'ID':<10} {'Linear (ms)':<20} {'Dict (ms)':<20} {'Faster by'}")
print("-" * 60)

for target_id in test_ids:
    linear_time = measure_time(linear_search, transactions_list, target_id)
    dict_time   = measure_time(dictionary_lookup, transactions_dict, target_id)

    linear_ms = linear_time * 1000
    dict_ms   = dict_time * 1000

    if dict_ms > 0:
        speedup = f"{linear_ms / dict_ms:.1f}x"
    else:
        speedup = "inf"

    print(f"{target_id:<10} {linear_ms:<20.6f} {dict_ms:<20.6f} {speedup}")

print("-" * 60)

print("\nConclusion:")
print(
    "Dictionary lookup is faster because Python dictionaries use a hash table "
    "internally. Finding any record takes the same amount of time (O(1)) regardless "
    "of how many records exist. Linear search is O(n) — it gets slower as the list "
    "grows because it may need to scan every record before finding the right one.\n"
    "This difference becomes significant at scale: searching record 1691 with linear "
    "search requires up to 1691 comparisons, while dictionary lookup always takes one.\n\n"
    "Alternative data structure: a sorted list with binary search would reduce lookup "
    "time to O(log n) — faster than linear search but without needing the extra memory "
    "a dictionary uses. For range queries (e.g. all transactions between two dates), "
    "a Binary Search Tree (BST) would outperform a plain dictionary since dictionaries "
    "have no concept of order."
)