import os
import sys
from pathlib import Path
import pytest

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from opinion_scraper.summary import summarize_pdf_local

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY is not set")
def test_summarize_pdf_local_large():
    """
    Test summarization of a large PDF file (more than 30 pages).
    """
    large_pdf_path = "tests/resources/large_pdf.pdf"
    summarization_prompt = "Summarize this document in Korean, focusing on its main points and implications for citizens."
    
    summary = summarize_pdf_local(large_pdf_path, summarization_prompt)
    
    assert summary is not None
    assert "Error" not in summary
    assert len(summary) > 0

@pytest.mark.skipif(not os.getenv("GEMINI_API_KEY"), reason="GEMINI_API_KEY is not set")
def test_summarize_pdf_local_small():
    """
    Test summarization of a small PDF file (less than or equal to 30 pages).
    """
    small_pdf_path = "tests/resources/2212939_의사국 의안과_의안원문.pdf"
    summarization_prompt = "Summarize this document in Korean, focusing on its main points and implications for citizens."
    
    summary = summarize_pdf_local(small_pdf_path, summarization_prompt)
    
    assert summary is not None
    assert "Error" not in summary
    assert len(summary) > 0