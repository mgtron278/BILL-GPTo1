import logging
import json
import requests
from azure.storage.blob import BlobServiceClient
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from io import BytesIO
import numpy as np
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Replace with your Azure Cognitive Services Form Recognizer API key and endpoint
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_API_KEY = os.getenv("FORM_RECOGNIZER_API_KEY")

# Initialize Form Recognizer Client
form_recognizer_client = DocumentAnalysisClient(
    endpoint=FORM_RECOGNIZER_ENDPOINT,
    credential=AzureKeyCredential(FORM_RECOGNIZER_API_KEY)
)

connection_string = os.getenv("CONNECTION_STRING")
container_name = "uploads"

def process_receipt(blob_name):
    # Initialize BlobServiceClient
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
    
    # Download the image from Blob Storage
    blob_data = blob_client.download_blob()
    image_data = blob_data.readall()

    # Use Form Recognizer to analyze the document (receipt)
    poller = form_recognizer_client.begin_analyze_document("prebuilt-receipt", image_data)
    result = poller.result()

    extracted_data = extract_receipt_details(result)

    extracted_data2 = json.dumps(extracted_data, indent=4)
    

    save_extracted_data_to_blob(blob_name, extracted_data2)

    return extracted_data2

    

def extract_receipt_details(result):
    # Initialize the output JSON
    extracted_data = {
        "store_details": {},
        "transaction_details": {},
        "purchased_items": [],
        "pricing": {}
    }

    # Extract store details
    document = result.documents[0]
    fields = document.fields

    extracted_data["store_details"] = {
        "name": fields.get("MerchantName").value if "MerchantName" in fields else "",
        "phone": fields.get("MerchantPhoneNumber").value if "MerchantPhoneNumber" in fields else ""
    }

    # Extract transaction details
    extracted_data["transaction_details"] = {
        "date": str(fields.get("TransactionDate").value) if "TransactionDate" in fields else "",
        "time": str(fields.get("TransactionTime").value) if "TransactionTime" in fields else "",
        "order_number": fields.get("ReceiptID").value if "ReceiptID" in fields else ""
    }

    # Extract purchased items
    items = fields.get("Items")
    if items and items.value_type == "list":
        for item in items.value:
            if item.value_type == "dictionary":
                item_fields = item.value
                extracted_data["purchased_items"].append({
                    "item_name": item_fields.get("Description").value if "Description" in item_fields else "",
                    "quantity": item_fields.get("Quantity").value if "Quantity" in item_fields else 0,
                    "price": item_fields.get("TotalPrice").value if "TotalPrice" in item_fields else 0
                })

    # Extract pricing details
    extracted_data["pricing"] = {
        "subtotal": fields.get("Subtotal").value if "Subtotal" in fields else 0,
        "discount": fields.get("Discount").value if "Discount" in fields else 0,
        "total": fields.get("Total").value if "Total" in fields else 0
    }
    

    return extracted_data
    
    #get_stjson.dumpructured_data_from_openai(extracted_data)
    


def save_extracted_data_to_blob(blob_name, data):
    #create a new blob for JSON data
    output_container = "uploads"
    output_blob_name = blob_name.replace('jpeg', 'json')
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    blob_client = blob_service_client.get_blob_client(container=output_container, blob=output_blob_name)
    
    blob_client.upload_blob(data, overwrite = True)

    print(f"Extracted JSON saved to Blob Storage: {output_blob_name}")

        
    


    


    
    


