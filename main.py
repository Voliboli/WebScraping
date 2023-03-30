import time
import requests
from src.scraper import WebScraper
from selenium.webdriver.common.by import By
import yaml
import sys
import hashlib

if __name__ == "__main__":
    config = None
    with open("config.yaml", "r") as c:
        try:
            config = yaml.safe_load(c)
        except yaml.YAMLError as exc:
            sys.exit(1, exc)

    ws = WebScraper(config["PATH"])
    ws.driver.maximize_window()
    ws.get_page(config["URL"])

    stats = ws.find_elements(By.XPATH, '// *[contains(@onclick, "MatchStatistics")]')
    print(len(stats))
    filtered_stats = []
    filtered_elements = set()
    for stat in stats:
        attr = stat.get_attribute("onclick")
        if config["MATCH_LINK_STRING"] in attr and attr not in filtered_elements:
            filtered_elements.add(attr)
            filtered_stats.append(stat)
    
    ws.click_element(filtered_stats[1])

    ws.driver.execute_script("window.scrollTo(0, 600)") # 1080 size of the page (it's like you cant click the element you don't actually see when bot controller browser opens)
    datavolley = ws.find_element(By.XPATH, "//a[@class='rtsLink']//span[@class='rtsTxt'][text()='DataVolley']")
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
    md5 = hashlib.md5()
    md5.update(resp.content)
    hex = md5.hexdigest()
    with open(f"data/raw/{hex}.pdf", "wb") as f:
        f.write(resp.content)
        print(f"{hex}.pdf successfuly stored")

    ws.get_page(config["URL"])
        
    ws.quit()