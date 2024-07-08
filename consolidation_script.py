import os
import pathlib
from rich import print
from dataclasses import dataclass
import pandas as pd

@dataclass
class Excel_info:
    original_file_name: str
    sheet_name: str
    pd_dataframe: pd.DataFrame

# Path to the directory where the files are stored
base_path = pathlib.Path(
    "/Users/marknyberg/Documents/Duke MBA/Academic Work/Operations Management/Littlefield/")
folder = pathlib.Path(base_path / "Initial Download")

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
    'Plot of daily average job lead time': 'Daily Avg Job Lead Time',
}

with pd.ExcelWriter("output.xlsx") as writer:
    for file_name, sheet_name in files_dict.items():
        file_path = folder / file_name
        df = pd.read_excel(file_path)
        df.to_excel(writer, sheet_name=sheet_name, index=False)





