import sqlite3
import os
from dotenv import load_dotenv
from datetime import datetime
import re
import glob # Import glob
import importlib.util # Import importlib.util

load_dotenv()

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    db_path = os.getenv("SQLITE_DB_PATH")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def _apply_migrations(conn):
    """Applies pending database migrations."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS migrations_applied (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            migration_name TEXT NOT NULL UNIQUE,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()

    migrations_dir = os.path.join(os.path.dirname(__file__), "migrations")
    migration_files = sorted(glob.glob(os.path.join(migrations_dir, "*.py")))

    for migration_file in migration_files:
        migration_name = os.path.basename(migration_file)
        cursor.execute("SELECT id FROM migrations_applied WHERE migration_name = ?", (migration_name,))
        if cursor.fetchone() is None:
            print(f"Applying migration: {migration_name}")
            try:
                spec = importlib.util.spec_from_file_location(migration_name, migration_file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.upgrade(os.getenv("SQLITE_DB_PATH"))
                cursor.execute("INSERT INTO migrations_applied (migration_name) VALUES (?)", (migration_name,))
                conn.commit()
            except Exception as e:
                print(f"Error applying migration {migration_name}: {e}")
                # Depending on desired behavior, might re-raise or exit
        else:
            print(f"Migration already applied: {migration_name}")


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
    
    _apply_migrations(conn) # Apply migrations after initial table creation
    
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

def update_post_legislation_info(url, legislation_number, submission_date):
    """Updates the legislation number and submission date for a post."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "UPDATE posts SET legislation_number = ?, submission_date = ? WHERE url = ?",
        (legislation_number, submission_date, url)
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