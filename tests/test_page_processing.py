import pytest
from unittest.mock import MagicMock, patch, mock_open
import os
import sys # Import sys
# import sqlite3 # Import sqlite3 to mock its connect method

# Add the parent directory to the Python path to allow importing from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from src.opinion_scraper.scraper import process_post, BASE_URL, PDF_DOWNLOAD_HEADERS_TEMPLATE

# Path to the sample HTML file
SAMPLE_HTML_PATH = 'tests/resources/20260107194927.html'

@pytest.fixture
def mock_requests_get():
    """Mocks requests.get to return content from the sample HTML file."""
    with patch('requests.get') as mock_get:
        # Mock HTML response
        with open(SAMPLE_HTML_PATH, 'r', encoding='utf-8') as f:
            mock_html_content = f.read()
        
        # Mock PDF response
        mock_pdf_content = b'%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj 2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000010 00000 n\n0000000057 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n106\n%%EOF' # A minimal valid PDF structure

        def side_effect(url, headers=None, stream=False):
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            if 'detailRP' in url:
                mock_response.content = mock_html_content
            elif '/better/atchFile/download/' in url:
                mock_response.content = mock_pdf_content
                mock_response.headers = {'Content-Disposition': 'attachment; filename="test_document.pdf"'}
                mock_response.iter_content.return_value = [mock_pdf_content]
            return mock_response
        
        mock_get.side_effect = side_effect
        yield mock_get

@pytest.fixture
def mock_database():
    """Mocks the database interactions."""
    # Patch the database module as it's imported in scraper.py
    with patch('src.opinion_scraper.scraper.database') as mock_db:
        # Mock get_db_connection which is called internally by database functions
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_db.get_db_connection.return_value = mock_conn
        
        # Mock cursor.fetchone to return None for get_post_by_url (simulates not downloaded)
        mock_cursor.fetchone.return_value = None

        # Ensure get_post_by_url on the mock_db returns None
        mock_db.get_post_by_url.return_value = None
        
        yield mock_db

@pytest.fixture
def mock_filesystem():
    """Mocks filesystem operations like os.makedirs and open."""
    with patch('os.makedirs') as mock_makedirs, \
         patch('os.path.exists', return_value=False), \
         patch('builtins.open', new_callable=mock_open) as mock_builtin_open, \
         patch('os.getenv') as mock_getenv:
        
        # Mock for PDF_DOWNLOAD_DIR and SQLITE_DB_PATH
        mock_getenv.side_effect = lambda key, default=None: {
            "PDF_DOWNLOAD_DIR": "downloads",
            "SQLITE_DB_PATH": "/tmp/test_db.sqlite" 
        }.get(key, default)
        
        yield mock_makedirs, mock_builtin_open

def test_process_post_new_html_pattern(mock_requests_get, mock_database, mock_filesystem):
    """
    Tests if process_post correctly extracts legislation info and downloads PDF
    for the new HTML pattern.
    """
    post_url = f"{BASE_URL}/gcom/nsmLmSts/out/2200001/detailRP"
    download_dir = "teststuff/temp_downloads"
    
    process_post(post_url, download_dir, delay=0) # Set delay to 0 for tests

    # Assert requests.get was called for the post page
    mock_requests_get.assert_any_call(post_url)

    # Assert legislation info was extracted and updated
    mock_database.update_post_legislation_info.assert_called_once_with(
        post_url, 
        '2200001',
        '2024. 5. 30.'
    )

    # Assert os.makedirs was called for the download directory
    mock_filesystem[0].assert_called_once_with(download_dir)

    # Assert requests.get was called for the PDF download
    # The seq from the HTML is 7844645
    expected_pdf_url = f"{BASE_URL}/better/atchFile/download/7844645"
    
    # Prepare expected headers, dynamically adding Referer
    expected_headers = PDF_DOWNLOAD_HEADERS_TEMPLATE.copy()
    expected_headers['Referer'] = post_url

    # We need to explicitly check the call with stream=True and headers
    mock_requests_get.assert_any_call(
        expected_pdf_url, 
        headers=expected_headers, 
        stream=True
    )
    
    # Assert open was called to write the PDF
    mock_builtin_open = mock_filesystem[1]
    mock_builtin_open.assert_called_once_with(os.path.join(download_dir, 'test_document.pdf'), 'wb')
    handle = mock_builtin_open()
    handle.write.assert_called_once()
    
    # Assert database was updated with download status
    # The relative path should be 'test_document.pdf' if PDF_DOWNLOAD_DIR is 'downloads'
    # Recalculate expected_db_pdf_path based on os.path.relpath behavior
    expected_db_pdf_path = os.path.relpath(os.path.join(download_dir, 'test_document.pdf'), "downloads")
    mock_database.update_post_download_status.assert_called_once_with(
        post_url, 
        expected_db_pdf_path
    )