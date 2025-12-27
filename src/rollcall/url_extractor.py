from selenium.webdriver.common.by import By

def extract_urls(browser):
    links=browser.find_elements(By.CSS_SELECTOR,'a[title="View Transcript"]')
    urls=[link.get_attribute("href") for link in links]
    return urls
