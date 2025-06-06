import streamlit as st
import pandas as pd
from utils import load_posts

st.title("🎮 Content Analysis B")

df = load_posts()

# Simple keyword-based categorization
def categorize_post(title):
    title = title.lower()
    if any(word in title for word in ['fortnite', 'fifa', 'roblox', 'game']):
        return 'Gaming'
    elif any(word in title for word in ['irl', 'live', 'stream']):
        return 'IRL'
    elif any(word in title for word in ['meme', 'funny', 'joke']):
        return 'Memes'
    elif any(word in title for word in ['music', 'song', 'rap']):
        return 'Music'
    else:
        return 'Other'

df['category'] = df['title'].apply(categorize_post)

st.subheader("Content Categories Distribution")
st.bar_chart(df['category'].value_counts())

st.subheader("Top Posts by Category")
selected_cat = st.selectbox("Choose category", df['category'].unique())
filtered = df[df['category'] == selected_cat].sort_values('score', ascending=False).head(5)
st.table(filtered[['title', 'score', 'num_comments', 'created_utc']])
