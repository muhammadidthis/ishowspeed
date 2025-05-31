import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
df = pd.read_csv('ishowspeed_yt_dataset_all.csv', parse_dates=['Date Posted'])

# Prepare data
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()

# Group by month
monthly_stats = df.groupby('Month')['Views'].agg(
    ['sum', 'count']).reset_index()
monthly_stats.rename(
    columns={'sum': 'Total Views', 'count': 'Video Count'}, inplace=True)

# Calculate growth rate
monthly_stats['Growth Rate (%)'] = monthly_stats['Total Views'].pct_change(
).fillna(0) * 100
monthly_stats['Spike'] = monthly_stats['Growth Rate (%)'] > 50

# Title
st.title("📈 IShowSpeed's Viewership Growth (All Time)")
st.markdown(
    "Visualizing IShowSpeed’s YouTube channel growth and identifying spike months.")

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

# Show spike month video breakdown
# ---- SPIKE MONTHS EXPANDABLE VIEW ----
st.header("🚀 Spike Months: Videos that Drove the Growth")

for _, row in spike_months.iterrows():
    month = row['Month']
    videos_in_month = df[df['Month'] == month].sort_values(
        by='Views', ascending=False)

    with st.expander(f"📅 {month.strftime('%B %Y')} (↑ {row['Growth Rate (%)']:.2f}%) - {len(videos_in_month)} videos"):
        for _, video in videos_in_month.iterrows():
            video_url = f"https://www.youtube.com/watch?v={video['Video ID']}"
            thumb_url = f"https://img.youtube.com/vi/{video['Video ID']}/hqdefault.jpg"

            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 1em;">
                <a href="{video_url}" target="_blank">
                    <img src="{thumb_url}" alt="Thumbnail" style="width: 160px; border-radius: 8px; margin-right: 15px;">
                </a>
                <div>
                    <a href="{video_url}" target="_blank" style="font-size: 16px; font-weight: bold;">{video['Title']}</a><br>
                    👁️ {int(video['Views']):,} | 👍 {int(video['Likes']):,} | 💬 {int(video['Comments']):,}
                </div>
            </div>
            """, unsafe_allow_html=True)
