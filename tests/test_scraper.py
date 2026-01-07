import pytest
from bs4 import BeautifulSoup
import os
import sys # Import sys

# Add the parent directory to the Python path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from opinion_scraper.scraper import _extract_legislation_info, _get_pdf_download_url_and_filename, BASE_URL

@pytest.fixture
def sample_html_soup():
    """
    Loads the sample HTML file and returns a BeautifulSoup object.
    """
    html_file_path = 'tests/resources/20260107194927.html'
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    return BeautifulSoup(html_content, 'html.parser')

def test_extract_legislation_info(sample_html_soup):
    """
    Tests the _extract_legislation_info function with sample HTML.
    """
    legislation_number, submission_date = _extract_legislation_info(sample_html_soup)
    assert legislation_number == "2200001"
    assert submission_date == "2024. 5. 30."

def test_get_pdf_download_url_and_filename(sample_html_soup):
    """
    Tests the _get_pdf_download_url_and_filename function with sample HTML.
    """
    pdf_url, file_name = _get_pdf_download_url_and_filename(sample_html_soup)
    expected_pdf_url = f"{BASE_URL}/better/atchFile/download/7844645"

    assert pdf_url == expected_pdf_url