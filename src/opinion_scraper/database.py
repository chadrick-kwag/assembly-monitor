import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
import re

load_dotenv()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    db_path = os.getenv("SQLITE_DB_PATH")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    """Initializes the database and creates the 'posts' table if it doesn't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL UNIQUE,
            pdf_downloaded BOOLEAN NOT NULL DEFAULT 0,
            last_checked TIMESTAMP,
            last_downloaded TIMESTAMP,
            pdf_path TEXT
        );
    """)
    conn.commit()
    conn.close()

def get_stats():
    """Retrieves statistics from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_urls = cursor.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    downloaded_pdfs = cursor.execute("SELECT COUNT(*) FROM posts WHERE pdf_downloaded = 1").fetchone()[0]
    
    conn.close()
    
    return {
        "total_urls": total_urls,
        "downloaded_pdfs": downloaded_pdfs,
        "not_downloaded": total_urls - downloaded_pdfs
    }
    
def add_post(url, pdf_downloaded=False, pdf_path=None):
    """Adds a new post to the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    last_checked = datetime.now()
    last_downloaded = datetime.now() if pdf_downloaded else None
    
    try:
        cursor.execute(
            "INSERT INTO posts (url, pdf_downloaded, last_checked, last_downloaded, pdf_path) VALUES (?, ?, ?, ?, ?)",
            (url, pdf_downloaded, last_checked, last_downloaded, pdf_path)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        # Post with this URL already exists
        pass
    finally:
        conn.close()

def get_post_by_url(url):
    """Retrieves a post from the database by its URL."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM posts WHERE url = ?", (url,))
    post = cursor.fetchone()
    
    conn.close()
    
    return post

def update_post_download_status(url, pdf_path):
    """Updates the download status of a post."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    last_downloaded = datetime.now()
    
    cursor.execute(
        "UPDATE posts SET pdf_downloaded = 1, last_downloaded = ?, pdf_path = ? WHERE url = ?",
        (last_downloaded, pdf_path, url)
    )
    
    conn.commit()
    conn.close()

def get_last_post_url():
    """Retrieves the URL of the last post that was successfully scraped."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT url FROM posts ORDER BY id DESC LIMIT 1")
    post = cursor.fetchone()
    
    conn.close()
    
    return post['url'] if post else None

def _get_id_from_url(url):
    """Extracts the ID from a URL."""
    match = re.search(r"/(\d+)/detailRP", url)
    if match:
        return int(match.group(1))
    return 0

def get_highest_id_num():
    """Retrieves the highest ID number from the URLs in the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT url FROM posts")
    urls = cursor.fetchall()
    
    conn.close()
    
    if not urls:
        return 0
    
    highest_id = 0
    for url in urls:
        id_num = _get_id_from_url(url['url'])
        if id_num > highest_id:
            highest_id = id_num
            
    return highest_id


if __name__ == '__main__':
    initialize_db()
