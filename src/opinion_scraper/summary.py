import os
import sys
import httpx
import pathlib
from dotenv import load_dotenv

# Conditional import for google.generativeai
from google import genai
from google.genai import types


load_dotenv()

# --- Configuration ---
def summarize_pdf_local(pdf_path: str, prompt: str = "이 입법안에 대한 핵심 내용을 요약해줘. 어떤 취지인지, 어떤 것들이 바뀌는지를 요약하고, 최종적으로는 이것이 일반 시민들에게 미칠 영향을 정리해줘") -> str:
    """
    Summarizes a local PDF file using the Gemini API.
    This method is suitable for smaller PDF files (typically under 20MB).
    For larger files, consider using the Gemini Files API.
    """
    API_KEY = os.getenv("GEMINI_API_KEY") # Move API_KEY retrieval here
    if not API_KEY:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it.")
    if not os.path.exists(pdf_path):
        return f"Error: PDF file not found at {pdf_path}"

    try:
        pdf_file_path = pathlib.Path(pdf_path)
        
        # Use a multimodal model like gemini-1.5-flash for summarization
        model_name = os.getenv("GEMINI_MODEL_NAME", 'gemma-3-27b-it')
        client = genai.Client(api_key=API_KEY) # Instantiate the client

        response = client.models.generate_content( # Call generate_content via client
            model=model_name, # Pass model name as string
            contents=[
                types.Part.from_bytes(data=pdf_file_path.read_bytes(), mime_type="application/pdf"), # type: ignore
                prompt,
            ],
        )
        
        # Accessing the text from the response
        return response.text

    except httpx.HTTPStatusError as e:
        return f"An HTTP error occurred: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"An error occurred during summarization: {e}"

