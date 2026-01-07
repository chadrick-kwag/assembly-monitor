import os
import sys
from unittest.mock import patch, Mock
import requests

# Add project root to path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.opinion_scraper.scraper import download_pdf, refresh_session

# URL from the HTML file, to be mocked
post_url_to_mock = 'https://opinion.lawmaking.go.kr/gcom/nsmLmSts/out/2215850/detailRP'
# Path to the local HTML file provided by the user
html_file_path = 'teststuff/teststuff/download_htmls/20260107_130449_833278.html'
# Keep a reference to the original requests.get function
original_requests_get = requests.get

def patched_requests_get(url, *args, **kwargs):
    """
    This function replaces requests.get during the test.
    If the URL matches the post_url we want to mock, it returns a mock
    response containing the local HTML content.
    Otherwise, it calls the original requests.get to perform a real HTTP request
    (e.g., for downloading the actual PDF).
    """
    if url == post_url_to_mock:
        print(f"Mocking requests.get for URL: {url}")
        try:
            with open(html_file_path, 'rb') as f:
                html_content = f.read()
            
            mock_response = Mock()
            mock_response.content = html_content
            mock_response.raise_for_status.return_value = None
            mock_response.status_code = 200
            return mock_response
        except FileNotFoundError:
            print(f"Error: HTML file not found at {html_file_path}")
            # Return a failed response to prevent the test from hanging
            mock_response = Mock()
            mock_response.raise_for_status.side_effect = requests.exceptions.RequestException("File not found")
            return mock_response
    
    print(f"Calling original requests.get for URL: {url}")
    return original_requests_get(url, *args, **kwargs)


@patch('src.opinion_scraper.scraper.requests.get', side_effect=patched_requests_get)
def main(mock_get):
    """
    Main function to run the PDF download test.
    The @patch decorator replaces requests.get in the scraper module with our patched_requests_get.
    """
    download_dir = 'teststuff/'

    print("--- Starting PDF download test ---")
    print(f"Using HTML file: {html_file_path}")
    print(f"Saving PDF to: {download_dir}")

    refresh_session()
    
    # Call the download function. The first requests.get call inside it will be mocked.
    download_pdf(post_url_to_mock, download_dir, delay=0)
    
    print("--- PDF download test finished ---")

if __name__ == "__main__":
    main()
