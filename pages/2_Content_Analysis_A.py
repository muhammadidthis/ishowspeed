import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils import load_posts

st.set_page_config(layout="wide", page_title="Content Analysis A", page_icon="📈")
st.title("📈 Reddit Post Trends & Insights")

# Load and preprocess
df = load_posts()
df['created_utc'] = pd.to_datetime(df['created_utc'])
df['month'] = df['created_utc'].dt.to_period('M').dt.to_timestamp()



# === Monthly Average Score & Comments ===
st.subheader("📈 Average Post Upvotes and Comments Over Time")
monthly_stats = df.groupby('month').agg({'score': 'mean', 'num_comments': 'mean'}).reset_index()

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(
    x=monthly_stats['month'], y=monthly_stats['score'],
    mode='lines+markers', name='Avg Upvotes', line=dict(color='skyblue')
))
fig_line.add_trace(go.Scatter(
    x=monthly_stats['month'], y=monthly_stats['num_comments'],
    mode='lines+markers', name='Avg Comments', line=dict(color='orange')
))
fig_line.update_layout(
    title="Monthly Avg Upvotes vs Comments",
    xaxis_title="Month",
    yaxis_title="Average Value",
    template="plotly_dark"
)
st.plotly_chart(fig_line, use_container_width=True)

# === Top 10 Upvoted Posts ===
st.subheader("🏆 Top 10 Most Upvoted Posts")
top_upvoted = df.sort_values('score', ascending=False).head(10)

for _, row in top_upvoted.iterrows():
    with st.expander(f"📌 {row['title'][:80]}..."):
        st.markdown(f"**Score:** {row['score']:,} | 💬 **Comments:** {row['num_comments']:,}")
        st.markdown(f"📅 **Posted:** {row['created_utc'].strftime('%B %d, %Y %H:%M')}")
        st.markdown("---")

# === Summary Metrics ===
st.subheader("📍 Key Metrics Snapshot")
total_posts = len(df)
avg_score = df['score'].mean()
avg_comments = df['num_comments'].mean()

col1, col2, col3 = st.columns(3)
col1.metric("Total Posts", f"{total_posts:,}")
col2.metric("Avg Score", f"{avg_score:.1f}")
col3.metric("Avg Comments", f"{avg_comments:.1f}")
