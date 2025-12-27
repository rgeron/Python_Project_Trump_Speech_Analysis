# Getting in Trump's Head

This project scrapes and analyzes Donald Trump's speeches from Roll Call.

## Setup

1.  **Clone the repository** (if you haven't already).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Scraping Speeches

To scrape the URLs of the speeches:

```bash
python scripts/speech_url_scrap.py
```

This script uses Selenium and Chrome to navigate the Roll Call website, scroll to load all speeches, and extract their URLs into a SQLite database (`data/speeches.db`).

### Processing Speeches

To process the scraped URLs and extract speech details (title, date, stats, transcriptions):

```bash
python scripts/process_speeches.py
```

This script reads the URLs from the database, fetches the content, parses it, and updates the database with the extracted information.

### Database Initialization

The database is initialized automatically, but you can manually initialize it using:

```bash
python scripts/init_db.py
```

```bash
tad data/speeches.parquet
tad data/transcriptions.parquet
```

## Notebooks

The `notebooks` directory contains Jupyter notebooks for analysis and testing:

- `test_db.ipynb`: Testing database interactions.
- `test_soup.ipynb`: Testing BeautifulSoup parsing.
- `title_analysis.ipynb`: Analysis of speech titles and locations.
- `project_overview.ipynb`: Overview of the project.

To run the notebooks:

```bash
jupyter notebook
```

## Project Structure

- `src/rollcall`: Main package containing modules for scraping, parsing, and database operations.
- `scripts`: Executable scripts for running the scraping and processing pipelines.
- `data`: Directory where the SQLite database (`speeches.db`) is stored.
- `notebooks`: Jupyter notebooks for analysis.
