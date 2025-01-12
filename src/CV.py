from azure.storage.blob import BlobServiceClient

from dotenv import load_dotenv
import os

load_dotenv()
connection_string = os.getenv("CONNECTION_STRING")

blob_service_client = BlobServiceClient.from_connection_string(connection_string)

container_name = "uploads"


def upload_image_to_blob(file_object, blob_name):
    try:
        # Get the BlobClient for the specified container and blob
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

        # Upload the image
        blob_client.upload_blob(file_object, overwrite=True)
        print(f"Image '{blob_name}' uploaded successfully to container '{container_name}'!")

    except Exception as e:
        print(f"An error occurred: {e}")



