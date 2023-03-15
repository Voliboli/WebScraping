from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import requests
import json

if __name__ == "__main__":
    PATH = "chromedriver_linux64/chromedriver"
    driver = webdriver.Chrome(PATH)
    actions = ActionChains(driver)

    driver.get("https://ozs-web.dataproject.com/CompetitionMatches.aspx?ID=88&PID=131")
    # use the find_elements_by_xpath method to locate the elements
    stats = driver.find_elements(By.XPATH, '// *[contains(@onclick, "MatchStatistics")]')

    # do something with the elements, such as print their text
    #for stat in stats:
    actions.click(stats[0]).perform()
    time.sleep(3)
    datavolley = driver.find_element(By.XPATH, "//span[@class='rtsTxt'][text()='DataVolley']/ancestor::a")
    actions.click(datavolley).perform()

    time.sleep(5)
    iframes = driver.find_elements(By.TAG_NAME, 'iframe')
    pdf_url = None
    for i in iframes:
        s = i.get_attribute("src")
        if "Match_Datavolley" in s:
            pdf_url = s
    assert pdf_url is not None
    #driver.get(pdf_url)
    #print(pdf_url)

    resp = requests.get(pdf_url)
    with open("stats/tmp.pdf", "wb") as f:
        f.write(resp.content)

    time.sleep(5)
    '''
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "myDynamicElement"))
        )
    finally:
        driver.quit()
    '''
        
    time.sleep(10)

    #driver.quit()