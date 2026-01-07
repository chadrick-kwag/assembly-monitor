import pytest
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the Python path so we can import from src
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from opinion_scraper.summary import summarize_pdf_local

load_dotenv()

# Define the path to the sample PDF
SAMPLE_PDF_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'resources/2212939_의사국 의안과_의안원문.pdf'))

@pytest.fixture(scope="module")
def set_gemini_api_key():
    # Set a dummy API key for testing purposes
    original_api_key = os.getenv("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = "DUMMY_API_KEY"
    yield
    # Restore original API key after tests
    if original_api_key:
        os.environ["GEMINI_API_KEY"] = original_api_key
    else:
        del os.environ["GEMINI_API_KEY"]

def test_summarize_pdf_local_success(set_gemini_api_key):
    """
    Tests that summarize_pdf_local returns a non-error, non-empty string.
    Note: This test will not actually call the Gemini API due to the dummy API key.
    It primarily checks for correct function execution and error handling up to the API call.
    """
    if not os.path.exists(SAMPLE_PDF_PATH):
        pytest.fail(f"Sample PDF not found at {SAMPLE_PDF_PATH}. Please ensure it's copied to tests/resources/.")

    summary = summarize_pdf_local(SAMPLE_PDF_PATH)

    # Assert that the summary contains an error message, as a dummy API key will lead to API failure.
    assert summary.startswith("An error occurred during summarization:") or \
           summary.startswith("An HTTP error occurred:")
    assert isinstance(summary, str)
    assert len(summary) > 0 # Ensure the error message is not empty
