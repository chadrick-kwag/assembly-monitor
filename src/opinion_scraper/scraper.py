import requests
from bs4 import BeautifulSoup
import os
import re
import time
from . import database
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://opinion.lawmaking.go.kr"

# Headers for the PDF download request. Referer will be added dynamically.
PDF_DOWNLOAD_HEADERS_TEMPLATE = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'ko,en;q=0.9,ko-KR;q=0.8,zh-CN;q=0.7,zh;q=0.6,en-US;q=0.5',
    'Connection': 'keep-alive',
    'Cookie': 'JSESSIONID=FSDbz6IfDaHC7cHzgqUVpS5-dp9TwRt_-q0hKYnL.node11; elevisor_for_j2ee_uid=4ba7ja6nz3n7p; PCID=17677554566492829293193; fileDownload=true; CMM_COOKIE_KEY=%7B%22srchTggPresetVal%22%3A%7B%22gcomnsmLmStsout%22%3Afalse%2C%22gcomnsmLmStsout2215774detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215770detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215860detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215890detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215890%22%3Afalse%2C%22gcomnsmLmStsout2215850detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215862detailRP%22%3Afalse%2C%22gcomnsmLmStsout2215791detailRP%22%3Afalse%7D%7D; clientid=070045953828',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}

def refresh_session():
    """
    Fetches a new JSESSIONID and updates the 'Cookie' in the header template.
    This should be called if downloads are failing due to an expired session.
    """
    global PDF_DOWNLOAD_HEADERS_TEMPLATE
    print("Attempting to refresh session cookie...")
    try:
        with requests.Session() as s:
            # Use a User-Agent from the template to appear like a standard browser
            headers = {'User-Agent': PDF_DOWNLOAD_HEADERS_TEMPLATE.get('User-Agent')}
            res = s.get(f"{BASE_URL}/gcom/nsmLmSts/out", headers=headers)
            res.raise_for_status()

            new_jsessionid = s.cookies.get('JSESSIONID')

            if new_jsessionid:
                old_cookie_string = PDF_DOWNLOAD_HEADERS_TEMPLATE['Cookie']
                
                # Replace the old JSESSIONID value with the new one
                new_cookie_string = re.sub(
                    r'JSESSIONID=[^;]+', 
                    f'JSESSIONID={new_jsessionid}', 
                    old_cookie_string
                )
                
                PDF_DOWNLOAD_HEADERS_TEMPLATE['Cookie'] = new_cookie_string
                print("Successfully refreshed session cookie (JSESSIONID).")
            else:
                print("Warning: Could not find JSESSIONID in response.")

    except requests.exceptions.RequestException as e:
        print(f"Error refreshing session: {e}")

def get_post_urls(start_page, end_page, delay=1, highest_id_num=0):
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
                post_url = BASE_URL + a["href"]
                id_num = _get_id_from_url(post_url)
                if highest_id_num > 0 and id_num <= highest_id_num:
                    return post_urls
                database.add_post(post_url)
                post_urls.append(post_url)
            time.sleep(delay)
        except requests.exceptions.RequestException as e:
            print(f"Error fetching page {page_index}: {e}")
    return post_urls

def _get_id_from_url(url):
    """Extracts the ID from a URL."""
    match = re.search(r"/(\d+)/detailRP", url)
    if match:
        return int(match.group(1))
    return 0


def process_post(post_url, download_dir, delay=1):
    """
    Download the PDF from a post URL.
    """
    post = database.get_post_by_url(post_url)
    if post and post['pdf_downloaded']:
        print(f"PDF for {post_url} already downloaded.")
        return

    try:
        response = requests.get(post_url)
        time.sleep(delay)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Extract legislation number and submission date
        legislation_number = None
        submission_date = None
        
        # Find the '발의정보' row
        발의정보_th = soup.find("th", scope="row", text="발의정보 ")
        if 발의정보_th:
            발의정보_td = 발의정보_th.find_next_sibling("td")
            if 발의정보_td:
                info_text = 발의정보_td.get_text(strip=True)
                
                # Regex for legislation number: looks for "제" followed by digits, then "호"
                leg_num_match = re.search(r"제(\d+)호", info_text)
                if leg_num_match:
                    legislation_number = leg_num_match.group(0) # Keep "제" and "호"
                
                # Regex for submission date: looks for (YYYY. MM. DD.)
                date_match = re.search(r"\((\d{4}\. \d{1,2}\. \d{1,2}\.)\)", info_text)
                if date_match:
                    submission_date = date_match.group(1).strip()
        
        if legislation_number and submission_date:
            print(f"Extracted: Legislation Number - {legislation_number}, Submission Date - {submission_date}")
            database.update_post_legislation_info(post_url, legislation_number, submission_date)
        else:
            print(f"Could not extract legislation info for {post_url}")
        
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
                print(f'pdf url: {pdf_url}')
                file_name = pdf_link_button.find(text=True, recursive=False).strip()

                if not os.path.exists(download_dir):
                    os.makedirs(download_dir)

                file_path = os.path.join(download_dir, file_name)

                # Prepare headers for PDF download, including the dynamic Referer
                pdf_headers = PDF_DOWNLOAD_HEADERS_TEMPLATE.copy()
                pdf_headers['Referer'] = post_url

                pdf_response = requests.get(pdf_url, headers=pdf_headers, stream=True)
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

                # Handle filename collisions
                if os.path.exists(file_path):
                    name, ext = os.path.splitext(file_name)
                    # Create a short hash from the URL to append to the filename
                    url_hash = hex(hash(post_url))[-6:]
                    file_name = f"{name}_{url_hash}{ext}"
                    file_path = os.path.join(download_dir, file_name)

                with open(file_path, "wb") as f:
                    for chunk in pdf_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"Downloaded {file_name}")
                
                # Remove the PDF_DOWNLOAD_DIR prefix before saving to DB
                db_pdf_path = os.path.relpath(file_path, os.getenv("PDF_DOWNLOAD_DIR", "downloads"))
                database.update_post_download_status(post_url, db_pdf_path)
        else:
            print(f"No PDF found for {post_url}")
            
    except requests.exceptions.RequestException as e:
        print(f"Error downloading PDF from {post_url}: {e}")
