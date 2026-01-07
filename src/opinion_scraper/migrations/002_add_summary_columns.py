def upgrade(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        ALTER TABLE posts
        ADD COLUMN summary TEXT;
    """)
    
    cursor.execute("""
        ALTER TABLE posts
        ADD COLUMN summary_model TEXT;
    """)
    
    conn.commit()
    conn.close()

def downgrade(db_path):
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # SQLite does not support dropping columns directly in older versions
    # For a proper downgrade in SQLite, you would typically need to
    # create a new table, copy data, drop the old, and rename the new.
    # For simplicity and typical migration patterns, we'll leave it as is
    # or raise an error indicating no direct downgrade path for column drops.
    print("Downgrade for 002_add_summary_columns.py not fully implemented (column drop not direct in SQLite).")
    
    conn.close()
