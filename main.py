import os
import io
import sys
import time
import json
import requests
from src.scraper import WebScraper
from selenium.webdriver.common.by import By
from minio import Minio
from minio.error import S3Error
import yaml
import sys
import hashlib

def retrieve_all_stats():
    filtered_stats = []
    filtered_elements = set()
    stats = ws.find_elements(By.XPATH, '// *[contains(@onclick, "MatchStatistics")]')
    for stat in stats:
        try:
            attr = stat.get_attribute("onclick")
            if config["MATCH_LINK_STRING"] in attr and attr not in filtered_elements:
                filtered_elements.add(attr)
                filtered_stats.append(stat)
        except Exception as e:
            print(f"Failed getting statistics, because of: {e}")
    
    return filtered_stats, filtered_elements 

def get_next_stat(already_retrieved):
    stats, elements = retrieve_all_stats()
    for stat, el in zip(stats, elements):
        if el not in already_retrieved:
            return stat, el
        
    return None, None
    

if __name__ == "__main__":
    ACCESS_KEY = os.environ["MINIO_ACCESS_KEY"]
    SECRET_KEY = os.environ["MINIO_SECRET_KEY"]

    minio_client = Minio(
        "minio.minio.svc:9000",
        access_key=ACCESS_KEY,
        secret_key=SECRET_KEY,
        secure=False # NOTE: ATM both services running on a local cluster
    )

    # Make the bucket if it doesn't exist.
    bucket_name = "voliboli"
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)
        print("Created bucket", bucket_name)
    else:
        print("Bucket", bucket_name, "already exists")
    duration = 3600
    failure = False
    try:
        start_time = time.time()
        config = None
        with open("config.yaml", "r") as c:
            try:
                config = yaml.safe_load(c)
            except yaml.YAMLError as exc:
                sys.exit(1, exc)

        print("Starting up Voliboli WebScraper!")
        
        ws = WebScraper(config["PATH"])
        ws.driver.maximize_window()

        print("Successfully initialized ChromeDriver!")

        # Check robots.txt
        robots = requests.get(config["ROBOTS_URL"])
        content = robots.text
        if content != 'User-Agent: *\r\nDisallow:':
            sys.exit(1, "Web Crawlers disallowed on this webpage. Closing session...")

        ws.get_page(config["URL"])

        stats = retrieve_all_stats()[0]
        if stats is None:
            print("Failed to retrieve any stats from the website")
            sys.exit(1)
        n_stats = len(stats)
        already_retrieved = []
        print("Starting processing the files")
        for n in range(n_stats):
            print(f"Processing stats #{n}")
            # Scroll down (12 games per screen)
            x = int(n / 12)
            if (x != 0):
                ws.driver.execute_script(f"window.scrollTo(0, {x*1000 + 1350})")
            # I believe everytime the page is loaded, the elements have different IDs that's why I cannot fetch all statistics only once! - StaleElementReferenceException
            stat, el = get_next_stat(already_retrieved)
            already_retrieved.append(el)
            ws.click_element(stat)

            ws.driver.execute_script("window.scrollTo(0, 600)") # 1080 size of the page (it's like you cant click the element you don't actually see when bot controller browser opens)
            datavolley = ws.find_element(By.XPATH, "//a[@class='rtsLink']//span[@class='rtsTxt'][text()='DataVolley']")
            ws.click_element(datavolley)

            iframes = ws.find_elements(By.TAG_NAME, 'iframe')
            pdf_url = None
            for i in iframes:
                s = i.get_attribute("src")
                if config["MATCH_PDF_STRING"] in s:
                    pdf_url = s
            assert pdf_url is not None

            resp = requests.get(pdf_url)
            md5 = hashlib.md5()
            md5.update(resp.content)
            hex = md5.hexdigest()
            # Convert JSON data to bytes
            #json_bytes = json.dumps(, indent=2).encode('utf-8')
            # Create a BytesIO object
            json_buffer = io.BytesIO(resp.content)
            # Construct object name with prefix and current date-time
            file_path = f"data/raw/{hex}.pdf"
            # Make sure the file doesn't already exist - hash/name based on the context of the file 
            if not os.path.exists(file_path):
                with open(file_path, "wb") as f:
                    f.write(resp.content)
                    print(f"{hex}.pdf successfuly stored")

            # Upload JSON data to Minio
            minio_client.fput_object(
                bucket_name,
                f"{hex}.pdf",
                file_path,
            )

            print(f"JSON object successfully stored in Minio: {hex}.pdf")

            ws.get_page(config["URL"])
            elapsed_time = time.time() - start_time

            # Check if the elapsed time is greater than the desired duration
            if elapsed_time > duration:
                raise TimeoutError("Script ran for more than 60 minutes")
    
    except Exception as e:
        print(f"Error: {e}")
        failure = True
    
    finally:
        ws.quit()
        if failure:
            sys.exit(1)
        else:
            sys.exit(0)
