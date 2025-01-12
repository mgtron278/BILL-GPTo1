
import os
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json
from typing import Dict, Any
import streamlit as st
from src.extracting_blob import process_receipt


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")




def create_receipt_chain():
    # Initialize the language model
    model = ChatOpenAI(
        temperature=0,  # Set to 0 for more deterministic responses
        model="gpt-3.5-turbo",
        api_key=api_key  # You can change this to gpt-4 if needed
    )
    
    # Create the prompt template using the new format
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that answers questions about receipt data.
        Here is the receipt data in JSON format:
        {receipt_data}
        
        Please provide clear and concise answers based only on the information available in the receipt data."""),
        ("human", "{question}")
    ])
    
    # Create the chain using the new pattern
    chain = prompt | model | StrOutputParser()
    
    return chain

def query_receipt(chain, question: str, receipt_data: Dict[str, Any]) -> str:
    # Format receipt data as a string
    receipt_str = json.dumps(receipt_data, indent=2)
    
    # Run the chain with the new invoke pattern
    response = chain.invoke({
        "receipt_data": receipt_str,
        "question": question
    })
    
    return response

def main(blob_name):
    # Make sure you have set your OpenAI API key
    receipt_data = process_receipt(blob_name)
    # Create the chain
    chain = create_receipt_chain()
    
    # Example questions
    questions = [
        "What items were purchased?",
        "What was the total amount?",
    ]
    
    # Run example queries
    for question in questions:
        print(f"\nQuestion: {question}")
        try:
            response = query_receipt(chain, question, receipt_data)
            print(f"Answer: {response}")
        except Exception as e:
            print(f"Error processing question: {str(e)}")

