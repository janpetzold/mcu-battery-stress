# Needs install
#
# pip3 install paho-mqtt azure-storage-blob python-dotenv
#
# Make sure to open port 1883 on VM. Afterwards add it as systemd service (see README) so
# it automatically runs in the background even when closing/disconnecting a session and rebooting
#

import paho.mqtt.client as mqtt
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

# Azure Storage Account settings
connect_str = os.getenv('AZURE_STORAGE_CONNECT_STRING')
container_name = 'mqtthq-storage-container'

# MQTT Broker settings
mqtt_broker = 'broker.emqx.io'
mqtt_port = 1883 
mqtt_topic = 'batteryhub/status'

# Connect to Azure Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client(container_name)

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(mqtt_topic)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload} on topic {msg.topic}")
    
    now = datetime.now()
    formatted_now = now.strftime("%Y-%m-%d-%H-%M")
    
    # Create the blob name using the formatted date and time
    #blob_name = f"{formatted_now}.json"
    
    # Create a blob client using the local file name as the name for the blob
    #blob_client = container_client.get_blob_client(blob_name)

    #print(f"Uploading to Azure Storage as blob: {blob_name}")
    
    # Upload the created file
    #blob_client.upload_blob(msg.payload)

# Create an MQTT client and attach our routines to it.
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1)
client.on_connect = on_connect
client.on_message = on_message

client.connect(mqtt_broker, mqtt_port, 60)

# Blocking call that processes network traffic, dispatches callbacks and handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a manual interface.
client.loop_forever()