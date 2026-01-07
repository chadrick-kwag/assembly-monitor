import unittest
from unittest.mock import patch, MagicMock
import os
import requests

from opinion_scraper.scraper import _get_last_page_number

class TestPagination(unittest.TestCase):

    def test_get_last_page_number(self):
        mock_html = """
        <html>
        <body>
            <div class="paginate">
                <a href="?pageIndex=1&amp;blockStartPage=1" class="move first" title="처음페이지">
                    <span class="a11y_hidden">처음페이지</span>
                </a>
                <a href="?pageIndex=774&amp;blockStartPage=771" class="move prev" title="이전10페이지">
                    <span class="a11y_hidden">이전10페이지</span>
                </a>
                <a href="?pageIndex=771&amp;blockStartPage=771" class="on" title="771페이지">
                    <span class="a11y_hidden">771페이지</span>
                </a>
                <a href="?pageIndex=772&amp;blockStartPage=771" title="772페이지">
                    <span class="a11y_hidden">772페이지</span>
                </a>
                <a href="?pageIndex=775&amp;blockStartPage=771" class="move icoCnt_last" title="마지막페이지">
                    <span class="a11y_hidden">마지막페이지</span>
                </a>
            </div>
        </body>
        </html>
        """
        
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = mock_html.encode('utf-8')
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            last_page = _get_last_page_number()
            self.assertEqual(last_page, 775)
            mock_get.assert_called_once_with("https://opinion.lawmaking.go.kr/gcom/nsmLmSts/out?pageIndex=1&blockStartPage=1")

    def test_get_last_page_number_no_link(self):
        mock_html = """
        <html>
        <body>
            <div class="paginate">
                <!-- No last page link -->
            </div>
        </body>
        </html>
        """

        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.content = mock_html.encode('utf-8')
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response

            last_page = _get_last_page_number()
            self.assertEqual(last_page, 1) # Should default to 1 if not found

    def test_get_last_page_number_request_error(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.exceptions.RequestException("Test Error")

            last_page = _get_last_page_number()
            self.assertEqual(last_page, 1) # Should default to 1 on error

if __name__ == '__main__':
    unittest.main()
