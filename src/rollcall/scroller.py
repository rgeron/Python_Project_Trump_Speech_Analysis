import time

def scroll_to_bottom(browser):
    prev_height = 0
    while True:
        browser.execute_script("window.scrollBy(0, 3000);")
        time.sleep(2)
        new_height = browser.execute_script("return window.scrollY;")
        if new_height == prev_height:
            break
        prev_height = new_height