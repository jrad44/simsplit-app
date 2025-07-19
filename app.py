import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json

# --- Page Setup ---
st.set_page_config(page_title="SimSplit Telemetry Analyzer", layout="wide")
st.markdown("<h1 style='text-align: center; color: #00ffcc;'>SimSplit • Advanced Telemetry Visualizer</h1>", unsafe_allow_html=True)

# --- File Uploads ---
col1, col2 = st.columns(2)
with col1:
    uploaded_file1 = st.file_uploader("📥 Upload the Garage61 lap you want to compare your time to (CSV file only)", type="csv", key="baseline")
with col2:
    uploaded_file2 = st.file_uploader("📥 Upload your Garage61 lap here (CSV file only)", type="csv", key="comparison")

# --- Helper Functions ---
def standardize_columns(df):
    df.columns = [col.strip() for col in df.columns]
    return df

def plot_overlaid_telemetry(df1, df2, frame=None):
    expected_cols = ['Speed', 'Throttle', 'Brake', 'Steering']
    labels = ['You', 'Comparison Lap']
    colors = ['#00ffcc', '#ff4c4c']

    available_cols = [col for col in expected_cols if col in df1.columns or col in df2.columns]
    if 'SteeringWheelAngle' in df1.columns or 'SteeringWheelAngle' in df2.columns:
        available_cols.append('SteeringWheelAngle')

    marker_x = df1.iloc[frame]['LapDistPct'] if frame is not None else None

    for col in available_cols:
        fig = go.Figure()
        for df, label, color in zip([df1, df2], labels, colors):
            if col in df.columns or (col == 'SteeringWheelAngle' and 'SteeringWheelAngle' in df.columns):
                y_data = df[col] if col in df.columns else df['SteeringWheelAngle']
                fig.add_trace(go.Scatter(x=df['LapDistPct'], y=y_data, mode='lines', name=f"{label}", line=dict(color=color)))
        if marker_x is not None:
            fig.add_vline(x=marker_x, line_width=2, line_dash="dot", line_color="white")
        if col in df1.columns:
            if col == 'Brake':
                brake_on = df1['Brake'] > 0.1
                for i in range(len(df1)):
                    if brake_on.iloc[i]:
                        fig.add_vrect(x0=df1['LapDistPct'].iloc[i], x1=df1['LapDistPct'].iloc[min(i+1, len(df1)-1)], fillcolor="red", opacity=0.2, line_width=0)
            if col == 'Throttle':
                accel_on = df1['Throttle'] > 0.1
                for i in range(len(df1)):
                    if accel_on.iloc[i]:
                        fig.add_vrect(x0=df1['LapDistPct'].iloc[i], x1=df1['LapDistPct'].iloc[min(i+1, len(df1)-1)], fillcolor="green", opacity=0.1, line_width=0)
        fig.update_layout(title=f"{col} Comparison", xaxis_title="Lap %", yaxis_title=col)
        st.plotly_chart(fig, use_container_width=True)

def plot_overlaid_gps_map(df1, df2, frame=None):
    if 'Lat' in df1.columns and 'Lon' in df1.columns and 'Lat' in df2.columns and 'Lon' in df2.columns:
        fig = px.line_mapbox(df1, lat='Lat', lon='Lon', zoom=13, height=400, color_discrete_sequence=["#00ffcc"])
        fig.add_trace(px.line_mapbox(df2, lat='Lat', lon='Lon').data[0])
        fig.data[1].line.color = "#ff4c4c"
        if frame is not None:
            marker1_lat = df1.iloc[frame]['Lat']
            marker1_lon = df1.iloc[frame]['Lon']
            marker2_lat = df2.iloc[frame]['Lat']
            marker2_lon = df2.iloc[frame]['Lon']
            fig.add_trace(px.scatter_mapbox(lat=[marker1_lat], lon=[marker1_lon], marker=dict(size=12, color="#00ffcc")).data[0])
            fig.add_trace(px.scatter_mapbox(lat=[marker2_lat], lon=[marker2_lon], marker=dict(size=12, color="#ff4c4c")).data[0])
        fig.update_layout(title="Driving Line Comparison", mapbox_style="carto-darkmatter", margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

# --- Main Logic ---
if uploaded_file1 and uploaded_file2:
    df1 = pd.read_csv(uploaded_file1)
    df2 = pd.read_csv(uploaded_file2)
    df1 = standardize_columns(df1)
    df2 = standardize_columns(df2)

    st.subheader("📊 You vs Comparison Lap Telemetry Overlaid")

    total_frames = min(len(df1), len(df2))
    frame = st.slider("Playback Position", min_value=0, max_value=total_frames-1, value=total_frames-1)

    plot_overlaid_telemetry(df1, df2, frame)
    plot_overlaid_gps_map(df1, df2, frame)
