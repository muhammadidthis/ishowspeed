import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from utils import load_posts

st.title("📈 Content Analysis A")

df = load_posts()
df['created_utc'] = pd.to_datetime(df['created_utc'])

st.subheader("Monthly Post Volume")
df['month'] = df['created_utc'].dt.to_period('M')
monthly_counts = df.groupby('month').size()

fig, ax = plt.subplots()
monthly_counts.plot(kind='bar', ax=ax)
plt.xticks(rotation=45)
st.pyplot(fig)

st.subheader("Top 10 Most Upvoted Posts")
top_upvoted = df.sort_values('score', ascending=False).head(10)
st.table(top_upvoted[['title', 'score', 'num_comments', 'created_utc']])
