import io
from datetime import datetime as dt

import streamlit as st
import pandas as pd

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

def file_rename(file_name: str) -> str:
    for file_start, short_name in files_dict.items():
        if file_name.startswith(file_start):
            return short_name

st.set_page_config(layout="centered", page_title="Littlefield Consolidator", page_icon=":bar_chart:")

st.title('Littlefield Consolidator')

uploaded_files = st.file_uploader("Upload files", type=['xlsx'], accept_multiple_files=True)

outfile = io.BytesIO()

if uploaded_files:
    with pd.ExcelWriter(outfile) as writer:
        for file in uploaded_files:
            df = pd.read_excel(file)
            short_name = file_rename(file.name)
            df.to_excel(writer, sheet_name=short_name, index=False)



    st.download_button("Download", outfile, file_name=f"Littlefield_{dt.now().strftime('%Y%m%d_%H%M')}.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.markdown("### Usage\n"
            "- Drag and drop the files you want to consolidate into the box above.\n"
            "- Click the download button to download the consolidated file.\n")