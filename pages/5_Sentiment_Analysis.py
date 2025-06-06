import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from utils import fetch_and_analyze_sentiment

st.title("Sentiment Analysis on IShowSpeed Reddit Comments")

# Run sentiment analysis if CSV not found or by button
if 'df_sentiment' not in st.session_state:
    with st.spinner("Fetching and analyzing comments..."):
        df = fetch_and_analyze_sentiment(
            client_id='4hd7cUPwUfo3cfdrYD47Hg',
            client_secret='hh1DSeiYJeQlRWkSKUq-gZSXhIs0mg',
            user_agent='windows:iShowpeed:v1.0 (by u/rubytheambivert)'
        )
        df.to_csv('ishowspeed_comments_sentiment.csv', index=False)
        st.session_state.df_sentiment = df
else:
    df = st.session_state.df_sentiment

st.subheader("Sentiment Distribution")
sent_counts = df['sentiment_label'].value_counts()
st.bar_chart(sent_counts)

st.subheader("Sentiment Over Time")
df['date'] = df['timestamp'].dt.date
time_sentiment = df.groupby(['date', 'sentiment_label']).size().unstack().fillna(0)
st.line_chart(time_sentiment)

st.subheader("Word Cloud of Comments")
text = " ".join(df['comment_text'].dropna().tolist())
wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text)
st.image(wordcloud.to_array(), use_column_width=True)

st.subheader("Sample Comments")
st.dataframe(df[['comment_text', 'sentiment_score', 'sentiment_label']].sample(10))
