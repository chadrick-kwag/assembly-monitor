from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import sqlite3
import os
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime

# Load environment variables
load_dotenv()

app = FastAPI()

# Pydantic model for a Post
class Post(BaseModel):
    id: int
    url: str
    pdf_downloaded: bool
    last_checked: Optional[datetime]
    last_downloaded: Optional[datetime]
    pdf_path: Optional[str]
    legislation_number: Optional[str]
    submission_date: Optional[str]
    summary: Optional[str]
    summary_model: Optional[str]

# Database connection dependency
def get_db():
    db_path = os.getenv("SQLITE_DB_PATH")
    if not db_path:
        raise ValueError("SQLITE_DB_PATH environment variable not set.")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Legislation Scraper API"}

class PostsResponse(BaseModel):
    total_count: int
    posts: List[Post]

@app.get("/posts/", response_model=PostsResponse)
def get_all_posts(
    fetchsize: int = 100,  # Default fetch size
    startfrom: int = 0,  # Default start from index
    db: sqlite3.Connection = Depends(get_db)
):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts LIMIT ? OFFSET ?", (fetchsize, startfrom))
    posts_data = cursor.fetchall()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM posts")
    total_count = cursor.fetchone()[0]

    # Convert sqlite3.Row to dictionary and then to Pydantic model
    posts = [Post(**{k: row[k] for k in row.keys()}) for row in posts_data]
    
    return PostsResponse(total_count=total_count, posts=posts)

@app.get("/posts/{post_id}", response_model=Post)
def get_post_by_id(post_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE id = ?", (post_id,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post(**{k: post[k] for k in post.keys()})

@app.get("/posts/legislation/{legislation_number}", response_model=Post)
def get_post_by_legislation_number(legislation_number: str, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM posts WHERE legislation_number = ?", (legislation_number,))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return Post(**{k: post[k] for k in post.keys()})

@app.get("/download/pdf/{post_id}")
async def download_pdf(post_id: int, db: sqlite3.Connection = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT pdf_path FROM posts WHERE id = ?", (post_id,))
    result = cursor.fetchone()

    if not result or not result['pdf_path']:
        raise HTTPException(status_code=404, detail="PDF not found for this post.")
    
    pdf_file_path = result['pdf_path']

    # Ensure the file exists and is a valid path
    if not os.path.exists(pdf_file_path):
        raise HTTPException(status_code=404, detail="PDF file not found on server.")
    
    # Extract filename for download
    filename = os.path.basename(pdf_file_path)
    
    return FileResponse(pdf_file_path, media_type='application/pdf', filename=filename)