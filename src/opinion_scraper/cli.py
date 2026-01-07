import click
from .scraper import get_post_urls, download_pdf

@click.command()
@click.option("--start-page", default=1, help="The page number to start scraping from.")
@click.option("--end-page", default=1, help="The page number to stop scraping at.")
@click.option("--output-dir", default="downloads", help="The directory to save the downloaded PDFs.")
@click.option("--delay", default=1, help="Time delay in seconds between requests.")
def main(start_page, end_page, output_dir, delay):
    """
    A web scraper for opinion.lawmaking.go.kr
    """
    click.echo(f"Scraping from page {start_page} to {end_page}")
    post_urls = get_post_urls(start_page, end_page, delay)
    click.echo(f"Found {len(post_urls)} posts.")
    
    for url in post_urls:
        download_pdf(url, output_dir, delay)
        
    click.echo("Done.")

if __name__ == "__main__":
    main()
