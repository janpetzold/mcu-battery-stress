# Find the median execution time for all downloaded messages
import json
import statistics

# Path to the merged JSON file
merged_json_path = 'messages/messages.json'

# Load the merged JSON data
with open(merged_json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Extract the 'e' values
e_values = [item['payload']['e'] for item in data if 'e' in item['payload']]

# Calculate the median
if e_values:
    median_e = statistics.median(e_values)
    print(f"The median value of 'e' is: {median_e}")
else:
    print("No 'e' values found.")