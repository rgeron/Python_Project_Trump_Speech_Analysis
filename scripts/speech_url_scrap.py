import sys,os
sys.path.insert(0,os.path.abspath(os.path.join(os.path.dirname(__file__),'..','src')))
import requests
import time
from rollcall.browser_setup import get_browser
from rollcall.speech_filter_action import open_page_close_popup_and_click_filters
from rollcall.scroller import scroll_to_bottom
from rollcall.url_extractor import extract_urls
from rollcall.storage import store_urls

import argparse

def main():
    parser = argparse.ArgumentParser(description='Scrap speech URLs for a candidate.')
    parser.add_argument('--candidate', type=str, default='trump', choices=['trump', 'harris', 'biden'], help='Candidate to scrap (trump, harris, or biden)')
    args = parser.parse_args()

    candidate = args.candidate.lower()
    
    if candidate == 'trump':
        url = 'https://rollcall.com/factbase/trump/search/'
        db_path = "data/speeches.db"
    elif candidate in ['harris', 'biden']:
        url = f'https://rollcall.com/factbase/{candidate}/search/'
        db_path = "data/other_candidate.db"
    else:
        print(f"Unknown candidate: {candidate}")
        return

    print(f"Scraping URLs for {candidate} from {url} into {db_path}")

    # Initialize DB if it doesn't exist
    from rollcall.speeches_db import init_db
    init_db(db_path=db_path)

    browser = get_browser()
    open_page_close_popup_and_click_filters(browser, url)
    scroll_to_bottom(browser)
    urls = extract_urls(browser)
    store_urls(urls, db_path=db_path)

if __name__ == "__main__":
    main()
