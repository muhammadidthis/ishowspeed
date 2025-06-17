import streamlit as st
import pandas as pd
import plotly.express as px
import calendar

# Load dataset
df = pd.read_csv('ishowspeed_yt_dataset_all.csv', parse_dates=['Date Posted'])

st.set_page_config(layout="wide")
st.title("🎥 Views Trend by Content Type")

# --- Year-Month Range selectors at the top ---
years = sorted(df['Date Posted'].dt.year.unique())
months = list(range(1, 13))

col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
with col1:
    start_year = st.selectbox("Start Year", years, index=0)
with col2:
    start_month = st.selectbox(
        "Start Month", months, index=0, format_func=lambda x: calendar.month_name[x])
with col3:
    end_year = st.selectbox("End Year", years, index=len(years) - 1)
with col4:
    end_month = st.selectbox(
        "End Month", months, index=11, format_func=lambda x: calendar.month_name[x])

start_date = pd.to_datetime(f"{start_year}-{start_month}-01")
end_day = calendar.monthrange(end_year, end_month)[1]
end_date = pd.to_datetime(f"{end_year}-{end_month}-{end_day}")

# Filter dataset by date range
df_filtered = df[(df['Date Posted'] >= start_date)
                 & (df['Date Posted'] <= end_date)]

# Prepare month column after filtering
df_filtered['Month'] = df_filtered['Date Posted'].dt.to_period(
    'M').dt.to_timestamp()

# === Multiline Chart: Monthly Views per Content Type (ALL content types) ===
st.subheader("Monthly Views by Content Type (All Types)")

monthly_all = (
    df_filtered.groupby(['Month', 'Content Type'])['Views']
    .sum()
    .reset_index()
)

fig_multi = px.line(
    monthly_all,
    x='Month',
    y='Views',
    color='Content Type',
    labels={'Views': 'Total Views', 'Month': 'Month',
            'Content Type': 'Content Type'},
    title='Monthly Views Over Time by Content Type',
    template='plotly_dark'
)
st.plotly_chart(fig_multi, use_container_width=True)

# --- Total Videos per Content Type Bar Chart ---
video_counts = df_filtered.groupby('Content Type')[
    'Video ID'].count().reset_index()
video_counts = video_counts.rename(columns={'Video ID': 'Total Videos'})

st.subheader("Total Videos per Content Type")
fig_bar = px.bar(
    video_counts.sort_values('Total Videos', ascending=False),
    x='Content Type',
    y='Total Videos',
    labels={'Total Videos': 'Number of Videos',
            'Content Type': 'Content Type'},
    template='plotly_dark',
    title='Total Number of Videos Uploaded per Content Type'
)
st.plotly_chart(fig_bar, use_container_width=True)

# --- Total Views per Content Type Bar Chart ---
st.subheader("Total Views per Content Type")

total_views_by_type = df_filtered.groupby(
    'Content Type')['Views'].sum().reset_index()

fig_total_views = px.bar(
    total_views_by_type.sort_values('Views', ascending=False),
    x='Content Type',
    y='Views',
    title='Total Views per Content Type',
    labels={'Content Type': 'Content Type', 'Views': 'Total Views'},
    template='plotly_dark'
)

st.plotly_chart(fig_total_views, use_container_width=True)


# Select Content Type for detailed view
content_types = video_counts['Content Type'].dropna().unique()
selected_content = st.selectbox(
    "Select Content Type for Trend Analysis", options=sorted(content_types))

# Filter data for selected content type
filtered_df = df_filtered[df_filtered['Content Type'] == selected_content]

if filtered_df.empty:
    st.warning(
        "No data available for the selected content type in the chosen date range.")
    st.stop()

# Monthly total views for selected content type
monthly_views = filtered_df.groupby('Month')['Views'].sum().reset_index()

# Calculate growth rate over time
monthly_views['Prev Views'] = monthly_views['Views'].shift(1)
monthly_views['Growth Rate (%)'] = (
    (monthly_views['Views'] - monthly_views['Prev Views']) / monthly_views['Prev Views']) * 100
monthly_views = monthly_views.fillna(0)



# Plot Growth Rate Over Time
fig_growth = px.bar(
    monthly_views,
    x='Month',
    y='Growth Rate (%)',
    title=f"Monthly View Growth Rate for '{selected_content}' Content",
    labels={'Growth Rate (%)': 'Growth Rate (%)', 'Month': 'Month'},
    template='plotly_dark'
)
st.plotly_chart(fig_growth, use_container_width=True)

# Average likes and comments per video for selected content type
avg_likes = filtered_df['Likes'].mean()
avg_comments = filtered_df['Comments'].mean()

col1, col2 = st.columns(2)
col1.metric(label="Average Likes per Video", value=f"{avg_likes:.0f}")
col2.metric(label="Average Comments per Video", value=f"{avg_comments:.0f}")

# Top 5 videos by views for selected content type
st.subheader(f"Top 5 Videos in '{selected_content}' by Views")
top_videos = filtered_df.sort_values('Views', ascending=False).head(5)

for _, video in top_videos.iterrows():
    video_url = f"https://www.youtube.com/watch?v={video['Video ID']}"
    thumbnail_url = f"https://img.youtube.com/vi/{video['Video ID']}/hqdefault.jpg"
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1em;">
        <a href="{video_url}" target="_blank">
            <img src="{thumbnail_url}" alt="Thumbnail" style="width: 160px; border-radius: 8px; margin-right: 15px;">
        </a>
        <div>
            <a href="{video_url}" target="_blank" style="font-size: 16px; font-weight: bold; color: white;">{video['Title']}</a><br>
            👁️ {int(video['Views']):,} | 👍 {int(video['Likes']):,} | 💬 {int(video['Comments']):,}
        </div>
    </div>
    """, unsafe_allow_html=True)
