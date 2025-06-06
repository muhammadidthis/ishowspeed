import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('ishowspeed_cleaned_processed.csv', parse_dates=['Date Posted'])

# Rename columns to match YouTube version
df.rename(columns={
    'Date': 'Date Posted',
    'views': 'Views',
    'likes': 'Likes',
    'comments': 'Comments',
    'text': 'Title',
    'videoUrl': 'Video ID'
}, inplace=True)

# Handle missing or invalid dates
df = df[df['Date Posted'].notna()]
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()

# Group by month
monthly_stats = df.groupby('Month')['Views'].agg(['sum', 'count']).reset_index()
monthly_stats.rename(columns={'sum': 'Total Views', 'count': 'Video Count'}, inplace=True)

# Calculate growth rate
monthly_stats['Growth Rate (%)'] = monthly_stats['Total Views'].pct_change().fillna(0) * 100
monthly_stats['Spike'] = monthly_stats['Growth Rate (%)'] > 50

# Title
st.set_page_config(layout="wide")
st.title("📈 IShowSpeed's Viewership Growth (All Time)")
st.markdown("Visualizing IShowSpeed’s TikTok growth and identifying spike months.")

# Line chart with spike markers
fig_views = px.line(
    monthly_stats,
    x='Month',
    y='Total Views',
    title='Total Monthly Views Over Time',
    markers=True,
    hover_data={'Growth Rate (%)': ':.2f'}
)

spike_months = monthly_stats[monthly_stats['Spike']]
fig_views.add_scatter(
    x=spike_months['Month'],
    y=spike_months['Total Views'],
    mode='markers',
    marker=dict(size=10, color='red', symbol='circle'),
    name='Spike Months'
)
st.plotly_chart(fig_views, use_container_width=True)

# Bar chart for growth rate
st.subheader("📊 Monthly Growth Rate (%) Over Time")
fig_growth = px.bar(
    monthly_stats,
    x='Month',
    y='Growth Rate (%)',
    color='Growth Rate (%)',
    color_continuous_scale='Plasma',
    title='Growth Rate of Monthly Views (%)'
)
st.plotly_chart(fig_growth, use_container_width=True)

# KPI summary
st.subheader("📌 Lifetime Viewership Summary")
col1, col2, col3 = st.columns(3)
col1.metric("Total Views", f"{int(monthly_stats['Total Views'].sum()):,}")
col2.metric("Avg Views/Month", f"{int(monthly_stats['Total Views'].mean()):,}")
col3.metric("Total Months", f"{monthly_stats.shape[0]}")

# Spike Month Video Breakdown
st.header("🚀 Spike Months: Videos that Drove the Growth")
for _, row in spike_months.iterrows():
    month = row['Month']
    videos_in_month = df[df['Month'] == month].sort_values(by='Views', ascending=False)

    with st.expander(f"📅 {month.strftime('%B %Y')} (↑ {row['Growth Rate (%)']:.2f}%) - {len(videos_in_month)} videos"):
        for _, video in videos_in_month.iterrows():
            # Handle video ID (TikTok may have full URLs)
            video_id = video['Video ID']
            is_url = isinstance(video_id, str) and video_id.startswith("http")
            video_url = video_id if is_url else f"https://www.tiktok.com/@ishowspeed/video/{video_id}"
            thumbnail_url = "https://www.tiktok.com/favicon.ico"  # No public thumbnails

            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 1em;">
                <a href="{video_url}" target="_blank">
                    <img src="{thumbnail_url}" alt="Thumbnail" style="width: 60px; border-radius: 8px; margin-right: 15px;">
                </a>
                <div>
                    <a href="{video_url}" target="_blank" style="font-size: 16px; font-weight: bold;">{video['Title']}</a><br>
                    👁️ {int(video['Views']):,} | 👍 {int(video['Likes']):,} | 💬 {int(video['Comments']):,}
                </div>
            </div>
            """, unsafe_allow_html=True)
