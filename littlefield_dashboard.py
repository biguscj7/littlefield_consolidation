import streamlit as st
import pandas as pd
from plotly import express as px

st.set_page_config(layout="wide", page_title="Littlefield Dashboard", page_icon=":bar_chart:")

st.title('Littlefield Dashboard')

data, notes, background = st.tabs(["Data", "Notes", "Background"])

KITS_IN_LOT = 60
ROLLING_WINDOW_DAYS = 3

with data:
    uploaded_file = st.file_uploader("Upload files", type=['xlsx'])

    if uploaded_file:
        all_data = pd.read_excel(uploaded_file, index_col=0)
        text_data = pd.read_excel(uploaded_file, sheet_name="Text Data", index_col=0)
        transaction_data = pd.read_excel(uploaded_file, sheet_name="Transaction History")
        inventory_data = pd.read_excel(uploaded_file, sheet_name="Inventory Data", index_col=0)

        cumulative_flow_df = all_data[["Daily accepted kits"]]
        cumulative_flow_df["Completed kits"] = all_data["Daily Completed Jobs - Seven day"] + all_data[
            "Daily Completed Jobs - One day"] + all_data["Daily Completed Jobs - Half day"]
        cumulative_flow_df["WIP"] = (all_data["Station 1 Queue"] + all_data["Station 2 Queue"] + all_data[
            "Station 3 Queue"]) / KITS_IN_LOT

        day_value = text_data.loc["Day", "Value"]
        balance_value = text_data.loc["Balance", "Value"]

        with st.container():
            left_column, right_column = st.columns(2)

            start_day = left_column.number_input("Start day", min_value=all_data.index[0], max_value=all_data.index[-1],
                                                 value=all_data.index[0])
            end_day = right_column.number_input("End day", min_value=all_data.index[0], max_value=all_data.index[-1],
                                                value=all_data.index[-1])

            day_range = [start_day, end_day]
            inventory_range = [start_day, end_day + 0.8]

        total_wip = (all_data.iloc[-1, 3] + all_data.iloc[-1, 4] + all_data.iloc[-1, 5]) / KITS_IN_LOT

        st.divider()

        with st.container():
            left_column, left_middle_column, right_middle_column, right_column = st.columns(4)

            left_column.markdown(f"**Day:** {day_value}")
            left_column.markdown(f"**Balance:** ${balance_value}")
            left_middle_column.markdown(f"**Inventory level:** {inventory_data.iloc[-1, 1] / 60:.0f}")
            left_middle_column.markdown(f"**Total WIP:** {total_wip:.0f}")
            right_middle_column.markdown(
                f"**Last 24 days mean inbound jobs:** {all_data[-24:]['Daily accepted kits'].mean():.1f}")
            right_middle_column.markdown(
                f"**Last 24 days mean completed jobs:** {all_data[-24:]['Daily Completed Jobs - Seven day'].mean():.1f}")

            right_column.markdown(f"**{text_data.loc["Order Status", "Value"]}**")

        if all_data[-1:]["Jobs Waiting Kits"].values > 0:
            st.markdown(f":red[**Jobs waiting kits:** {all_data[-1:]['Jobs Waiting Kits'].values[0]}]")

        st.divider()

        left_column, right_column = st.columns(2)

        wip_cumulative_flow_fig = px.line(cumulative_flow_df.rolling(window=ROLLING_WINDOW_DAYS).mean(),
                                          x=cumulative_flow_df.index,
                                          y=["Daily accepted kits", "Completed kits", "WIP"],
                                          title=f"Cumulative Flow Diagram - {ROLLING_WINDOW_DAYS} day rolling average",
                                          range_x=day_range)
        left_column.plotly_chart(wip_cumulative_flow_fig)

        lead_time_fig = px.line(all_data, x=all_data.index,
                                y=['Daily Avg Lead Time - Seven day', 'Daily Avg Lead Time - One day',
                                   'Daily Avg Lead Time - Half day'],
                                title="Average Lead Time", range_x=day_range)
        right_column.plotly_chart(lead_time_fig)

        cash_on_hand_fig = px.line(all_data, x=all_data.index, y=["Cash on Hand"], title="Cash on Hand",
                                   range_x=day_range)
        right_column.plotly_chart(cash_on_hand_fig)

        inventory_level_fig = px.line(inventory_data, x="day", y="data",
                                      title="Inventory Level", range_x=inventory_range)
        left_column.plotly_chart(inventory_level_fig)

        queue_plot = px.line(all_data, x=all_data.index, y=["Station 1 Queue", "Station 2 Queue", "Station 3 Queue"],
                             title="Consolidated Queue Data", range_x=day_range)
        left_column.plotly_chart(queue_plot)

        utilization_plot = px.line(all_data, x=all_data.index,
                                   y=['Station 1 Utilization', 'Station 2 Utilization', 'Station 3 Utilization'],
                                   title="Consolidated Utilization", range_x=day_range)
        right_column.plotly_chart(utilization_plot)

        completed_jobs_fig = px.line(all_data, x=all_data.index,
                                     y=['Daily Completed Jobs - Seven day', 'Daily Completed Jobs - One day',
                                        'Daily Completed Jobs - Half day'],
                                     title="Completed Jobs", range_x=day_range)
        left_column.plotly_chart(completed_jobs_fig)


        waiting_kits_fig = px.line(all_data, x=all_data.index, y=["Jobs Waiting Kits"], title="Jobs Waiting Kits",
                                   range_x=day_range)
        right_column.plotly_chart(waiting_kits_fig)

        avg_rev_per_job_fig = px.line(all_data, x=all_data.index,
                                      y=["Avg Rev per Job  - Seven day", "Avg Rev per Job  - One day",
                                         "Avg Rev per Job  - Half day"], title="Average Revenue per Job",
                                      range_x=day_range)
        left_column.plotly_chart(avg_rev_per_job_fig)

        accepted_kits_fig = px.line(all_data, x=all_data.index, y=["Daily accepted kits"],
                                    title="Accepted kits", range_x=day_range)
        right_column.plotly_chart(accepted_kits_fig)


        right_column.markdown("**Transaction history**")
        right_column.dataframe(transaction_data, hide_index=True, use_container_width=True)

        left_column.markdown("**Stats**")
        left_column.dataframe(
            all_data.loc[start_day:end_day,
            ["Daily accepted kits", "Daily Completed Jobs - Seven day", "Daily Completed Jobs - One day",
             "Daily Completed Jobs - Half day"]].describe().loc[['count', 'mean', 'std', 'min', 'max']], )

        left_column.markdown("*Stats based on day range selected*")

with notes:
    st.markdown("### Usage\n"
                "- Download consolidated data file from MS Teams.\n"
                "- Go to the 'data' tab and drag and drop the file you want or browse for it.\n"
                "- Charts will be generated for the data you uploaded.\n")

    st.markdown("### Help / issues\n"
                "- Contact Mark")

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
