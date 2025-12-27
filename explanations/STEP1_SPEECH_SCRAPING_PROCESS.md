# Donald Trump Speech Scraping and Database Storage Process

## Project Overview

This project implements a comprehensive web scraping system to collect Donald Trump's speeches from RollCall.com and store them in a SQLite database for subsequent NLP analysis. The system has successfully scraped **885 speech URLs** and is designed to handle the complete pipeline from web scraping to data storage.

## Architecture Overview

The project follows a modular architecture with clear separation of concerns:

```
src/rollcall/
├── browser_setup.py          # Browser configuration and setup
├── speech_filter_action.py   # Page navigation and filter interactions
├── scroller.py              # Infinite scroll handling
├── url_extractor.py         # URL extraction from page elements
├── storage.py               # Database storage operations
└── speeches_db.py           # Database schema and initialization
```

## Detailed Process Flow

### 1. Database Initialization

**File**: `scripts/init_db.py` → `src/rollcall/speeches_db.py`

The system starts by initializing a SQLite database with the following schema:

```sql
CREATE TABLE IF NOT EXISTS Speeches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT UNIQUE,
    soup TEXT
);
```

**Key Features:**

- **Auto-incrementing ID**: Primary key for unique identification
- **Unique URL constraint**: Prevents duplicate speech entries
- **Soup field**: Reserved for storing HTML content (currently NULL)
- **File location**: `data/speeches.db`

### 2. Browser Setup and Configuration

**File**: `src/rollcall/browser_setup.py`

The system uses Selenium WebDriver with Chrome for web scraping:

```python
def get_browser():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("detach", True)
    # Auto-installs ChromeDriver
    path_to_web_driver = chromedriver_autoinstaller.install()
    service = Service(executable_path=path_to_web_driver)
    browser = webdriver.Chrome(service=service, options=chrome_options)
    return browser
```

**Configuration Details:**

- **Window size**: 1920x1080 for optimal page rendering
- **Auto-detach**: Keeps browser open for debugging
- **Auto-installation**: Automatically downloads and configures ChromeDriver
- **Security options**: Disabled sandbox and dev-shm-usage for stability

### 3. Target Website Navigation

**File**: `src/rollcall/speech_filter_action.py`

The system navigates to RollCall's Trump speech database:

```python
def open_page_close_popup_and_click_filters(browser, url):
    browser.get(url)  # https://rollcall.com/factbase/trump/search/
    # Close popup modal
    close_btn = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.cursor-pointer.text-right.mr-4.mt-2"))
    )
    close_btn.click()
    # Click "Speech" filter
    label = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='Speech']"))
    )
    label.click()
```

**Navigation Steps:**

1. **Load target URL**: `https://rollcall.com/factbase/trump/search/`
2. **Handle popup**: Automatically closes any modal popups
3. **Apply filters**: Clicks the "Speech" filter to show only speech transcripts
4. **Wait strategies**: Uses WebDriverWait for reliable element interaction

### 4. Infinite Scroll Implementation

**File**: `src/rollcall/scroller.py`

The system implements infinite scroll to load all available speeches:

```python
def scroll_to_bottom(browser):
    prev_height = 0
    while True:
        browser.execute_script("window.scrollBy(0, 3000);")
        time.sleep(2)
        new_height = browser.execute_script("return window.scrollY;")
        if new_height == prev_height:
            break
        prev_height = new_height
```

**Scroll Strategy:**

- **Incremental scrolling**: 3000px per scroll action
- **Wait time**: 2 seconds between scrolls for content loading
- **Termination condition**: Stops when no new content loads (height unchanged)
- **JavaScript execution**: Uses `window.scrollBy()` for smooth scrolling

### 5. URL Extraction

**File**: `src/rollcall/url_extractor.py`

The system extracts speech URLs from the loaded page:

```python
def extract_urls(browser):
    links = browser.find_elements(By.CSS_SELECTOR, 'a[title="View Transcript"]')
    urls = [link.get_attribute("href") for link in links]
    return urls
```

**Extraction Method:**

- **CSS Selector**: Targets links with `title="View Transcript"`
- **Attribute extraction**: Gets `href` attribute from each link
- **Return format**: List of speech transcript URLs

### 6. Database Storage

**File**: `src/rollcall/storage.py`

URLs are stored in the SQLite database with duplicate prevention:

```python
def store_urls(urls):
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect("data/speeches.db")
    for url in urls:
        conn.execute("INSERT OR IGNORE INTO Speeches (url, soup) VALUES (?, ?)", (url, None))
    conn.commit()
    conn.close()
```

**Storage Features:**

- **Directory creation**: Ensures `data/` directory exists
- **Duplicate prevention**: Uses `INSERT OR IGNORE` to avoid duplicates
- **Batch processing**: Processes all URLs in a single transaction
- **Connection management**: Properly closes database connections

### 7. Main Execution Pipeline

**File**: `scripts/speech_url_scrap.py`

The complete scraping process is orchestrated as follows:

```python
def main():
    browser = get_browser()
    url = 'https://rollcall.com/factbase/trump/search/'
    open_page_close_popup_and_click_filters(browser, url)
    scroll_to_bottom(browser)
    urls = extract_urls(browser)
    store_urls(urls)
```

**Execution Flow:**

1. **Initialize browser** with Chrome WebDriver
2. **Navigate to target page** and apply filters
3. **Scroll to load all content** using infinite scroll
4. **Extract all speech URLs** from the page
5. **Store URLs in database** with duplicate prevention

## Data Storage Strategy

### Current Implementation

- **Database**: SQLite (`data/speeches.db`)
- **Records**: 885 speech URLs collected
- **Schema**: Simple structure with ID, URL, and reserved soup field
- **Location**: Local file-based storage
