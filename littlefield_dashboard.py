import streamlit as st
import pandas as pd
from plotly import express as px
from plotly import graph_objects as go

st.set_page_config(layout="wide", page_title="Littlefield Dashboard", page_icon=":bar_chart:")

st.title('Littlefield Dashboard')

data, notes, background = st.tabs(["Data", "Notes", "Background"])

KITS_IN_LOT = 60
ROLLING_WINDOW_DAYS = 3


def update_fig_layout(fig):
    # fig.update_layout(title_font_size=48, xaxis_title_font_size=36, xaxis_tickfont_size=32,
    #                   yaxis_title_font_size=36, yaxis_tickfont_size=32, legend_font_size=32,
    #                   legend_title_font_size=28)
    # fig.update_xaxes(tickfont=dict(color="black"), titlefont=dict(color="black"))
    # fig.update_yaxes(tickfont=dict(color="black"), titlefont=dict(color="black"))
    # fig.update_traces(line_width=5)
    return fig


with (data):
    # uploaded_file = st.file_uploader("Upload files", type=['xlsx'])
    uploaded_file = open("./Littlefield data_day_486_240729_0607.xlsx", "rb")

    if uploaded_file:
        all_data = pd.read_excel(uploaded_file, index_col=0)
        text_data = pd.read_excel(uploaded_file, sheet_name="Text Data", index_col=0)
        transaction_data = pd.read_excel(uploaded_file, sheet_name="Transaction History")
        inventory_data = pd.read_excel(uploaded_file, sheet_name="Inventory Data", index_col=0)

        cumulative_flow_df = all_data.loc[:, ["Daily accepted jobs"]]
        cumulative_flow_df.loc[:, "Completed jobs"] = all_data["Daily Completed Jobs - Seven day"] + all_data[
            "Daily Completed Jobs - One day"] + all_data["Daily Completed Jobs - Half day"]
        cumulative_flow_df.loc[:, "WIP (jobs)"] = (
                (all_data["Station 1 Queue"] + all_data["Station 2 Queue"] + all_data[
                    "Station 3 Queue"]) / KITS_IN_LOT)

        day_value = text_data.loc["Day", "Value"]
        balance_value = text_data.loc["Balance", "Value"]

        with st.container():
            left_column, right_column = st.columns(2)

            start_day = left_column.number_input("Start day", min_value=all_data.index[0], max_value=all_data.index[-1],
                                                 value=(all_data.index[-1]) - 30)
            end_day = right_column.number_input("End day", min_value=all_data.index[0], max_value=all_data.index[-1],
                                                value=all_data.index[-1])

            day_range = [start_day, end_day]
            inventory_range = [start_day, end_day + 0.8]

            rolling_window = left_column.number_input("Rolling window (days)", min_value=1, max_value=30, value=3)
            trailing_window = right_column.number_input("Lookback duration (days)", min_value=1, max_value=30, value=5)

        total_wip = (all_data.iloc[-1, 3] + all_data.iloc[-1, 4] + all_data.iloc[-1, 5]) / KITS_IN_LOT

        st.divider()

        with st.container():
            left_column, left_middle_column, right_middle_column, right_column = st.columns(4)

            left_column.markdown(f"**Day:** {day_value}")
            left_column.markdown(f"**Balance:** ${balance_value}")
            left_middle_column.markdown(f"**Inventory level:** {inventory_data.iloc[-1, 1] / 60:.2f}")
            left_middle_column.markdown(f"**Total WIP:** {total_wip:.2f}")
            right_middle_column.markdown(
                f"**{trailing_window} day mean inbound jobs:** {cumulative_flow_df[-trailing_window:]['Daily accepted jobs'].mean():.1f}")
            right_middle_column.markdown(
                f"**{trailing_window} day mean completed jobs:** {cumulative_flow_df[-trailing_window:]['Completed jobs'].mean():.1f}")

            right_column.markdown(f"**{text_data.loc["Order Status", "Value"]}**")
            st.markdown(
                '<div style="text-align: center"><i> Above data is referenced to last day of simulator data (regardless of Start Day/End Day) </i></div>',
                unsafe_allow_html=True)

        if all_data[-1:]["Jobs Waiting Kits"].values > 0:
            st.markdown(f":red[**Jobs waiting kits:** {all_data[-1:]['Jobs Waiting Kits'].values[0]}]")

        st.divider()

        left_column, right_column = st.columns(2)

        wip_cumulative_flow_fig = go.Figure(
            data=[
                go.Scatter(x=cumulative_flow_df.index,
                           y=cumulative_flow_df["Daily accepted jobs"].rolling(window=rolling_window).mean(),
                           name="Daily accepted jobs", mode="lines",
                           marker=dict(color=px.colors.qualitative.Alphabet[0])),
                go.Scatter(x=cumulative_flow_df.index,
                           y=cumulative_flow_df["Completed jobs"].rolling(window=rolling_window).mean(),
                           name="Completed jobs",
                           mode="lines", marker=dict(color=px.colors.qualitative.Alphabet[1])),
                go.Scatter(x=cumulative_flow_df.index,
                           y=cumulative_flow_df["WIP (jobs)"].rolling(window=rolling_window).mean(), name="WIP",
                           mode="lines", marker=dict(color=px.colors.qualitative.Alphabet[2])),
            ],
            layout=go.Layout(title=f"Cumulative Flow Diagram - {rolling_window} day rolling average", ),
        )
        wip_cumulative_flow_fig = update_fig_layout(wip_cumulative_flow_fig)
        wip_cumulative_flow_fig.update_yaxes(title_text="Jobs")
        wip_cumulative_flow_fig.update_xaxes(title_text="Day", range=day_range)
        left_column.plotly_chart(wip_cumulative_flow_fig)

        lead_time_fig = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Daily Avg Lead Time - Seven day"], name="Seven day",
                           mode="lines", marker=dict(color=px.colors.qualitative.Dark24[0])),
                go.Scatter(x=all_data.index, y=all_data["Daily Avg Lead Time - One day"], name="One day", mode="lines",
                           marker=dict(color=px.colors.qualitative.Dark24[1])),
                go.Scatter(x=all_data.index, y=all_data["Daily Avg Lead Time - Half day"], name="Half day",
                           mode="lines", marker=dict(color=px.colors.qualitative.Dark24[2])),
            ],
            layout=go.Layout(title="Average Lead Time", ),
        )

        lead_time_fig = update_fig_layout(lead_time_fig)
        lead_time_fig.update_yaxes(title_text="Days")
        lead_time_fig.update_xaxes(title_text="Day", range=day_range)
        right_column.plotly_chart(lead_time_fig)

        inventory_level_fig = px.line(inventory_data, x="day", y="data",
                                      title="Inventory Level (kits)", range_x=inventory_range)
        inventory_level_fig = update_fig_layout(inventory_level_fig)
        inventory_level_fig.update_yaxes(title_text="Kits")
        inventory_level_fig.update_xaxes(title_text="Day")
        left_column.plotly_chart(inventory_level_fig)

        cash_on_hand_fig = px.line(all_data, x=all_data.index, y=["Cash on Hand"], title="Cash on Hand",
                                   range_x=day_range)
        cash_on_hand_fig = update_fig_layout(cash_on_hand_fig)
        cash_on_hand_fig.update_yaxes(title_text="Dollars")
        cash_on_hand_fig.update_xaxes(title_text="Day")
        right_column.plotly_chart(cash_on_hand_fig)

        queue_plot = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Station 1 Queue"], name="Station 1", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 2 Queue"], name="Station 2", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 3 Queue"], name="Station 3", mode="lines", ),
            ],
            layout=go.Layout(title="Consolidated Queue Data (kits)", ),
        )

        queue_plot = update_fig_layout(queue_plot)
        queue_plot.update_yaxes(title_text="Kits")
        queue_plot.update_xaxes(title_text="Day", range=day_range)
        left_column.plotly_chart(queue_plot)

        utilization_plot = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Station 1 Utilization"], name="Station 1", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 2 Utilization"], name="Station 2", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 3 Utilization"], name="Station 3", mode="lines", ),
            ],
            layout=go.Layout(title="Consolidated Utilization", ),
        )

        utilization_plot = update_fig_layout(utilization_plot)
        utilization_plot.update_yaxes(title_text="Utilization index")
        utilization_plot.update_xaxes(title_text="Day", range=day_range)
        right_column.plotly_chart(utilization_plot)

        accepted_kits_fig = px.line(all_data, x=all_data.index, y=["Daily accepted jobs"],
                                    title="Accepted jobs", range_x=day_range)
        accepted_kits_fig = update_fig_layout(accepted_kits_fig)
        accepted_kits_fig.update_yaxes(title_text="Jobs")
        accepted_kits_fig.update_xaxes(title_text="Day")
        left_column.plotly_chart(accepted_kits_fig)

        completed_jobs_fig = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Daily Completed Jobs - Seven day"], name="Seven day",
                           mode="lines", marker=dict(color=px.colors.qualitative.Dark24[0])),
                go.Scatter(x=all_data.index, y=all_data["Daily Completed Jobs - One day"], name="One day", mode="lines",
                           marker=dict(color=px.colors.qualitative.Dark24[1])),
                go.Scatter(x=all_data.index, y=all_data["Daily Completed Jobs - Half day"], name="Half day",
                           mode="lines", marker=dict(color=px.colors.qualitative.Dark24[2])),
            ],
            layout=go.Layout(title="Completed Jobs", ),
        )

        completed_jobs_fig = update_fig_layout(completed_jobs_fig)
        completed_jobs_fig.update_yaxes(title_text="Jobs")
        completed_jobs_fig.update_xaxes(title_text="Day", range=day_range)
        right_column.plotly_chart(completed_jobs_fig)

        utilization_smoothed = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Station 1 Utilization"].rolling(window=rolling_window).mean(),
                           name="Station 1", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 2 Utilization"].rolling(window=rolling_window).mean(),
                           name="Station 2", mode="lines", ),
                go.Scatter(x=all_data.index, y=all_data["Station 3 Utilization"].rolling(window=rolling_window).mean(),
                           name="Station 3", mode="lines", ),
            ],
            layout=go.Layout(title=f"Utilization - {rolling_window} day rolling average", ),
        )

        utilization_smoothed = update_fig_layout(utilization_smoothed)
        utilization_smoothed.update_yaxes(title_text="Utilization index")
        utilization_smoothed.update_xaxes(title_text="Day", range=day_range)
        left_column.plotly_chart(utilization_smoothed)

        avg_rev_per_job_fig = go.Figure(
            data=[
                go.Scatter(x=all_data.index, y=all_data["Avg Rev per Job  - Seven day"],
                           name="Seven day", mode="lines", marker=dict(color=px.colors.qualitative.Dark24[0])),
                go.Scatter(x=all_data.index, y=all_data["Avg Rev per Job  - One day"],
                           name="One day", mode="lines", marker=dict(color=px.colors.qualitative.Dark24[1])),
                go.Scatter(x=all_data.index, y=all_data["Avg Rev per Job  - Half day"],
                           name="Half day", mode="lines", marker=dict(color=px.colors.qualitative.Dark24[2])),
            ],
            layout=go.Layout(title="Average Revenue per Job", ),
        )

        avg_rev_per_job_fig = update_fig_layout(avg_rev_per_job_fig)
        avg_rev_per_job_fig.update_yaxes(title_text="Dollars")
        avg_rev_per_job_fig.update_xaxes(title_text="Day", range=day_range)
        right_column.plotly_chart(avg_rev_per_job_fig)

        waiting_kits_fig = px.line(all_data, x=all_data.index, y=["Jobs Waiting Kits"], title="Jobs Waiting Kits",
                                   range_x=day_range)
        waiting_kits_fig = update_fig_layout(waiting_kits_fig)
        waiting_kits_fig.update_yaxes(title_text="Jobs")
        waiting_kits_fig.update_xaxes(title_text="Day")
        left_column.plotly_chart(waiting_kits_fig)

        right_column.markdown("**Transaction history**")
        filter_text = right_column.text_input("Filter by parameter")
        transaction_data_filtered = transaction_data[(
                (transaction_data.Day <= day_range[1]) & (transaction_data.Day >= day_range[0]) & (
            transaction_data["Parameter"].str.contains(filter_text, case=False)))]
        right_column.dataframe(transaction_data_filtered, hide_index=True, use_container_width=True)

        left_column.markdown("**Stats**")
        left_column.dataframe(
            all_data.loc[start_day:end_day,
            ["Daily accepted jobs", "Daily Completed Jobs - Seven day", "Daily Completed Jobs - One day",
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
