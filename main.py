# Import necessary libraries
import json
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
import re

# Function to extract and clean body content from an email object
def extract_and_clean_body_content(email_object: Dict) -> Optional[str]:
    """
    Extracts the 'body' content from an email object and cleans the HTML content.

    Args:
    email_object (Dict): A dictionary containing email data.

    Returns:
    Optional[str]: The cleaned text content extracted from the 'body' field, or None if not found.
    """
    try:
        # Check if 'body' and 'content' keys exist in the email object
        if 'body' in email_object and 'content' in email_object['body']:
            body_content = email_object['body']['content']
            # Clean the HTML content using the clean_html_content function
            return clean_html_content(body_content)
        else:
            # Print a message if body content is not found
            print(f"Body content not found for email with subject: {email_object.get('subject', 'No subject')}")
            return None
    except Exception as e:
        # Handle any exceptions that occur during extraction
        print(f"An error occurred while extracting body content: {e}")
        return None

# Function to clean HTML content
def clean_html_content(html_content: str) -> str:
    """
    Cleans the provided HTML content by removing script and style elements 
    and extracting the text.

    This function uses BeautifulSoup to parse the HTML content, removes 
    any <script> and <style> tags, and retrieves the text while preserving 
    line breaks. It then strips leading and trailing whitespace from each 
    line, removes empty lines, and consolidates multiple spaces into a 
    single space in the final cleaned text.

    Args:
        html_content (str): The HTML content to be cleaned.

    Returns:
        str: The cleaned text content extracted from the HTML, with 
        unnecessary whitespace removed.
    """
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(html_content, "lxml")
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    
    # Extract text content
    text = soup.get_text(separator='\n')
    
    # Clean up the extracted text
    lines = (line.strip() for line in text.splitlines())
    non_empty_lines = [line for line in lines if line]
    clean_text = '\n'.join(non_empty_lines)
    
    # Remove extra whitespace and return the cleaned text
    return re.sub(r'\s+', ' ', clean_text).strip()

# Function to process the JSON file containing email data
def process_file(file_path: str) -> List[Dict[str, Optional[str]]]:
    """
    Processes a file containing JSON data from Microsoft Graph API, extracting and cleaning the body content.

    Args:
    file_path (str): Path to the file containing the JSON data.

    Returns:
    List[Dict[str, Optional[str]]]: A list of dictionaries, each containing the extracted content and metadata.
    """
    results = []
    with open(file_path, 'r') as file:
        try:
            # Load JSON data from the file
            data = json.load(file)
            
            # Check if 'value' key exists and is a list
            if 'value' in data and isinstance(data['value'], list):
                # Process each email object in the 'value' list
                for i, email_object in enumerate(data['value']):
                    # Extract and clean the body content
                    cleaned_content = extract_and_clean_body_content(email_object)
                    
                    # Extract sender information
                    sender = email_object.get('sender', {}).get('emailAddress', {})
                    
                    # Append processed email data to results list
                    results.append({
                        "index": i + 1,
                        "subject": email_object.get('subject', 'No subject'),
                        "sender_name": sender.get('name', 'Unknown'),
                        "sender_address": sender.get('address', 'No address'),
                        "cleaned_content": cleaned_content
                    })
            else:
                print("No 'value' array found in the JSON data.")
        except json.JSONDecodeError as e:
            # Handle JSON decoding errors
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            # Handle any other unexpected errors
            print(f"An unexpected error occurred: {e}")

    return results

# Main execution block
if __name__ == "__main__":
    # Specify the path to the JSON file
    file_path = 'paste.txt'
    
    # Process the file and get the results
    processed_results = process_file(file_path)

    # Print the processed results
    for result in processed_results:
        print(f"\n--- Email {result['index']} ---")
        print(f"Subject: {result['subject']}")
        print(f"Sender: {result['sender_name']} <{result['sender_address']}>")
        print("Cleaned Content:")
        print(result['cleaned_content'])
        print("-" * 50)