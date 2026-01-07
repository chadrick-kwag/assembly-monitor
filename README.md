# Opinion Scraper

A web scraper for opinion.lawmaking.go.kr

## Features

*   **Command-Line Interface (CLI)**: Built with the `click` library, it allows users to specify `start-page`, `end-page`, and an `output-dir` for downloaded files.
*   **Web Scraping**: Utilizes `requests` for making HTTP requests and `BeautifulSoup4` for parsing HTML content.
*   **URL Discovery**: It iterates through specified page ranges on the target website to identify and collect URLs pointing to individual opinion posts.
*   **PDF Download**: For each identified post URL, it navigates to the post page, locates the PDF download link, extracts the filename, and downloads the PDF to the designated output directory.
*   **Database Integration**: Tracks all post URLs and whether the associated PDF was downloaded using SQLite.
*   **Environment Variables**: Uses `python-dotenv` to manage the SQLite database path and PDF download directory.
*   **Fetch Latest Posts**: A feature to fetch only the latest posts up to the last post URL gathered in a previous attempt.
*   **Comprehensive Reporting**: Provides a summary of processed URLs, downloaded PDFs, and URLs without downloaded PDFs.
*   **Duplicate Filename Handling**: Ensures that PDF filenames are unique to prevent overwriting.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/opinion_scraper.git
    cd opinion_scraper
    ```
2.  **Install dependencies using `uv`:**
    ```bash
    uv pip install -e .
    ```

## Configuration

Create a `.env` file in the root directory of the project to configure the database and download paths:

```
SQLITE_DB_PATH=opinions.db
PDF_DOWNLOAD_DIR=downloads
```

*   `SQLITE_DB_PATH`: Path to your SQLite database file. Defaults to `opinions.db`.
*   `PDF_DOWNLOAD_DIR`: Directory where downloaded PDFs will be saved. Defaults to `downloads`.

## Usage

### Scraping

To scrape opinions from a specific page range:

```bash
scrape-opinions scrape --start-page 1 --end-page 10
```

You can optionally specify an output directory (overrides `.env` setting):

```bash
scrape-opinions scrape --start-page 1 --end-page 10 --output-dir my_pdfs
```

### Fetching Latest Posts

To fetch only the latest posts since your last scraping attempt (it will stop when it encounters an already processed URL):

```bash
scrape-opinions scrape --fetch-latest
```

### Checking Status

To check the current status of the database:

```bash
scrape-opinions status
```

### Other Options

*   `--delay`: Time delay in seconds between requests (default: 1).

### Examples

Scrape pages 1 to 5 with a 2-second delay:

```bash
scrape-opinions scrape --start-page 1 --end-page 5 --delay 2
```

Fetch latest posts and save to a custom directory:

```bash
scrape-opinions scrape --fetch-latest --output-dir new_opinions
```