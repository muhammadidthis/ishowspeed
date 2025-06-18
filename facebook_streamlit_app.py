import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
import plotly.express as px
import nltk
from nltk.corpus import stopwords
from textblob import TextBlob
from wordcloud import WordCloud

# First-time setup
nltk.download('stopwords')

# Streamlit settings
st.set_page_config(page_title="📘 Facebook Comments Analysis", layout="wide")
st.title("📘 Facebook Comments Dashboard")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("iShowSpeed_Facebook_comments_sentiment.csv")  # Adjust path if needed
    df["created_time"] = pd.to_datetime(df["created_time"])
    df["message"] = df["message"].fillna("")
    return df

df = load_data()

# Sentiment Analysis
@st.cache_data
def analyze_sentiment(text):
    return TextBlob(text).sentiment.polarity

st.sidebar.markdown("### Filter by Date")
start_date = st.sidebar.date_input("Start Date", value=df["created_time"].min().date())
end_date = st.sidebar.date_input("End Date", value=df["created_time"].max().date())
filtered_df = df[(df["created_time"].dt.date >= start_date) & (df["created_time"].dt.date <= end_date)]

# Add sentiment score
with st.spinner("Analyzing sentiments..."):
    filtered_df["sentiment_score"] = filtered_df["message"].apply(analyze_sentiment)
    filtered_df["sentiment_label"] = filtered_df["sentiment_score"].apply(
        lambda x: "positive" if x > 0 else "negative" if x < 0 else "neutral"
    )

# Activity over time
st.subheader("📈 Comments Activity Over Time")
activity_df = filtered_df.groupby(filtered_df["created_time"].dt.date).size()
st.line_chart(activity_df)

# Top reacted comments
st.subheader("🔥 Most Reacted Comments")
top_reacted = filtered_df.sort_values(by="reactions_count", ascending=False).head(5)
for _, row in top_reacted.iterrows():
    st.markdown(f"**{row['author_name']}** ({row['reactions_count']} reactions):")
    st.write(f"💬 {row['message']}")
    st.markdown("---")

# Most common words
st.subheader("🔠 Most Common Words (Excluding Stopwords)")
stop_words = set(stopwords.words("english"))
all_words = []

for message in filtered_df["message"]:
    words = str(message).lower().split()
    clean = [word for word in words if word.isalpha() and word not in stop_words]
    all_words.extend(clean)

common_words = Counter(all_words).most_common(15)
common_df = pd.DataFrame(common_words, columns=["Word", "Count"])
st.bar_chart(common_df.set_index("Word"))

st.subheader("📊 Sentiment Distribution")

sentiment_count = filtered_df["sentiment_label"].value_counts().reset_index()
sentiment_count.columns = ["Sentiment", "Count"]

fig = px.bar(
    sentiment_count,
    x="Sentiment",
    y="Count",
    color="Sentiment",
    color_discrete_map={
        "positive": "#00cc96",
        "neutral": "#636efa",
        "negative": "#ef553b"
    },
    title="Sentiment Breakdown of Facebook Comments",
    text="Count",
)

fig.update_traces(textposition='outside')
fig.update_layout(
    xaxis_title="Sentiment",
    yaxis_title="Number of Comments",
    font=dict(size=14),
    showlegend=False
)

st.plotly_chart(fig, use_container_width=True)

# 📉 Sentiment Over Time
st.subheader("📉 Sentiment Over Time")

# Group by date and sentiment
sentiment_overtime = filtered_df.groupby([
    filtered_df["created_time"].dt.date,
    "sentiment_label"
]).size().reset_index(name="count")

# Sort the data
sentiment_overtime = sentiment_overtime.sort_values(by="created_time")

# Plotly line chart
fig = px.line(
    sentiment_overtime,
    x="created_time",
    y="count",
    color="sentiment_label",
    markers=True,
    title="Sentiment Trend Over Time",
    color_discrete_map={
        "positive": "#00cc96",
        "neutral": "#636efa",
        "negative": "#ef553b"
    },
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Number of Comments",
    font=dict(size=14)
)

st.plotly_chart(fig, use_container_width=True)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def get_diverse_examples(df_sentiment, n=5):
    """
    Get n diverse examples from the sentiment dataframe
    using TF-IDF + cosine similarity.
    """
    df_sentiment = df_sentiment.drop_duplicates(subset=["message"])
    texts = df_sentiment["message"].tolist()

    if len(texts) <= n:
        return texts

    tfidf = TfidfVectorizer(stop_words="english").fit_transform(texts)
    sim_matrix = cosine_similarity(tfidf)
    selected = [0]  # Start with the first one

    for _ in range(1, n):
        # Get the most dissimilar next one
        remaining = list(set(range(len(texts))) - set(selected))
        dissimilarities = [sim_matrix[i][selected].mean() for i in remaining]
        next_idx = remaining[dissimilarities.index(min(dissimilarities))]
        selected.append(next_idx)

    return [texts[i] for i in selected]

# positive comments
st.subheader("💚 Positive Comments")
positive_df = filtered_df[filtered_df["sentiment_label"] == "positive"]
positive_examples = get_diverse_examples(positive_df, n=5)
for msg in positive_examples:
    st.success(f"💬 {msg}")

# negative comments
st.subheader("💔 Negative Comments")
negative_df = filtered_df[filtered_df["sentiment_label"] == "negative"]
negative_examples = get_diverse_examples(negative_df, n=5)
for msg in negative_examples:
    st.error(f"💬 {msg}")

# Show data
with st.expander("📄 View Raw Facebook Comments"):
    st.dataframe(filtered_df)