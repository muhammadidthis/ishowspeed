import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter
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

# Show data
with st.expander("📄 View Raw Facebook Comments"):
    st.dataframe(filtered_df)

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

# Optional: Sentiment distribution
st.subheader("📊 Sentiment Distribution")
sentiment_count = filtered_df["sentiment_label"].value_counts()
fig, ax = plt.subplots()
sns.barplot(x=sentiment_count.index, y=sentiment_count.values, palette="Spectral", ax=ax)
ax.set_ylabel("Number of Comments")
st.pyplot(fig)
