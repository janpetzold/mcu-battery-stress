# Find the duration, median execution time for all downloaded messages
import json
from datetime import datetime
import statistics

# Path to the merged JSON file
merged_json_path = 'messages/messages.json'

# Load the merged JSON data
with open(merged_json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Calculate execution time in total
# Extract timestamps and convert them to datetime objects
timestamps = [datetime.strptime(entry["timestamp"], "%Y-%m-%dT%H:%M:%S") for entry in data]

# Find the earliest and latest timestamps
earliest_timestamp = min(timestamps)
latest_timestamp = max(timestamps)

# Calculate the difference in minutes
difference_in_minutes = round((latest_timestamp - earliest_timestamp).total_seconds() / 60)
print(f"Total runtime was {difference_in_minutes} minutes")

# Extract the 'e' values
e_values = [item['payload']['e'] for item in data if 'e' in item['payload']]

# Calculate the median
if e_values:
    median_e = statistics.median(e_values)
    print(f"Median execution time of a single run was {median_e} seconds")
else:
    print("No 'e' values found.")

messages_via_lte = sum(1 for entry in data if entry["payload"]["n"] == "lte")

print(f"There were {len(data)} messages in total, LTE was used for {messages_via_lte} messages")

timestamps_sorted = sorted(timestamps)

# Calculate the delays between consecutive timestamps in minutes
delays = [(timestamps_sorted[i+1] - timestamps_sorted[i]).total_seconds() / 60 for i in range(len(timestamps_sorted)-1)]

# Count the occurrences where the delay was longer than 23 minutes
# Defined interval is 20mins, typical runtime is ~1min so leave a bit of headroom to indicate drop rate
occurrences_longer_than_23_min = sum(1 for delay in delays if delay > 23)

print(f"Messages were not sent in the defined interval on {occurrences_longer_than_23_min} occasions")