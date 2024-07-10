import time
import os

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from dotenv import load_dotenv

load_dotenv()

driver = webdriver.Chrome()
driver.get("https://op.responsive.net/lt/operatns820g/entry.html")
id_elem = driver.find_element(By.NAME, "id")
id_elem.clear()
id_elem.send_keys(os.getenv("LITTLEFIELD_USERNAME"))

pw_elem = driver.find_element(By.NAME, "password")
pw_elem.clear()
pw_elem.send_keys(os.getenv("LITTLEFIELD_PASSWORD"))
pw_elem.send_keys(Keys.RETURN)

url_list = ["https://op.responsive.net/Littlefield/Plot?data=JOBIN&x=all",  # job arrivals
            "https://op.responsive.net/Littlefield/Plot?data=JOBQ&x=all",  # waiting for kits
            "https://op.responsive.net/Littlefield/Plot?data=INV&x=all",  # inventory
            "https://op.responsive.net/Littlefield/Plot?data=S1Q&x=all",  # station 1 queue
            "https://op.responsive.net/Littlefield/Plot?data=S1UTIL&x=all",  # station 1 utilization
            "https://op.responsive.net/Littlefield/Plot?data=S2Q&x=all",  # station 2 queue
            "https://op.responsive.net/Littlefield/Plot?data=S2UTIL&x=all",  # station 2 utilization
            "https://op.responsive.net/Littlefield/Plot?data=S3Q&x=all",  # station 3 queue
            "https://op.responsive.net/Littlefield/Plot?data=S3UTIL&x=all",  # station 3 utilization
            "https://op.responsive.net/Littlefield/Plot?data=JOBOUT&x=all",  # completed job count
            "https://op.responsive.net/Littlefield/Plot?data=JOBT&x=all",  # job lead times
            "https://op.responsive.net/Littlefield/Plot?data=JOBREV&x=all",  # revenues
            ]

for url in url_list:
    driver.get(url)  # inventory
    download_element = driver.find_element(By.CLASS_NAME, 'download')
    download_element.click()
    time.sleep(0.5)

driver.close()
