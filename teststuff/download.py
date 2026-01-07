
import sys
import os
import requests
from datetime import datetime

def download_html(url):
    """
    Downloads the HTML content of a given URL and saves it to a file.

    The file is saved in the 'teststuff/download_htmls' directory with a
    filename based on the current timestamp. The requested URL is added as a
    comment at the top of the HTML file.

    Args:
        url (str): The URL of the webpage to download.
    """
    try:
        # Create the directory if it doesn't exist
        output_dir = 'teststuff/download_htmls'
        os.makedirs(output_dir, exist_ok=True)

        # Fetch the HTML content
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        html_content = response.text

        # Prepare the content to be saved
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = f"{timestamp}.html"
        file_path = os.path.join(output_dir, filename)
        
        url_comment = f"<!-- URL: {url} -->\n"
        content_to_save = url_comment + html_content

        # Save the HTML content to a file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content_to_save)

        print(f"Successfully downloaded and saved HTML from {url} to {file_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading {url}: {e}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python download.py <URL>")
        sys.exit(1)
    
    target_url = sys.argv[1]
    download_html(target_url)
