# pylint: disable=import-error, no-member, too-many-locals
'''A script that creates a Streamlit dashboard using LMNH plant data from the last 24 hours'''
from os import environ as ENV
import io
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import streamlit as st
import altair as alt
import boto3

import pymssql


BUCKET_NAME = "c16-louis-data"
PREFIX = "historical/"


def get_conn() -> pymssql.Connection:
    '''Connects to AWS RDS using pymssql'''
    load_dotenv()
    connection = pymssql.connect(host=ENV["DB_HOST"],
                                 database=ENV["DB_NAME"],
                                 user=ENV["DB_USERNAME"],
                                 password=ENV["DB_PASSWORD"],
                                 port=ENV["DB_PORT"])

    return connection


def execute_query(connection: pymssql.Connection, q: str) -> dict[list]:
    '''Executes a query using pymssql'''
    cur = connection.cursor()
    cur.execute(q)
    data = cur.fetchall()
    return data


def get_plant_information(connection: pymssql.Connection) -> pd.DataFrame:
    '''Queries the database, returns and merges tables'''
    plant_type_df = pd.read_sql('SELECT * FROM plant_type', connection)
    botanist_df = pd.read_sql('SELECT * FROM botanist', connection)
    origin_df = pd.read_sql('SELECT * FROM origin', connection)
    plant_df = pd.read_sql('SELECT * FROM plant', connection)
    merged_plant_with_type = pd.merge(plant_df, plant_type_df,
                                      on='plant_type_id', how='outer')
    merged_plant_with_type_with_botanist = pd.merge(
        merged_plant_with_type, botanist_df, on='botanist_id', how='outer')
    plant_information = pd.merge(
        merged_plant_with_type_with_botanist, origin_df, on='location_id', how='outer'
    ).sort_values("plant_id")
    return plant_information


def get_measurements(connection: pymssql.Connection) -> pd.DataFrame:
    '''Returns all measurements from the measurement table taken within 24 hours'''
    query = "SELECT * FROM measurement;"
    measurement = pd.read_sql(query, connection)
    measurement = measurement[measurement['measurement_time']
                              > datetime.now() - timedelta(hours=24)]
    return measurement


def create_botanist_pie_chart(df: pd.DataFrame) -> alt.Chart:
    '''Creates a pie chart of plant count per botanist'''
    g_df = df.groupby("botanist_name").agg(
        {"plant_id": "count"}).reset_index()

    g_df.rename(columns={"botanist_name": "Botanist",
                "plant_id": "Number of plants"}, inplace=True)

    pie = alt.Chart(g_df).mark_arc(innerRadius=75).encode(
        theta=alt.Theta(field="Number of plants", type="quantitative", stack=True, scale=alt.Scale(
            type="linear", rangeMax=1.5708, rangeMin=-1.5708)),
        color=alt.Color(field="Botanist", type="nominal",
                        scale=alt.Scale(scheme="greens"))
    )
    text = pie.mark_text(radius=110, fontSize=25, fill="black", baseline="middle", align="center"
                         ).encode(
        text=alt.Text("Number of plants:Q")
    )
    chart = (pie + text).properties(
        title="Plant Distribution by Botanist")

    return chart


def create_single_plant_chart(merged_df: pd.DataFrame, plant_id: int) -> alt.Chart:
    '''Creates a 24hr reading chart for a single plant using ID'''
    single_plant_measurement = merged_df[merged_df['plant_id'] == plant_id].sort_values(
        "measurement_time").reset_index()

    plant_name = single_plant_measurement['plant_name'].iloc[0]

    base = alt.Chart(single_plant_measurement).encode(
        alt.X('measurement_time:T').title(None),
    ).properties(width=20)

    temperature_line = base.mark_line(stroke='#e83d17', interpolate='monotone').encode(
        alt.Y('temperature').axis(
            title='Avg. Temperature (°C)', titleColor='#e83d17')
    )

    moisture_line = base.mark_line(stroke='#5276A7', interpolate='monotone').encode(
        alt.Y('moisture').axis(
            title='Moisture Content (%)', titleColor='#5276A7')
    )

    chart = alt.layer(temperature_line, moisture_line).resolve_scale(
        y='independent'
    ).properties(title=f"Temperature and moisture content of the {plant_name}")

    return chart, plant_name


