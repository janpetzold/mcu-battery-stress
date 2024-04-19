import os
import json
from datetime import datetime

# Path to the directory containing the JSON files
directory_path = 'messages'

# Prepare an empty list to hold the merged data
merged_data = []

# List all files in the directory, sorted by modification date ascending
files = sorted(os.listdir(directory_path), key=lambda x: os.path.getmtime(os.path.join(directory_path, x)))

# Iterate over each file
for filename in files:
    if filename.endswith('.json'):
        file_path = os.path.join(directory_path, filename)
        
        # Get the modification date of the file
        mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()

        # Open and read the content of the file
        with open(file_path, 'r', encoding='utf-8') as file:
            content = json.load(file)
            # Append the content to the merged_data list, including the modification date
            merged_data.append({"timestamp": mod_time, "payload": content})

# Path for the output file
output_path = './messages/messages.json'

# Write the merged data to a new JSON file
with open(output_path, 'w', encoding='utf-8') as output_file:
    json.dump(merged_data, output_file, ensure_ascii=False, indent=4)

# Move to subdirectory
#os.rename("./messages.json", "./messages/messages.json")

print(f"Merged JSON saved to {output_path}.")