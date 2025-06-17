import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from streamlit_plotly_events import plotly_events

# Load dataset
df = pd.read_csv('ishowspeed_cleaned_processed.csv')

# Rename columns to match YouTube version
df.rename(columns={
    'Date': 'Date Posted',
    'views': 'Views',
    'likes': 'Likes',
    'comments': 'Comments',
    'text': 'Title',
    'videoUrl': 'Video ID'
}, inplace=True)

# Parse dates
df['Date Posted'] = pd.to_datetime(df['Date Posted'], errors='coerce')
df = df.dropna(subset=['Date Posted'])  # drop rows with bad/missing dates



# Start Streamlit
st.set_page_config(layout="wide")
st.title("📈 Viewership Growth Over Time (TikTok Edition)")

# Prepare monthly aggregation
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()
monthly_views = df.groupby('Month')['Views'].agg(['sum']).reset_index()
monthly_views['Prev Views'] = monthly_views['sum'].shift(1)
monthly_views['Growth Rate (%)'] = (
    (monthly_views['sum'] - monthly_views['Prev Views']) / monthly_views['Prev Views']) * 100

# Sidebar: threshold for spike detection
threshold = st.slider("📊 Minimum Growth % to Highlight as Spike",
                      min_value=10, max_value=300, value=80, step=10)
spike_months = monthly_views[monthly_views['Growth Rate (%)'] > threshold]

# === Overall Graph ===
st.header("Overall Monthly Views with Spikes Highlighted")

fig_overall = go.Figure()
fig_overall.add_trace(go.Scatter(
    x=monthly_views['Month'],
    y=monthly_views['sum'],
    mode='lines+markers',
    name='Monthly Views',
    line=dict(color='royalblue', width=2),
    marker=dict(size=6)
))
fig_overall.add_trace(go.Scatter(
    x=spike_months['Month'],
    y=spike_months['sum'],
    mode='markers',
    marker=dict(size=10, color='red', symbol='circle'),
    name='Spikes'
))
fig_overall.update_layout(
    title='📈 Monthly Views Over Time',
    xaxis_title='Month',
    yaxis_title='Total Views',
    hovermode='x unified',
    plot_bgcolor='#1e1e1e',
    paper_bgcolor='#1e1e1e',
    font=dict(color='white'),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='gray'),
    legend=dict(
        bgcolor='#1e1e1e',
        bordercolor='gray',
        borderwidth=1
    )
)
st.plotly_chart(fig_overall, use_container_width=True)

# === Clickable version ===
st.header("Click on a Spike to See Videos from that Month")

fig_click = go.Figure()
fig_click.add_trace(go.Scatter(
    x=monthly_views['Month'],
    y=monthly_views['sum'],
    mode='lines+markers',
    name='Monthly Views',
    line=dict(color='royalblue', width=2),
    marker=dict(size=6)
))
fig_click.add_trace(go.Scatter(
    x=spike_months['Month'],
    y=spike_months['sum'],
    mode='markers',
    marker=dict(size=10, color='red', symbol='circle'),
    name='Spikes'
))
fig_click.update_layout(
    title='📈 Monthly Views Over Time (Click a Red Dot)',
    xaxis_title='Month',
    yaxis_title='Total Views',
    hovermode='x unified',
    plot_bgcolor='#1e1e1e',
    paper_bgcolor='#1e1e1e',
    font=dict(color='white'),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor='gray'),
    legend=dict(
        bgcolor='#1e1e1e',
        bordercolor='gray',
        borderwidth=1
    )
)
clicked = plotly_events(fig_click, click_event=True, key="clickable_growth_chart")

# Show videos in that spike month
if clicked:
    clicked_month = pd.to_datetime(clicked[0]['x']).to_period('M').to_timestamp()
    st.subheader(f"📅 Videos for: {clicked_month.strftime('%B %Y')}")

    videos_in_month = df[df['Month'] == clicked_month].sort_values(by='Views', ascending=False)

    for _, video in videos_in_month.iterrows():
        video_url = video['Video ID']
        st.markdown(f"""
        <div style="margin-bottom: 1em;">
            <a href="{video_url}" target="_blank" style="font-size: 16px; font-weight: bold; color: white;">
                {video['Title']}
            </a><br>
            👁️ {int(video['Views']):,} | 👍 {int(video['Likes']):,} | 💬 {int(video['Comments']):,}
        </div>
        """, unsafe_allow_html=True)
