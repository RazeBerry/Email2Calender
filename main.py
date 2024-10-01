import json
from typing import List, Optional, Dict
from bs4 import BeautifulSoup
import re
from datetime import datetime, timezone

def extract_and_clean_body_content(email_object: Dict) -> Optional[str]:
    """
    Extracts the 'body' content from an email object and cleans the HTML content.
    
    Args:
    email_object (Dict): A dictionary containing email data.
    
    Returns:
    Optional[str]: The cleaned text content extracted from the 'body' field, or None if not found.
    """
    try:
        if 'body' in email_object and 'content' in email_object['body']:
            body_content = email_object['body']['content']
            return clean_html_content(body_content)
        else:
            print(f"Body content not found for email with subject: {email_object.get('subject', 'No subject')}")
            return None
    except Exception as e:
        print(f"An error occurred while extracting body content: {e}")
        return None

def clean_html_content(html_content: str) -> str:
    """Helper function to clean HTML content."""
    soup = BeautifulSoup(html_content, "lxml")
    for script_or_style in soup(["script", "style"]):
        script_or_style.decompose()
    text = soup.get_text(separator='\n')
    lines = (line.strip() for line in text.splitlines())
    non_empty_lines = [line for line in lines if line]
    clean_text = '\n'.join(non_empty_lines)
    return re.sub(r'\s+', ' ', clean_text).strip()

def parse_datetime(datetime_str: str) -> str:
    """
    Parses the datetime string and returns a formatted string.
    
    Args:
    datetime_str (str): A string representing a datetime in ISO format.
    
    Returns:
    str: A formatted datetime string.
    """
    try:
        dt = datetime.fromisoformat(datetime_str.rstrip('Z')).replace(tzinfo=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S %Z")
    except ValueError:
        return "Unknown"

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
            data = json.load(file)
            if 'value' in data and isinstance(data['value'], list):
                for i, email_object in enumerate(data['value']):
                    cleaned_content = extract_and_clean_body_content(email_object)
                    sender = email_object.get('sender', {}).get('emailAddress', {})
                    sent_time = parse_datetime(email_object.get('sentDateTime', ''))
                    results.append({
                        "index": i + 1,
                        "subject": email_object.get('subject', 'No subject'),
                        "sender_name": sender.get('name', 'Unknown'),
                        "sender_address": sender.get('address', 'No address'),
                        "sent_time": sent_time,
                        "cleaned_content": cleaned_content
                    })
            else:
                print("No 'value' array found in the JSON data.")
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
    
    return results

# Example usage
if __name__ == "__main__":
    file_path = 'paste.txt'
    processed_results = process_file(file_path)
    
    for result in processed_results:
        print(f"\n--- Email {result['index']} ---")
        print(f"Subject: {result['subject']}")
        print(f"Sender: {result['sender_name']} <{result['sender_address']}>")
        print(f"Sent Time: {result['sent_time']}")
        print("Cleaned Content:")
        print(result['cleaned_content'])
        print("-" * 50)