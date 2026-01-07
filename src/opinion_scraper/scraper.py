import requests
from bs4 import BeautifulSoup
import os
import re
import time

BASE_URL = "https://opinion.lawmaking.go.kr"

def get_post_urls(start_page, end_page, delay=1):
    """
    Get all post URLs from the given page range.
    """
    post_urls = []
    for page_index in range(start_page, end_page + 1):
        url = f"https://opinion.lawmaking.go.kr/gcom/nsmLmSts/out?pageIndex={page_index}&blockStartPage=1"
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            for a in soup.select(".tbl_list tbody tr td.tal a"):
                post_urls.append(BASE_URL + a["href"])
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_index}: {e}")
    return post_urls

def download_pdf(post_url, download_dir, delay=1):
    """
    Download the PDF from a post URL.
    """
    try:
        response = requests.get(post_url)
        time.sleep(delay)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Find the link to the PDF
        pdf_link = None
        for a in soup.find_all("a", href=True):
            if "lmFileDownload.do" in a["href"]:
                pdf_link = a
                break

        if pdf_link:
            pdf_url = BASE_URL + pdf_link["href"]
            file_name_match = re.search(r"fileNm=([^&]+)", pdf_link["onclick"])
            if file_name_match:
                file_name = file_name_match.group(1)
            else:
                # Fallback to extract from URL if not in onclick
                file_name_match = re.search(r"File_NAME=([^&]+)", pdf_url)
                if file_name_match:
                    file_name = file_name_match.group(1)
                else:
                    file_name = pdf_url.split("=")[-1] + ".pdf" # A default name
            
            file_path = os.path.join(download_dir, file_name)

            if not os.path.exists(download_dir):
                os.makedirs(download_dir)

            pdf_response = requests.get(pdf_url, stream=True)
            time.sleep(delay)
            pdf_response.raise_for_status()

            with open(file_path, "wb") as f:
                for chunk in pdf_response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {file_name}")
        else:
            print(f"No PDF found for {post_url}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from {post_url}: {e}")
