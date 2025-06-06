import streamlit as st
import pandas as pd
import plotly.express as px

# Load and preprocess data once, cache for speed
@st.cache_data
def load_data():
    df = pd.read_csv("iShowSpeed_comments_sentiment.csv")
    df['comment_date'] = pd.to_datetime(df['comment_date'], errors='coerce')
    return df

df = load_data()

st.title("YouTube Comments Dashboard")

# --- Video selector & embed ---
video_ids = df['video_id'].unique()
selected_video_id = st.selectbox("Select Video to View", video_ids)

# Show video embed (YouTube embed)
st.video(f"https://www.youtube.com/watch?v={selected_video_id}")

# Filter data for selected video
df_video = df[df['video_id'] == selected_video_id]

# --- Filters ---
# Sentiment filter
sentiment_options = ['All'] + sorted(df_video['sentiment'].dropna().unique().tolist())
selected_sentiment = st.selectbox("Filter by Sentiment", sentiment_options)

# Date filter
min_date = df_video['comment_date'].min()
max_date = df_video['comment_date'].max()
start_date, end_date = st.date_input("Filter by Date Range", value=(min_date.date(), max_date.date()), 
                                     min_value=min_date.date(), max_value=max_date.date())

# Apply sentiment filter
if selected_sentiment != 'All':
    df_filtered = df_video[df_video['sentiment'] == selected_sentiment]
else:
    df_filtered = df_video.copy()

# Apply date filter
df_filtered = df_filtered[
    (df_filtered['comment_date'].dt.date >= start_date) & 
    (df_filtered['comment_date'].dt.date <= end_date)
]

# --- Search comments ---
search_text = st.text_input("Search comments")
search_button = st.button("Search")

if search_button and search_text.strip():
    df_filtered = df_filtered[df_filtered['comment_text'].str.contains(search_text, case=False, na=False)]

st.markdown(f"### Showing {len(df_filtered)} comments after filters")

# --- Plots ---
col1, col2 = st.columns(2)

with col1:
    # Pie chart for sentiment distribution (filtered & selected video)
    sentiment_counts = df_filtered['sentiment'].value_counts().reset_index()
    sentiment_counts.columns = ['Sentiment', 'Count']
    if not sentiment_counts.empty:
        fig_pie = px.pie(sentiment_counts, values='Count', names='Sentiment', title="Sentiment Distribution")
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.write("No sentiment data to display.")

with col2:
    # Bar chart likes per sentiment
    likes_per_sentiment = df_filtered.groupby('sentiment')['comment_likes'].sum().reset_index()
    if not likes_per_sentiment.empty:
        fig_bar = px.bar(likes_per_sentiment, x='sentiment', y='comment_likes', 
                         title="Total Likes per Sentiment", labels={'comment_likes': 'Total Likes', 'sentiment': 'Sentiment'})
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.write("No likes data to display.")

# Line chart comments over time
comments_over_time = df_filtered.groupby(df_filtered['comment_date'].dt.date).size().reset_index(name='count')
if not comments_over_time.empty:
    fig_line = px.line(comments_over_time, x='comment_date', y='count', title="Comments Over Time", labels={'comment_date': 'Date', 'count': 'Number of Comments'})
    st.plotly_chart(fig_line, use_container_width=True)
else:
    st.write("No comment data to display over time.")

# --- Show comments (limit to first 50 for performance) ---
st.markdown("### Comments:")

if len(df_filtered) == 0:
    st.write("No comments match your filters/search.")
else:
    for idx, row in df_filtered.head(50).iterrows():
        st.markdown(f"**{row['author_name']}** ({row['comment_date'].strftime('%Y-%m-%d')}):")
        st.write(row['comment_text'])
        st.markdown(f"👍 Likes: {row['comment_likes']} | Replies: {row['reply_count']} | Sentiment: {row['sentiment']}")
        st.markdown("---")
