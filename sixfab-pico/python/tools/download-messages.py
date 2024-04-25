# Small helper script to downoad messages from Azure Blob Stoarge that were added after
# certain point in time. Run in WSL.

from azure.storage.blob import BlobServiceClient
from datetime import datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv('AZURE_STORAGE_CONNECT_STRING')
container_name = "mqtthq-storage-container"

blob_service_client = BlobServiceClient.from_connection_string(connection_string)
container_client = blob_service_client.get_container_client(container_name)

# Specify your datetime threshold here (year, month, day, hour, minute, second)
# Make sure to use UTC time if your Blob Storage is using UTC
datetime_threshold = datetime(2024, 3, 26, 3, 0, 0, tzinfo=timezone.utc)

# List all blobs in the container and download the ones created after the datetime_threshold
for blob in container_client.list_blobs():
    if blob.creation_time > datetime_threshold and blob.name.endswith('.json'):
        print(f"Downloading {blob.name}...")
        blob_client = container_client.get_blob_client(blob)
        download_path = os.path.join('messages', blob.name)
        with open(download_path, "wb") as download_file:
            download_file.write(blob_client.download_blob().readall())

         # Set the modification time to the blob's time
        mod_time = blob.creation_time.timestamp()
        os.utime(download_path, (mod_time, mod_time))

print("Download completed.")