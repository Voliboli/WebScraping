import time
import requests
from src.scraper import WebScraper
from selenium.webdriver.common.by import By
import yaml
import sys

if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as c:
        try:
            config = yaml.safe_load(c)
        except yaml.YAMLError as exc:
            sys.exit(1, exc)

    ws = WebScraper(config["PATH"])
    ws.get_page(config["URL"])

    stats = ws.find_elements(By.XPATH, '// *[contains(@onclick, "MatchStatistics")]')
    ws.click_element(stats[0])

    datavolley = ws.find_element(By.XPATH, "//a[@class='rtsLink']//span[@class='rtsTxt'][text()='DataVolley']")
    ws.wait_to_become_clickable(By.XPATH, "//a[@class='rtsLink']//span[@class='rtsTxt'][text()='DataVolley']")
    time.sleep(3)
    ws.click_element(datavolley)

    iframes = ws.find_elements(By.TAG_NAME, 'iframe')
    pdf_url = None
    for i in iframes:
        s = i.get_attribute("src")
        print(s)
        if config["MATCH_PDF_STRING"] in s:
            pdf_url = s
    assert pdf_url is not None

    resp = requests.get(pdf_url)
    with open("data/raw/tmp.pdf", "wb") as f:
        f.write(resp.content)
        print("PDF successfuly stored")

    ws.quit()