import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

def get_browser():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_experimental_option("detach", True)
    path_to_web_driver = chromedriver_autoinstaller.install()
    service = Service(executable_path=path_to_web_driver)
    browser = webdriver.Chrome(service=service,
                            options=chrome_options)
    return browser