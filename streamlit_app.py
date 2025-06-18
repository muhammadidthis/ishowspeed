import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import plotly.express as px
import nltk
from nltk.corpus import stopwords
from collections import Counter
import string
import plotly.express as px
import pandas as pd

# --- PAGE CONFIG ---
st.set_page_config(layout="wide", page_title="YouTube Comment Sentiment Dashboard")
st.markdown("<h1 style='text-align: center;'>📊 YouTube Comment Sentiment Analysis</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- LOAD DATA ---
df = pd.read_csv("iShowSpeed_comments_sentiment.csv")
df = df.dropna(subset=["comment_text"])
df["comment_text"] = df["comment_text"].astype(str)

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters")
sentiment_filter = st.sidebar.multiselect(
    "Select Sentiment",
    options=sorted(df["sentiment"].unique()),
    default=sorted(df["sentiment"].unique())
)

video_filter = st.sidebar.multiselect(
    "Select Video ID",
    options=sorted(df["video_id"].unique()),
    default=sorted(df["video_id"].unique())
)

sentiment_wc = st.sidebar.selectbox(
    "Word Cloud Sentiment",
    ["All"] + list(df["sentiment"].unique())
)

# --- FILTERED DATA ---
filtered_df = df[
    (df["sentiment"].isin(sentiment_filter)) &
    (df["video_id"].isin(video_filter))
]

# --- KPI SECTION ---
st.markdown("### 🔢 Summary Statistics")
kpi1, kpi2, kpi3 = st.columns(3)
kpi1.metric(label="💬 Total Comments", value=len(filtered_df))
kpi2.metric(label="📹 Unique Videos", value=filtered_df["video_id"].nunique())
kpi3.metric(label="🧠 Sentiment Classes", value=filtered_df["sentiment"].nunique())

st.markdown("---")

# --- WORD CLOUD ---
st.markdown("### ☁️ Word Cloud")

wc_text = " ".join(
    filtered_df["comment_text"]
) if sentiment_wc == "All" else " ".join(
    filtered_df[filtered_df["sentiment"] == sentiment_wc]["comment_text"]
)

# Ensure all items are strings
wc_text = " ".join([str(word) for word in wc_text.split()])

# Create WordCloud
wordcloud = WordCloud(width=900, height=400, background_color="white", colormap="viridis").generate(wc_text)
fig_wc, ax_wc = plt.subplots(figsize=(12, 6))
ax_wc.imshow(wordcloud, interpolation="bilinear")
ax_wc.axis("off")
st.pyplot(fig_wc)

st.markdown("---")


# --- SENTIMENT OVER TIME ---
st.markdown("### ⏳ Sentiment Over Time")

# Ensure comment_date is datetime
filtered_df["comment_date"] = pd.to_datetime(filtered_df["comment_date"], errors='coerce')

# Drop NaT dates (if any)
filtered_df = filtered_df.dropna(subset=["comment_date"])

# Group by date and sentiment
sentiment_time = (
    filtered_df.groupby([filtered_df["comment_date"].dt.date, "sentiment"])
    .size()
    .reset_index(name="count")
)

# Pivot for plotting
sentiment_time_pivot = sentiment_time.pivot(index="comment_date", columns="sentiment", values="count").fillna(0)

# Plotting
st.line_chart(sentiment_time_pivot)

# --- SENTIMENT DISTRIBUTION PIE ---
st.markdown("### 🥧 Sentiment Distribution")
sentiment_counts = filtered_df["sentiment"].value_counts().reset_index()
sentiment_counts.columns = ['Sentiment', 'Count']
fig_pie = px.pie(sentiment_counts, names='Sentiment', values='Count',
                 color_discrete_sequence=px.colors.qualitative.Set3,
                 title="Distribution of Sentiment")
st.plotly_chart(fig_pie, use_container_width=True)

# --- SENTIMENT PER VIDEO ID BAR ---
st.markdown("### 📊 Sentiment per Video ID")
fig_bar = px.histogram(filtered_df, x="video_id", color="sentiment", barmode="group",
                       title="Sentiment Counts by Video ID", text_auto=True,
                       color_discrete_sequence=px.colors.qualitative.Set2)
fig_bar.update_layout(xaxis_title="Video ID", yaxis_title="Number of Comments")
st.plotly_chart(fig_bar, use_container_width=True)

top_commenters = filtered_df['author_name'].value_counts().head(10)
st.bar_chart(top_commenters)

st.markdown("### 🔥 Most Liked Comments")
top_liked = filtered_df.sort_values(by='comment_likes', ascending=False).head(5)
for idx, row in top_liked.iterrows():
    st.markdown(f"**{row['author_name']}** ({row['comment_likes']} 👍): {row['comment_text']}")

# Heat Map
# Preprocess time-based fields
filtered_df["day"] = filtered_df["comment_date"].dt.day_name()
filtered_df["hour"] = filtered_df["comment_date"].dt.hour

# Ensure consistent day order
day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
filtered_df["day"] = pd.Categorical(filtered_df["day"], categories=day_order, ordered=True)

# Group by day and hour
heatmap_data = (
    filtered_df.groupby(["day", "hour"])
    .size()
    .reset_index(name="comment_count")
)

# Plot using Plotly
fig = px.density_heatmap(
    heatmap_data,
    x="hour",
    y="day",
    z="comment_count",
    color_continuous_scale="Viridis",
    nbinsx=24,
    title="📊 Comment Activity Heatmap",
    labels={"comment_count": "Number of Comments", "hour": "Hour of Day", "day": "Day of Week"},
)

fig.update_layout(
    xaxis_nticks=24,
    height=500,
    margin=dict(t=40, l=10, r=10, b=40),
    coloraxis_colorbar=dict(title="Comment Count"),
)

st.plotly_chart(fig, use_container_width=True)

nltk.download("stopwords")
stop_words = set(stopwords.words("english"))

def get_top_words(df, sentiment_label, top_n=10):
    comments = df[df['sentiment'] == sentiment_label]["comment_text"].dropna().str.lower()
    words = []

    for comment in comments:
        tokens = comment.translate(str.maketrans('', '', string.punctuation)).split()
        words.extend([word for word in tokens if word not in stop_words and word.isalpha()])

    word_freq = Counter(words)
    return word_freq.most_common(top_n)

# Layout: Two columns
st.subheader("🔍 Most Common Words by Sentiment")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 😊 Positive Comments")
    top_pos_words = get_top_words(filtered_df, "Positive", 10)
    for word, freq in top_pos_words:
        st.markdown(f"- **{word}**: {freq} times")

with col2:
    st.markdown("### 😡 Negative Comments")
    top_neg_words = get_top_words(filtered_df, "Negative", 10)
    for word, freq in top_neg_words:
        st.markdown(f"- **{word}**: {freq} times")

# --- EMBED YOUTUBE VIDEOS ---
st.markdown("### 📺 Watch Selected YouTube Videos")

unique_videos = filtered_df["video_id"].unique()
if len(unique_videos) == 0:
    st.info("No videos to show based on current filters.")
else:
    video_cols = st.columns(2)
    for idx, vid in enumerate(unique_videos):
        video_url = f"https://www.youtube.com/watch?v={vid}"
        with video_cols[idx % 2]:
            st.video(video_url)


# --- COMMENT LIKES BY SENTIMENT ---
st.markdown("### ❤️ Average Comment Likes by Sentiment")
avg_likes = filtered_df.groupby("sentiment")["comment_likes"].mean().reset_index()
fig_likes = px.bar(avg_likes, x="sentiment", y="comment_likes",
                   color="sentiment", text_auto=".2f",
                   color_discrete_sequence=px.colors.qualitative.Pastel,
                   title="Average Comment Likes per Sentiment")
fig_likes.update_layout(xaxis_title="Sentiment", yaxis_title="Avg Likes")
st.plotly_chart(fig_likes, use_container_width=True)

# --- DATA TABLE ---
st.markdown("### 🧾 Filtered Comments Table")
with st.expander("🔎 View Data Table"):
    st.dataframe(
        filtered_df[["video_id", "author_name", "comment_date", "comment_likes", "sentiment", "comment_text"]]
        .sort_values(by="comment_likes", ascending=False)
        .reset_index(drop=True),
        use_container_width=True,
        height=400
    )