def display_reading_change(merged_df: pd.DataFrame) -> float:
    """Display the difference between readings from today and all time"""
    not_today_df = merged_df[merged_df['measurement_time'].dt.day !=
                             datetime.now().day]
    temperature_mean = not_today_df['temperature'].mean()
    moisture_mean = not_today_df['moisture'].mean()
    return temperature_mean, moisture_mean


def get_temp_anomalies(merged_df: pd.DataFrame) -> pd.DataFrame:
    '''Returns a dataframe of plant_id and anomaly count (temp with |zscore| > 2.5)'''
    merged_df = merged_df.copy()
    merged_df['temperature_zscore'] = merged_df.groupby('plant_id')['temperature'].transform(
        lambda x: (x - x.mean()) / x.std()
    )

    merged_df['anomalies'] = (abs(merged_df['temperature_zscore']) > 2.5).groupby(
        merged_df['plant_id']).transform('sum')

    return merged_df[['plant_id', 'anomalies']].drop_duplicates()


def get_moisture_anomalies(merged_df: pd.DataFrame) -> pd.DataFrame:
    '''Returns a dataframe of plant_id and anomaly count (temp with |zscore| > 2.5)'''
    merged_df = merged_df.copy()
    merged_df['moisture_zscore'] = merged_df.groupby('plant_id')['moisture'].transform(
        lambda x: (x - x.mean()) / x.std()
    )

    merged_df['anomalies'] = (abs(merged_df['moisture_zscore']) > 2.5).groupby(
        merged_df['plant_id']).transform('sum')

    return merged_df[['plant_id', 'anomalies']].drop_duplicates()


def get_plant_by_temperature_anomaly_chart(
        merged_df: pd.DataFrame, plant_df: pd.DataFrame) -> alt.Chart:
    '''Returns a bar chart of the top 10 plants by anomaly count'''
    anomaly_summary = get_temp_anomalies(
        merged_df).reset_index().drop(columns=['index'])
    anomaly_df = pd.merge(anomaly_summary, plant_df,
                          how='outer', on="plant_id")
    top_10_anomalies = anomaly_df.sort_values(
        'anomalies', ascending=False).head(10)
    top_10_anomalies = top_10_anomalies[[
        'plant_id', "anomalies", "plant_name"]]
    top_10_anomalies.rename(columns={
                            "plant_id": "Plant ID", "anomalies": "Anomaly Count",
                            "plant_name": "Name"})
    chart = alt.Chart(top_10_anomalies).mark_bar().encode(
        x=alt.X('anomalies:Q', axis=alt.Axis(title='Anomaly Count')),
        y=alt.Y('plant_name:O', sort=alt.EncodingSortField(
            field='anomalies', order='descending'), axis=alt.Axis(title='Plant Name')),
        color=alt.Color('anomalies:Q', scale=alt.Scale(scheme='greens'), legend=alt.Legend(
            title='Anomaly Count')),
        tooltip=['plant_name', 'plant_id', 'anomalies']
    ).properties(
        width=600,
        height=400,
        title='Anomalous temperature results per plant in the last 24 hours'
    )

    return chart


def get_plant_by_moisture_anomaly_chart(
        merged_df: pd.DataFrame, plant_df: pd.DataFrame) -> alt.Chart:
    '''Returns a bar chart of the top 10 plants by anomaly count'''
    anomaly_summary = get_moisture_anomalies(
        merged_df).reset_index().drop(columns=['index'])
    anomaly_df = pd.merge(anomaly_summary, plant_df,
                          how='outer', on="plant_id")
    top_10_anomalies = anomaly_df.sort_values(
        'anomalies', ascending=False).head(10)
    top_10_anomalies = top_10_anomalies[[
        'plant_id', "anomalies", "plant_name"]]
    top_10_anomalies.rename(columns={
                            "plant_id": "Plant ID", "anomalies": "Anomaly Count",
                            "plant_name": "Name"})
    chart = alt.Chart(top_10_anomalies).mark_bar().encode(
        x=alt.X('anomalies:Q', axis=alt.Axis(title='Anomaly Count')),
        y=alt.Y('plant_name:O', sort=alt.EncodingSortField(
            field='anomalies', order='descending'), axis=alt.Axis(title='Plant Name')),
        color=alt.Color('anomalies:Q', scale=alt.Scale(scheme='greens'), legend=alt.Legend(
            title='Anomaly Count')),
        tooltip=['plant_name', 'plant_id', 'anomalies']
    ).properties(
        width=600,
        height=400,
        title='Anomalous moisture results per plant in the last 24 hours'
    )

    return chart


