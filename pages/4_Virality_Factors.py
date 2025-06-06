import streamlit as st
import pandas as pd
from utils import load_posts

st.title("🔥 Virality Factors")

df = load_posts()

st.markdown("""
These are example posts that went viral due to:
- Funny/unexpected moments
- High audience engagement
- Controversial or trending topics
""")

top_posts = df.sort_values(['score', 'num_comments'], ascending=False).head(3)

for i, row in top_posts.iterrows():
    st.markdown(f"### {row['title']}")
    st.write(f"**Score:** {row['score']} | **Comments:** {row['num_comments']}")
    st.write(f"[View Post]({row['url']})")
    st.markdown("---")
