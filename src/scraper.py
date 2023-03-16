from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException, NoSuchElementException

class WebScraper:
    def __init__(self, driver_path):
        try:
            self.driver = webdriver.Chrome(executable_path=driver_path)
            self.wait = WebDriverWait(self.driver, 10)
        except WebDriverException as e:
            print("Error initializing web driver: ", e)

    def get_page(self, url):
        try:
            self.driver.get(url)
        except WebDriverException as e:
            print("Error getting page: ", e)

    def find_element(self, locator, value):
        try:
            element = self.wait.until(EC.presence_of_element_located((locator, value)))
            return element
        except TimeoutException as e:
            print(f"Timed out waiting for element {locator}={value}: ", e)
        except NoSuchElementException as e:
            print(f"Element {locator}={value} not found: ", e)

    def find_elements(self, locator, value):
        try:
            elements = self.wait.until(EC.presence_of_all_elements_located((locator, value)))
            return elements
        except TimeoutException as e:
            print(f"Timed out waiting for element {locator}={value}: ", e)
        except NoSuchElementException as e:
            print(f"Elements {locator}={value} not found: ", e)

    def click_element(self, element):
        try:
            element.click()
        except WebDriverException as e:
            print("Error clicking element: ", e)

    def wait_to_become_clickable(self, locator, value):
        try:
            self.wait.until(EC.element_to_be_clickable((locator, value)))
        except TimeoutException as e:
            print("Timed out waiting for element to become clickable: ", e)

    def wait_for_url_change(self, old_url):
        try:
            self.wait.until(EC.url_changes(old_url))
        except TimeoutException as e:
            print("Timed out waiting for URL change: ", e)

    def get_element_text(self, element):
        try:
            return element.text
        except WebDriverException as e:
            print("Error getting element text: ", e)

    def quit(self):
        try:
            self.driver.quit()
        except WebDriverException as e:
            print("Error quitting web driver: ", e)