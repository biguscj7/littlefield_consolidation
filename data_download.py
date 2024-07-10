import time
import os
from pathlib import Path
from functools import reduce
from datetime import datetime as dt

import pandas as pd

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from dotenv import load_dotenv

load_dotenv()

download_dir = Path("~/Downloads").expanduser()

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
            "https://op.responsive.net/Littlefield/Plot?data=CASH&x=all&team=teamdevils", # cash on hand
            ]

files_dict = {
    'Plot of utilization of station 1, averaged over each day': 'Station 1 Utilization',
    'Plot of utilization of station 2, averaged over each day': 'Station 2 Utilization',
    'Plot of utilization of station 3, averaged over each day': 'Station 3 Utilization',
    'Plot of daily average number of kits queued for station 1': 'Station 1 Queue',
    'Plot of daily average number of kits queued for station 2': 'Station 2 Queue',
    'Plot of daily average number of kits queued for station 3': 'Station 3 Queue',
    'Plot of number of jobs accepted each day': 'Daily accepted kits',
    'Plot of daily average number of jobs waiting for kits': 'Jobs Waiting Kits',
    'Plot of inventory level in kits (not an average)': 'Kit Inventory Level',
    'Plot of daily average revenue per job': 'Avg Revenue per Job',
    'Plot of number of completed jobs each day': 'Daily Completed Jobs',
    'Plot of daily average job lead time': 'Daily Avg Lead Time',
    'Plot of cash on hand at the end of each day': 'Cash on Hand',
}


def find_shortname(file_name: str) -> str:
    for file_start, short_name in files_dict.items():
        if file_name.startswith(file_start):
            return short_name


driver = webdriver.Chrome()
driver.get("https://op.responsive.net/lt/operatns820g/entry.html")
id_elem = driver.find_element(By.NAME, "id")
id_elem.clear()
id_elem.send_keys(os.getenv("LITTLEFIELD_USERNAME"))

pw_elem = driver.find_element(By.NAME, "password")
pw_elem.clear()
pw_elem.send_keys(os.getenv("LITTLEFIELD_PASSWORD"))
pw_elem.send_keys(Keys.RETURN)

for url in url_list:
    driver.get(url)  # inventory
    download_element = driver.find_element(By.CLASS_NAME, 'download')
    download_element.click()
    time.sleep(0.5)

driver.close()

dataframes = []

for file_start, short_name in files_dict.items():
    for file in download_dir.glob("*.xlsx"):
        if file.name.startswith(file_start):
            df = pd.read_excel(file, index_col=0)
            match short_name:
                case x if "Utilization" in x:
                    df.columns = [x]
                    dataframes.append(df)
                case x if "Queue" in x:
                    df.columns = [x]
                    dataframes.append(df)
                case x if "accepted" in x:
                    df.columns = [x]
                    dataframes.append(df)
                case x if "Inventory" in x:
                    df.columns = [x]
                    dataframes.append(df)
                case x if "Completed" in x:
                    df.columns = [f"{x} - Seven day", f"{x} - One day", f"{x} - Half day"]
                    dataframes.append(df)
                case x if "Lead Time" in x:
                    df.columns = [f"{x} - Seven day", f"{x} - One day", f"{x} - Half day"]
                    dataframes.append(df)
                case x if "Cash on Hand" == x:
                    df.columns = [x]
                    dataframes.append(df)

            all_data = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True),
                              dataframes)

            all_data.to_excel(download_dir / f"Littlefield data {dt.now().strftime('%Y%m%d_%H%M')}.xlsx",
                              sheet_name="All Data")
