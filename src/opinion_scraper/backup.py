import os
import zipfile
from datetime import datetime
import click
from dotenv import load_dotenv

@click.command()
def main():
    """
    Creates a backup of the SQLite database and downloaded PDFs.
    """
    load_dotenv()

    # Set default values if not defined in .env
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "opinions.db")
    PDF_DOWNLOAD_DIR = os.getenv("PDF_DOWNLOAD_DIR", "downloads")
    # Default BACKUP_DIR to 'backups' in the current working directory
    BACKUP_DIR = os.getenv("BACKUP_DIR", "backups") 

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    zip_filename = f"backup_{timestamp}.zip"
    full_zip_path = os.path.join(BACKUP_DIR, zip_filename)

    click.echo("Starting backup...")
    click.echo(f"Database path: {SQLITE_DB_PATH}")
    click.echo(f"PDF download directory: {PDF_DOWNLOAD_DIR}")
    click.echo(f"Backup file: {full_zip_path}")

    # Create the backup directory if it doesn't exist
    os.makedirs(BACKUP_DIR, exist_ok=True)

    db_exists = os.path.isfile(SQLITE_DB_PATH)
    pdf_dir_exists = os.path.isdir(PDF_DOWNLOAD_DIR)

    if not db_exists:
        click.echo(f"Warning: Database file '{SQLITE_DB_PATH}' not found. Skipping.", err=True)

    if not pdf_dir_exists:
        click.echo(f"Warning: PDF download directory '{PDF_DOWNLOAD_DIR}' not found. Skipping.", err=True)

    try:
        with zipfile.ZipFile(full_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            if db_exists:
                zipf.write(SQLITE_DB_PATH, os.path.basename(SQLITE_DB_PATH))
                click.echo(f"Added database: {SQLITE_DB_PATH}")
            
            if pdf_dir_exists:
                for root, _, files in os.walk(PDF_DOWNLOAD_DIR):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Create archive name to preserve directory structure within the zip
                        # e.g., downloads/subdir/file.pdf
                        arcname = os.path.join(os.path.basename(PDF_DOWNLOAD_DIR), os.path.relpath(file_path, PDF_DOWNLOAD_DIR))
                        zipf.write(file_path, arcname)
                        # click.echo(f"Added PDF: {file_path}") # Too verbose, uncomment for debugging
                click.echo(f"Added PDF directory: {PDF_DOWNLOAD_DIR}")
        
        click.echo(f"Backup successful! Created {full_zip_path}")
    except Exception as e:
        click.echo(f"Backup failed: {e}", err=True)
        exit(1)

if __name__ == "__main__":
    main()