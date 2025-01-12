import streamlit as st
from src.CV import upload_image_to_blob
from src.extracting_blob import process_receipt
from src.my_openai import create_receipt_chain, query_receipt
import os

# Set up the uploaded file directory
UPLOAD_FOLDER = "uploaded_files"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Function to handle image upload and process the receipt
def handle_image_upload():
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        blob_name = uploaded_file.name
        upload_image_to_blob(uploaded_file, blob_name)
        
        
        
        # Step 2: Process the uploaded file
        extracted_json_data = process_receipt(blob_name)
        return extracted_json_data
    return None

def main():
    # Title of the app
    st.title("Receipt Question Answering")

    # Step 1: Upload Image and Process
    st.subheader("Step 1: Upload Receipt Image")
    extracted_json_data = handle_image_upload()

    if extracted_json_data:
        st.success("File uploaded and receipt processed successfully!")
        
        # Step 2: Ask a Question
        st.subheader("Step 2: Ask a Question about the Receipt")
        question = st.text_input("Enter your question:")

        if question:
            # Create the chain and process the question
            chain = create_receipt_chain()
            try:
                answer = query_receipt(chain, question, extracted_json_data)
                st.write(f"**Answer**: {answer}")
            except Exception as e:
                st.error(f"Error processing the question: {str(e)}")
    else:
        st.warning("Please upload a receipt image first!")

if __name__ == "__main__":
    main()
