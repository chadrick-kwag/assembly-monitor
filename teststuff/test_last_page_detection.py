import sys
import os
import unittest
from unittest.mock import patch, MagicMock

# Add the src directory to the path so we can import opinion_scraper
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from opinion_scraper.scraper import get_last_page_number, BASE_URL
import requests

class TestLastPageDetection(unittest.TestCase):

    def test_get_last_page_number_success(self):
        """
        Test that get_last_page_number correctly extracts the last page number
        from a mocked HTML response.
        """
        mock_html = """
        <html><body>
            <div class="paginate">
                <a href="?pageIndex=1&blockStartPage=1">1</a>
                <a href="?pageIndex=2&blockStartPage=1">2</a>
                <span>...</span>
                <a href="?pageIndex=10&blockStartPage=1">10</a>
                <a href="?pageIndex=11&blockStartPage=1">11</a>
                <a href="?pageIndex=200&blockStartPage=1">200</a>
                <a href="?pageIndex=201&blockStartPage=1">맨끝</a>
            </div>
        </body></html>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = mock_html.encode('utf-8')
            mock_get.return_value = mock_response

            last_page = get_last_page_number(delay=0) # Set delay to 0 for tests
            self.assertEqual(last_page, 201)
            mock_get.assert_called_once_with(f"{BASE_URL}/gcom/nsmLmSts/out")

    def test_get_last_page_number_no_pagination(self):
        """
        Test that get_last_page_number returns 0 if no pagination links are found.
        """
        mock_html = """
        <html><body>
            <div>No pagination here</div>
        </body></html>
        """
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.return_value = None
            mock_response.content = mock_html.encode('utf-8')
            mock_get.return_value = mock_response

            last_page = get_last_page_number(delay=0)
            self.assertEqual(last_page, 0)

    def test_get_last_page_number_request_error(self):
        """
        Test that get_last_page_number returns 0 on a request error.
        """
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Test error")
            last_page = get_last_page_number(delay=0)
            self.assertEqual(last_page, 0)

if __name__ == '__main__':
    unittest.main()
