import click
import os
import time
from dotenv import load_dotenv
from .scraper import get_post_urls, process_post, _get_last_page_number
from .database import initialize_db, get_stats, get_highest_id_num, get_posts_to_summarize, update_post_summary, get_post_by_legislation_number
from .summary import summarize_pdf_local
from tqdm import tqdm
from . import backup 
from click import style

load_dotenv()

@click.group()
def main():
    """
    A web scraper for opinion.lawmaking.go.kr
    """
    pass

main.add_command(backup.main, name="backup") # <--- ADD THIS LINE

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
        click.echo(style("Fetching latest posts...", fg="yellow"))
        highest_id = get_highest_id_num()
        # Scrape a large number of pages, will stop when highest_id_num is reached
        post_urls = get_post_urls(1, 100, delay, highest_id_num=highest_id) 
    else:
        if end_page == 'end':
            end_page = _get_last_page_number()
            click.echo(style(f"Determined last page to be {end_page}", fg="blue"))
        click.echo(style(f"Scraping from page {start_page} to {end_page}", fg="blue"))


    click.echo(style(f"Found {len(post_urls)} new posts.", fg="green"))

    for url in post_urls:
        process_post(url, output_dir, delay)

    stats = get_stats()
    click.echo(style("\n--- Scraping Report ---", fg="yellow", bold=True))
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"URLs without PDF: {stats['not_downloaded']}")
    click.echo(f"Posts summarized: {stats['summarized_posts']}")
    click.echo("----------------------")

    click.echo(style("Done.", fg="green"))

@main.command()
@click.option("--legislation-number", help="Summarize a specific post by its legislation number.")
@click.option("--delay", default=5, help="Time delay in seconds between summarization attempts.")
def summarize(legislation_number, delay):
    """
    Generate summaries for downloaded PDFs using a generative AI model.
    """
    initialize_db()

    pdf_download_dir = os.getenv("PDF_DOWNLOAD_DIR", "downloads")

    if legislation_number:
        click.echo(style(f"Attempting to summarize post with legislation number: {legislation_number}", fg="blue"))
        post = get_post_by_legislation_number(legislation_number)
        if post and post['pdf_downloaded'] and post['pdf_path']:
            full_pdf_path = os.path.join(pdf_download_dir, post['pdf_path'])
            click.echo(style(f"Summarizing {full_pdf_path}...", fg="blue"))
            time.sleep(delay)  # Add delay
            summary_text = summarize_pdf_local(full_pdf_path)
            if summary_text.startswith("Error:"):
                click.echo(style(f"Failed to summarize: {summary_text}", fg="red"), err=True)
            else:
                model_name = os.getenv("GEMINI_MODEL_NAME")
                if not model_name:
                    raise ValueError("GEMINI_MODEL_NAME environment variable not set.")
                update_post_summary(post['url'], summary_text, model_name)
                click.echo(style("Summary generated and saved to database.", fg="green"))
                click.echo(style("\n--- Summary ---", fg="yellow", bold=True))
                click.echo(summary_text)
                click.echo("---------------")
        else:
            click.echo(style(f"Post with legislation number {legislation_number} not found, or PDF not downloaded.", fg="red"))
    else:
        click.echo(style("Generating summaries for all posts without a summary...", fg="yellow"))
        posts_to_summarize = get_posts_to_summarize()
        if not posts_to_summarize:
            click.echo(style("No posts found that need summarization.", fg="yellow"))
            return

        for post in tqdm(posts_to_summarize, desc="Summarizing PDFs"):
            if post['pdf_path']:
                full_pdf_path = os.path.join(pdf_download_dir, post['pdf_path'])
                tqdm.write(style(f"Summarizing {full_pdf_path}...", fg="blue"))
                time.sleep(delay)  # Add delay
                summary_text = summarize_pdf_local(full_pdf_path)
                if summary_text.startswith("Error:"):
                    tqdm.write(style(f"Failed to summarize {full_pdf_path}: {summary_text}", fg="red"), err=True)
                else:
                    model_name = os.getenv("GEMINI_MODEL_NAME")
                    if not model_name:
                        raise ValueError("GEMINI_MODEL_NAME environment variable not set.")
                    update_post_summary(post['url'], summary_text, model_name)
                    tqdm.write(style(f"Successfully summarized {full_pdf_path}", fg="green"))
            else:
                tqdm.write(style(f"Skipping post {post['url']} as no PDF path is available.", fg="yellow"), err=True)
        click.echo(style("Summarization complete.", fg="green"))

    stats = get_stats()
    click.echo(style("\n--- Summarization Report ---", fg="yellow", bold=True))
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
    click.echo(style("\n--- Database Status ---", fg="yellow", bold=True))
    click.echo(f"Total URLs in database: {stats['total_urls']}")
    click.echo(f"PDFs downloaded: {stats['downloaded_pdfs']}")
    click.echo(f"URLs without PDF: {stats['not_downloaded']}")
    click.echo(f"Posts summarized: {stats['summarized_posts']}")
    click.echo("-----------------------")

if __name__ == "__main__":
    main()