@st.cache_data(ttl=3600)
def load_data_from_s3(bucket: str, prefix: str) -> pd.DataFrame:
    """Connecting to s3 and loading data from buckets"""
    s3 = boto3.client("s3")
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)

    if "Contents" not in response:
        return pd.DataFrame()

    parquet_keys = [obj["Key"] for obj in response["Contents"]
                    if obj["Key"].endswith(".parquet")]

    dataframes = [
        pd.read_parquet(io.BytesIO(s3.get_object(
            Bucket=bucket, Key=key)["Body"].read()))
        for key in parquet_keys
    ]

    return pd.concat(dataframes, ignore_index=True) if dataframes else pd.DataFrame()


def streamlit(merged_df: pd.DataFrame, plant_df: pd.DataFrame,
              merged_long_df: pd.DataFrame) -> None:
    '''Execute the streamlit code'''

    st.title(
        ":seedling: :green[Botanist Dashboard] :seedling:")

    st.header(
        "_Liverpool Museum of Natural History_")

    yesterday_temperature_mean, yesterday_moisture_mean = display_reading_change(
        merged_df)

    temperature_mean = merged_df['temperature'].mean()
    temperature_difference_str = (
        f"{(temperature_mean - yesterday_temperature_mean).round(2)}°C "
        "since yesterday"
    )

    moisture_mean = merged_df['moisture'].mean()
    moisture_difference_str = f"{(moisture_mean-yesterday_moisture_mean).round(2)}% since yesterday"

    col1, col2 = st.columns([3, 5])

    with col1:
        st.header("Summary Stats")
        col3, col4 = st.columns(2)
        with col3:
            st.metric(label="Avg. Temperature", value=f"{temperature_mean.round(2)}°C",
                      delta=temperature_difference_str)
            st.metric(label="# Avg. Moisture:", value=f"{moisture_mean.round(2)}%",
                      delta=moisture_difference_str)

        with col4:
            st.title(":sunny:")
            st.title(":sweat_drops:")

        botanist_pie_chart = create_botanist_pie_chart(plant_df)

        st.altair_chart(botanist_pie_chart)

        st.image("carl_linnaeus.jpeg",
                 "Botanist of the month: Carl Linnaeus", width=200)

    with col2:
        st.header("Anomalous results")

        st.write(
            "Anomalies are defined as outliers outside of 2.5 \
            standard deviations from a plant's mean sensor values. \
            These anomalies may be attributable to faulty sensors, \
            and should be investigated thoroughly \
            to maintain a healthy range of flora at the museum.")

        moisture_anomaly_chart = get_plant_by_moisture_anomaly_chart(
            merged_df, plant_df)

        st.altair_chart(moisture_anomaly_chart)

        temperature_anomaly_chart = get_plant_by_temperature_anomaly_chart(
            merged_df, plant_df)

        st.altair_chart(temperature_anomaly_chart)

    st.subheader("Short-Term 24-Hour Database Insights")

    chosen_plant_id = int(st.selectbox(
        "Which plant would you like to analyse? Choose a plant ID:",
        (merged_df['plant_id'].unique()), key='short-term-id'))
    plant_chart, plant_name = create_single_plant_chart(
        merged_df, chosen_plant_id)

    st.write(f"You have selected the {plant_name}: ID {chosen_plant_id}")
    st.altair_chart(plant_chart)

    st.subheader("Long-Term Database Insights")

    chosen_plant_id_long = int(st.selectbox(
        "Which plant would you like to analyse? Choose a plant ID:",
        (merged_long_df['plant_id'].unique()), key='long-term-id'))
    plant_chart_long, plant_name_long = create_single_plant_chart(
        merged_long_df, chosen_plant_id_long)

    st.write(
        f"You have selected the {plant_name_long}: ID {chosen_plant_id_long}")
    st.altair_chart(plant_chart_long)


if __name__ == "__main__":

    st.set_page_config(
        page_title="Botanist Dashboard", layout="wide")
    load_dotenv()
    conn = get_conn()
    plants_df = get_plant_information(conn)
    measurement_df = get_measurements(conn)
    merged_24hr_df = pd.merge(plants_df, measurement_df,
                              on='plant_id', how='outer')
    longterm_df = load_data_from_s3(BUCKET_NAME, PREFIX)
    merged_longterm_df = pd.merge(
        longterm_df, plants_df[['plant_id', 'plant_name']], on='plant_id', how='left')

    streamlit(merged_24hr_df, plants_df, merged_longterm_df)
