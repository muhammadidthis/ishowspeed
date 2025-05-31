import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

# Load data
df = pd.read_csv('ishowspeed_yt_dataset_all.csv', parse_dates=['Date Posted'])

# Prepare data
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()

monthly_views = df.groupby('Month')['Views'].sum().reset_index()
monthly_views['Growth'] = monthly_views['Views'].pct_change() * \
    100  # % growth vs previous month
monthly_views['Growth'].fillna(0, inplace=True)

# Sidebar spike threshold slider
spike_threshold = st.slider(
    "Spike Threshold (% growth month-over-month)",
    min_value=0,
    max_value=200,
    value=50,
    step=5,
    help="Only show spikes with growth above this percentage."
)

# Identify spike months
spike_months = monthly_views[monthly_views['Growth'] > spike_threshold]

st.title("📈 IShowSpeed - Viewership Growth Over Time")

st.markdown(
    "This graph shows the total monthly views for IShowSpeed's YouTube channel, "
    "with red markers highlighting significant spikes in growth above the selected threshold."
)

# Colors and layout for dark theme
layout = dict(
    plot_bgcolor='black',
    paper_bgcolor='black',
    font=dict(color='white'),
    hovermode='x unified',
    margin=dict(l=40, r=40, t=60, b=40)
)

# First: Overall monthly views line chart
fig_overall = go.Figure()

fig_overall.add_trace(go.Scatter(
    x=monthly_views['Month'],
    y=monthly_views['Views'],
    mode='lines+markers',
    name='Monthly Views',
    line=dict(color='blue'),
    hovertemplate='%{x|%b %Y}<br>Views: %{y:,}<extra></extra>'
))

fig_overall.update_layout(title="Monthly Views (Overall)", **layout)
st.plotly_chart(fig_overall, use_container_width=True)

# Second: Highlighted spikes graph
fig_spikes = go.Figure()

fig_spikes.add_trace(go.Scatter(
    x=monthly_views['Month'],
    y=monthly_views['Views'],
    mode='lines',
    line=dict(color='blue'),
    name='Monthly Views',
    hovertemplate='%{x|%b %Y}<br>Views: %{y:,}<extra></extra>'
))

# Add red spike markers
fig_spikes.add_trace(go.Scatter(
    x=spike_months['Month'],
    y=spike_months['Views'],
    mode='markers',
    name='Spikes',
    marker=dict(color='red', size=10, symbol='circle'),
    hovertemplate='%{x|%b %Y}<br>Views: %{y:,}<extra></extra>'
))

fig_spikes.update_layout(
    title=f"Monthly Views with Spikes (> {spike_threshold}%)", **layout)

st.plotly_chart(fig_spikes, use_container_width=True)

# Dropdown for selecting spike month
if not spike_months.empty:
    spike_month_strs = spike_months['Month'].dt.strftime('%B %Y').tolist()
    selected_spike_str = st.selectbox(
        "Select a Spike Month to View Videos", spike_month_strs)
    selected_spike_month = pd.to_datetime(selected_spike_str)

    # Filter videos for the selected spike month
    videos_in_spike = df[df['Month'] == selected_spike_month]

    st.markdown(f"### 🎥 Videos posted in {selected_spike_str} (Spike Month)")

    if not videos_in_spike.empty:
        for _, row in videos_in_spike.iterrows():
            video_url = f"https://www.youtube.com/watch?v={row['Video ID']}"
            thumb_url = f"https://img.youtube.com/vi/{row['Video ID']}/0.jpg"
            st.markdown(
                f"**{row['Title']}**  \n"
                f"[![Thumbnail]({thumb_url})]({video_url})  \n"
                f"Views: {row['Views']:,} | Likes: {row['Likes']:,} | Comments: {row['Comments']:,}"
            )
            st.markdown("---")
    else:
        st.write("No videos found for this month.")
else:
    st.write(f"No spike months found above the {spike_threshold}% threshold.")
