from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time
from selenium.common.exceptions import TimeoutException

def open_page_close_popup_and_click_filters(browser, url):
    browser.get(url)
    try :
        close_btn=WebDriverWait(browser, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "div.cursor-pointer.text-right.mr-4.mt-2"))
            )
        close_btn.click()
    except :
        pass
    
    # Si y'a pas d'élément avec le tag speech dans les trucs loadés, y'a pas le filtre speech, donc il faut scroller jusqu'a load un speech
    max_retries = 20
    for _ in range(max_retries):
        try:
            label = WebDriverWait(browser, 2).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label[for='Speech']")))
            label.click()
            break
        except TimeoutException:
            # Scroll down to load more items
            browser.execute_script(f"window.scrollBy(0, {10000 * (_ + 1)});")
            time.sleep(1)
            # Scroll up to verify if filter is now available
            browser.execute_script("window.scrollTo(0, 0);")
            time.sleep(1)
    
    time.sleep(2)