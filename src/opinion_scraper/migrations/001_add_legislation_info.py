import sqlite3

def upgrade(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            ALTER TABLE posts ADD COLUMN legislation_number TEXT;
        """)
        cursor.execute("""
            ALTER TABLE posts ADD COLUMN submission_date TIMESTAMP;
        """)
        conn.commit()
        print("Migration 001_add_legislation_info.py applied successfully.")
    except sqlite3.Error as e:
        print(f"Error applying migration 001_add_legislation_info.py: {e}")
    finally:
        conn.close()

def downgrade(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        # SQLite does not support dropping columns easily.
        # A common workaround is to create a new table, copy data, and drop the old one.
        # For simplicity in this context, we might choose to do nothing or raise an error.
        # Here, we'll just print a message.
        print("Downgrade for 001_add_legislation_info.py not fully supported (column dropping).")
        # Example of how one *might* attempt a downgrade (more complex for real use)
        # cursor.execute("CREATE TEMPORARY TABLE posts_backup(id, url, pdf_downloaded, last_checked, last_downloaded, pdf_path);")
        # cursor.execute("INSERT INTO posts_backup SELECT id, url, pdf_downloaded, last_checked, last_downloaded, pdf_path FROM posts;")
        # cursor.execute("DROP TABLE posts;")
        # cursor.execute("CREATE TABLE posts(id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL UNIQUE, pdf_downloaded BOOLEAN NOT NULL DEFAULT 0, last_checked TIMESTAMP, last_downloaded TIMESTAMP, pdf_path TEXT);")
        # cursor.execute("INSERT INTO posts SELECT id, url, pdf_downloaded, last_checked, last_downloaded, pdf_path FROM posts_backup;")
        # conn.commit()
    except sqlite3.Error as e:
        print(f"Error downgrading migration 001_add_legislation_info.py: {e}")
    finally:
        conn.close()
