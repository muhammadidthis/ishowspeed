import streamlit as st
from utils import load_posts, load_comments

st.title("📊 Data Collection")

st.markdown("""
This page shows the raw Reddit post and comment data related to **IShowSpeed**, collected using the Reddit API (PRAW).
""")

st.subheader("Posts Dataset")
posts_df = load_posts()
st.dataframe(posts_df.head(20))

st.subheader("Comments Dataset")
comments_df = load_comments()
st.dataframe(comments_df.head(20))

st.success(f"✅ Loaded {len(posts_df)} posts and {len(comments_df)} comments.")
