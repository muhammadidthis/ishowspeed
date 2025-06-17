import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import plotly.express as px
import plotly.graph_objects as go
from utils import fetch_and_analyze_sentiment

st.set_page_config(page_title="Sentiment Analysis", layout="wide", page_icon="💬")
st.title("💬 Sentiment Analysis on IShowSpeed Reddit Comments")

# Load or fetch sentiment data
if 'df_sentiment' not in st.session_state:
    with st.spinner("🔍 Fetching and analyzing comments..."):
        df = fetch_and_analyze_sentiment(
            client_id='4hd7cUPwUfo3cfdrYD47Hg',
            client_secret='hh1DSeiYJeQlRWkSKUq-gZSXhIs0mg',
            user_agent='windows:iShowpeed:v1.0 (by u/rubytheambivert)'
        )
        df.to_csv('ishowspeed_comments_sentiment.csv', index=False)
        st.session_state.df_sentiment = df
else:
    df = st.session_state.df_sentiment

# Ensure datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['date'] = df['timestamp'].dt.date

# --- Layout for charts ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Sentiment Distribution (Pie Chart)")
    sent_counts = df['sentiment_label'].value_counts().reset_index()
    sent_counts.columns = ['Sentiment', 'Count']

    fig_pie = px.pie(
        sent_counts,
        values='Count',
        names='Sentiment',
        title='Comment Sentiment Breakdown',
        color='Sentiment',
        color_discrete_map={'positive': 'lightgreen', 'neutral': 'lightblue', 'negative': 'red'}
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("📈 Sentiment Trend Over Time")
    time_sentiment = df.groupby(['date', 'sentiment_label']).size().unstack().fillna(0)
    fig_line = px.line(
        time_sentiment,
        x=time_sentiment.index,
        y=['positive', 'neutral', 'negative'],
        title='Daily Sentiment Counts',
        labels={'value': 'Count', 'date': 'Date'},
        template='plotly_dark'
    )
    st.plotly_chart(fig_line, use_container_width=True)

# --- Word Cloud ---
st.subheader("☁️ Word Cloud of All Comments")
text = " ".join(df['comment_text'].dropna().tolist())
wordcloud = WordCloud(
    width=1000,
    height=400,
    background_color='black',
    colormap='rainbow',
    max_words=200
).generate(text)
st.image(wordcloud.to_array(), use_column_width=True)

st.markdown("## 🔥 Weekly Sentiment Heatmap (Normalized)")
st.caption("This heatmap shows how sentiment distribution varies across weekdays and posting time.")

df['weekday'] = df['timestamp'].dt.day_name()
df['hour'] = df['timestamp'].dt.hour

# Normalize sentiment counts by total per weekday
pivot_counts = df.groupby(['weekday', 'sentiment_label']).size().unstack(fill_value=0)
pivot_norm = pivot_counts.div(pivot_counts.sum(axis=1), axis=0)
weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
pivot_norm = pivot_norm.reindex(weekday_order)

# Plotly heatmap
fig_heat = go.Figure(data=go.Heatmap(
    z=pivot_norm.T.values,
    x=pivot_norm.index,
    y=pivot_norm.columns,
    colorscale='RdBu',
    colorbar=dict(title="Proportion"),
    hoverongaps=False
))

fig_heat.update_layout(
    title="Normalized Sentiment Distribution by Weekday",
    xaxis_title="Weekday",
    yaxis_title="Sentiment",
    height=400,
    margin=dict(l=60, r=40, t=60, b=60)
)
st.plotly_chart(fig_heat, use_container_width=True)

# Optional: Summary stats
st.subheader("📌 Summary Statistics")
col_pos, col_neu, col_neg = st.columns(3)
col_pos.metric("😊 Positive Comments", int(sent_counts[sent_counts['Sentiment'] == 'positive']['Count']))
col_neu.metric("😐 Neutral Comments", int(sent_counts[sent_counts['Sentiment'] == 'neutral']['Count']))
col_neg.metric("😠 Negative Comments", int(sent_counts[sent_counts['Sentiment'] == 'negative']['Count']))
