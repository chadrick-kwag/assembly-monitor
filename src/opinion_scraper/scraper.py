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
            for a in soup.select("td.subject a"):
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
        
        pdf_link_button = None
        for button in soup.find_all("button", onclick=re.compile(r"fnDownload\(\d+\)")):
            if ".pdf" in button.text.lower():
                pdf_link_button = button
                break

        if pdf_link_button:
            match = re.search(r"fnDownload\((\d+)\)", pdf_link_button["onclick"])
            if match:
                seq = match.group(1)
                pdf_url = f"{BASE_URL}/better/atchFile/download/{seq}"
                file_name = pdf_link_button.find(text=True, recursive=False).strip()

                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                file_path = os.path.join(download_dir, file_name)

                pdf_response = requests.get(pdf_url, stream=True)
                time.sleep(delay)
                pdf_response.raise_for_status()

                # Try to extract filename from Content-Disposition header, but also use the button text as a fallback
                if "Content-Disposition" in pdf_response.headers:
                    cd = pdf_response.headers["Content-Disposition"]
                    fname = re.findall(r"filename\*?=([^;]+)", cd)
                    if fname:
                        try:
                            header_filename = requests.utils.unquote(fname[0]).encode('latin-1').decode('utf-8')
                        except:
                            header_filename = requests.utils.unquote(fname[0])
                        header_filename = header_filename.strip("'\"")
                        if not header_filename.lower().endswith(".pdf"):
                            header_filename += ".pdf"
                        file_name = header_filename
                        file_path = os.path.join(download_dir, file_name)

                with open(file_path, "wb") as f:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {file_name}")
        else:
            print(f"No PDF found for {post_url}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from {post_url}: {e}")
