import io
from datetime import datetime as dt
from functools import reduce

import plotly.graph_objs
import streamlit as st
import pandas as pd
from plotly import express as px

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
}


def file_rename(file_name: str) -> str:
    for file_start, short_name in files_dict.items():
        if file_name.startswith(file_start):
            return short_name


def merge_data_and_plot(data: list, title: str = None) -> plotly.graph_objs.Figure:
    merge_df = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True),
                      data)
    return px.line(merge_df, x=merge_df.index, y=merge_df.columns, title=title)


st.set_page_config(layout="wide", page_title="Littlefield Consolidator", page_icon=":bar_chart:")

st.title('Littlefield Consolidator')

notes, data, background = st.tabs(["Notes", "Data", "Background"])

with notes:
    st.markdown("### Usage\n"
                "- Download desired files from the Littlefield simulation (do not change file names).\n"
                "- Go to the 'data' tab and drag and drop the files you want or browse for them.\n"
                "- Charts will be generated for the data you uploaded.\n"
                "- Click the download button to download the consolidated excel file.\n")

    st.markdown("### Caveats\n"
                "- This only currently handles the filenames as assigned by the Littlefield site.\n"
                "- If you upload a file twice, the second file will likely overwrite the first.\n")

    st.markdown("### Help / issues\n"
                "- Contact Mark")

with data:
    uploaded_files = st.file_uploader("Upload files", type=['xlsx'], accept_multiple_files=True)

    outfile = io.BytesIO()

    if uploaded_files:
        dataframes = []

        with pd.ExcelWriter(outfile) as writer:
            for file in uploaded_files:
                df = pd.read_excel(file, index_col=0)
                short_name = file_rename(file.name)
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

            all_data = reduce(lambda left, right: pd.merge(left, right, left_index=True, right_index=True),
                              dataframes)

            all_data.to_excel(writer, sheet_name="All Data")

        st.download_button("Download", outfile, file_name=f"Littlefield_{dt.now().strftime('%Y%m%d_%H%M')}.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        left_column, right_column = st.columns(2)

        accepted_kits_fig = px.line(all_data, x=all_data.index, y=["Daily accepted kits"],
                                    title="Accepted kits")
        left_column.plotly_chart(accepted_kits_fig)
        #left_column.markdown(
        #    f"#### Daily kits\nAverage: {all_data.mean()["Daily accepted kits"]: .2f} / Std dev: {all_data.std(ddof=0)["Daily accepted kits"]: .2f}\n")

        inventory_level_fig = px.line(all_data, x=all_data.index, y=["Kit Inventory Level"],
                                      title="Inventory Level")
        right_column.plotly_chart(inventory_level_fig)

        queue_plot = px.line(all_data, x=all_data.index, y=["Station 1 Queue", "Station 2 Queue", "Station 3 Queue"],
                             title="Consolidated Queue Data")
        left_column.plotly_chart(queue_plot)

        utilization_plot = px.line(all_data, x=all_data.index,
                                   y=['Station 1 Utilization', 'Station 2 Utilization', 'Station 3 Utilization'],
                                   title="Consolidated Utilization")
        right_column.plotly_chart(utilization_plot)

        completed_jobs_fig = px.line(all_data, x=all_data.index,
                                     y=['Daily Completed Jobs - Seven day', 'Daily Completed Jobs - One day',
                                        'Daily Completed Jobs - Half day'],
                                     title="Completed Jobs")
        left_column.plotly_chart(completed_jobs_fig)

        lead_time_fig = px.line(all_data, x=all_data.index,
                                y=['Daily Avg Lead Time - Seven day', 'Daily Avg Lead Time - One day',
                                   'Daily Avg Lead Time - Half day'],
                                title="Average Lead Time")
        right_column.plotly_chart(lead_time_fig)

with background:
    st.markdown("### Machine costs\n"
                "- Station 1: $90,000\n"
                "- Station 2: $80,000\n"
                "- Station 3: $100,000")
    st.markdown("### Order details\n"
                "- Lead time: 4 days\n"
                "- Fixed order cost: $1000/order\n"
                "- Order step:\n"
                "   - batches of 60 kits @ $10/kit\n"
                "   - i.e. $600 step\n")
