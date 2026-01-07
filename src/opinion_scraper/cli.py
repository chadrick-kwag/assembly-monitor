import click
import os
from dotenv import load_dotenv
from .scraper import get_post_urls, download_pdf
from .database import initialize_db, get_stats, get_highest_id_num

load_dotenv()

@click.group()
def main():
    """
    A web scraper for opinion.lawmaking.go.kr
    """
    pass

@main.command()
@click.option("--start-page", default=1, help="The page number to start scraping from.")
@click.option("--end-page", default=1, help="The page number to stop scraping at.")
@click.option("--output-dir", help="The directory to save the downloaded PDFs.")
@click.option("--delay", default=1, help="Time delay in seconds between requests.")
@click.option("--fetch-latest", is_flag=True, help="Fetch latest posts until the last known post.")
def scrape(start_page, end_page, output_dir, delay, fetch_latest):
    """
    Scrape opinions and download PDFs.
    """
    initialize_db()

    if not output_dir:
        output_dir = os.getenv("PDF_DOWNLOAD_DIR", "downloads")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if fetch_latest:
        click.echo("Fetching latest posts...")
        highest_id = get_highest_id_num()
        post_urls = get_post_urls(1, 100, delay, highest_id_num=highest_id) # Scrape a large number of pages
    else:
        click.echo(f"Scraping from page {start_page} to {end_page}")
        post_urls = get_post_urls(start_page, end_page, delay)


    click.echo(f"Found {len(post_urls)} new posts.")

    for url in post_urls:
        download_pdf(url, output_dir, delay)

    stats = get_stats()
    click.echo("\n--- Scraping Report ---")
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"URLs without PDF: {stats['not_downloaded']}")
    click.echo("----------------------")

    click.echo("Done.")

@main.command()
def status():
    """
    Show the current status of the database.
    """
    initialize_db()
    stats = get_stats()
    click.echo("\n--- Database Status ---")
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"URLs without PDF: {stats['not_downloaded']}")
    click.echo("-----------------------")

if __name__ == "__main__":
    main()
