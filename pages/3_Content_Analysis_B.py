import streamlit as st
import pandas as pd
import plotly.express as px
from utils import load_posts

st.set_page_config(layout="wide", page_title="Content Analysis B", page_icon="🎮")
st.title("🎮 Content Categorization & Insights")

# Load data
df = load_posts()
df['created_utc'] = pd.to_datetime(df['created_utc'])

# Improved keyword-based categorization
def categorize_post(title):
    title = title.lower()
    if any(kw in title for kw in ['fortnite', 'fifa', 'roblox', 'minecraft', 'cod', 'gaming', 'gameplay']):
        return 'Gaming'
    elif any(kw in title for kw in ['irl', 'live', 'stream', 'reaction']):
        return 'IRL'
    elif any(kw in title for kw in ['meme', 'funny', 'joke', 'humor', 'skit']):
        return 'Memes'
    elif any(kw in title for kw in ['music', 'song', 'rap', 'freestyle', 'track']):
        return 'Music'
    else:
        return 'Other'

df['Category'] = df['title'].apply(categorize_post)

# === Category Distribution Bar Chart ===
st.subheader("📊 Content Category Distribution")
category_counts = df['Category'].value_counts().reset_index()
category_counts.columns = ['Category', 'Count']

fig_cat = px.bar(
    category_counts,
    x='Category',
    y='Count',
    color='Category',
    title='Number of Posts per Category',
    template='plotly_dark'
)
st.plotly_chart(fig_cat, use_container_width=True)

# === Top Posts by Selected Category ===
st.subheader("🏆 Top Posts by Category")
categories = sorted(df['Category'].unique())
selected_cat = st.selectbox("Select a Category", categories)

top_posts = (
    df[df['Category'] == selected_cat]
    .sort_values('score', ascending=False)
    .head(5)
)

if top_posts.empty:
    st.warning("No posts found in this category.")
else:
    for _, row in top_posts.iterrows():
        with st.expander(f"📌 {row['title'][:80]}..."):
            st.markdown(f"**Score:** {row['score']:,} | 💬 **Comments:** {row['num_comments']:,}")
            st.markdown(f"📅 **Posted:** {row['created_utc'].strftime('%B %d, %Y %H:%M')}")
            st.markdown("---")

# === Summary Statistics ===
st.subheader("📍 Category-Wise Metrics Snapshot")
category_summary = df.groupby('Category').agg({
    'title': 'count',
    'score': 'mean',
    'num_comments': 'mean'
}).reset_index().rename(columns={'title': 'Total Posts', 'score': 'Avg Score', 'num_comments': 'Avg Comments'})

st.dataframe(category_summary.style.format({
    'Avg Score': '{:.1f}',
    'Avg Comments': '{:.1f}',
    'Total Posts': '{:,}'
}), use_container_width=True)
