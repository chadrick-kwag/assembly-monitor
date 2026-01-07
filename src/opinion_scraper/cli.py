import click
import os
from dotenv import load_dotenv
from .scraper import get_post_urls, process_post, _get_last_page_number
from .database import initialize_db, get_stats, get_highest_id_num, get_posts_to_summarize, update_post_summary, get_post_by_legislation_number
from .summary import summarize_pdf_local
from tqdm import tqdm

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
        # Scrape a large number of pages, will stop when highest_id_num is reached
        post_urls = get_post_urls(1, 100, delay, highest_id_num=highest_id) 
    else:
        if end_page == 'end':
            end_page = _get_last_page_number()
            click.echo(f"Determined last page to be {end_page}")
        click.echo(f"Scraping from page {start_page} to {end_page}")
        post_urls = get_post_urls(start_page, end_page, delay)


    click.echo(f"Found {len(post_urls)} new posts.")

    for url in post_urls:
        process_post(url, output_dir, delay)

    stats = get_stats()
    click.echo("\n--- Scraping Report ---")
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"URLs without PDF: {stats['not_downloaded']}")
    click.echo(f"Posts summarized: {stats['summarized_posts']}")
    click.echo("----------------------")

    click.echo("Done.")

@main.command()
@click.option("--legislation-number", help="Summarize a specific post by its legislation number.")
def summarize(legislation_number):
    """
    Generate summaries for downloaded PDFs using a generative AI model.
    """
    initialize_db()

    pdf_download_dir = os.getenv("PDF_DOWNLOAD_DIR", "downloads")

    if legislation_number:
        click.echo(f"Attempting to summarize post with legislation number: {legislation_number}")
        post = get_post_by_legislation_number(legislation_number)
        if post and post['pdf_downloaded'] and post['pdf_path']:
            full_pdf_path = os.path.join(pdf_download_dir, post['pdf_path'])
            click.echo(f"Summarizing {full_pdf_path}...")
            summary_text = summarize_pdf_local(full_pdf_path)
            if summary_text.startswith("Error:"):
                click.echo(f"Failed to summarize: {summary_text}", err=True)
            else:
                model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Default model name
                update_post_summary(post['url'], summary_text, model_name)
                click.echo("Summary generated and saved to database.")
                click.echo("\n--- Summary ---")
                click.echo(summary_text)
                click.echo("---------------")
        else:
            click.echo(f"Post with legislation number {legislation_number} not found, or PDF not downloaded.")
    else:
        click.echo("Generating summaries for all posts without a summary...")
        posts_to_summarize = get_posts_to_summarize()
        if not posts_to_summarize:
            click.echo("No posts found that need summarization.")
            return

        for post in tqdm(posts_to_summarize, desc="Summarizing PDFs"):
            if post['pdf_path']:
                full_pdf_path = os.path.join(pdf_download_dir, post['pdf_path'])
                summary_text = summarize_pdf_local(full_pdf_path)
                if summary_text.startswith("Error:"):
                    click.echo(f"Failed to summarize {full_pdf_path}: {summary_text}", err=True)
                else:
                    model_name = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash") # Default model name
                    update_post_summary(post['url'], summary_text, model_name)
            else:
                click.echo(f"Skipping post {post['url']} as no PDF path is available.", err=True)
        click.echo("Summarization complete.")

    stats = get_stats()
    click.echo("\n--- Summarization Report ---")
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"Posts summarized: {stats['summarized_posts']}")
    click.echo("--------------------------")


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
    click.echo(f"Posts summarized: {stats['summarized_posts']}")
    click.echo("-----------------------")

if __name__ == "__main__":
    main()
