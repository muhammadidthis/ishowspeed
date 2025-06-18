# Enhanced version with interactive and visually appealing charts using Plotly

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import seaborn as sns

# Set up the page
st.set_page_config(page_title="Facebook Reels Trend Analysis", layout="wide")
st.title("iShowSpeed Facebook Reels Trend Analysis")

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("iShowSpeed_Facebook_Reels.csv")
    df['date'] = pd.to_datetime(df['timestamp'], unit='s')
    df['year_month'] = df['date'].dt.to_period('M').astype(str)
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month_name()
    df['day_of_week'] = df['date'].dt.day_name()

    df['engagement_rate'] = (df['reactions_count'] + df['comments_count'] + df['reshare_count']) / df['play_count']
    df['reactions_per_play'] = df['reactions_count'] / df['play_count']
    df['comments_per_play'] = df['comments_count'] / df['play_count']
    df['shares_per_play'] = df['reshare_count'] / df['play_count']
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
min_plays = st.sidebar.slider("Minimum Play Count", 
                             min_value=int(df['play_count'].min()), 
                             max_value=int(df['play_count'].max()),
                             value=int(df['play_count'].quantile(0.25)))

selected_years = st.sidebar.multiselect("Select Years", 
                                      options=sorted(df['year'].unique(), reverse=True),
                                      default=sorted(df['year'].unique(), reverse=True))

filtered_df = df[(df['play_count'] >= min_plays) & 
                (df['year'].isin(selected_years))]

# Overview metrics
st.header("Performance Overview")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Videos", len(filtered_df))
col2.metric("Avg Play Count", f"{filtered_df['play_count'].mean():,.0f}")
col3.metric("Avg Reactions", f"{filtered_df['reactions_count'].mean():,.0f}")
col4.metric("Avg Engagement", f"{filtered_df['engagement_rate'].mean()*100:.2f}%")

# Tabs for visual exploration
st.header("Trends Over Time")
tab1, tab2, tab3 = st.tabs(["Monthly Trends", "Weekday Patterns", "Video Length"])

with tab1:
    monthly_trend = filtered_df.groupby('year_month').agg({
        'play_count': 'mean',
        'reactions_count': 'mean',
        'comments_count': 'mean',
        'reshare_count': 'mean'
    }).reset_index()

    fig = px.line(monthly_trend, x='year_month', 
                  y=['play_count', 'reactions_count', 'comments_count', 'reshare_count'],
                  markers=True,
                  labels={"value": "Average Count", "year_month": "Month"},
                  title="Monthly Performance Trends")
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_trend = filtered_df.groupby('day_of_week').agg({
        'play_count': 'mean', 'engagement_rate': 'mean'
    }).reindex(weekday_order).reset_index()

    fig1 = px.bar(weekday_trend, x='day_of_week', y='play_count',
                 title='Avg Play Count by Day of Week', labels={'play_count': 'Avg Plays'},
                 color='play_count', color_continuous_scale='Blues')

    fig2 = px.bar(weekday_trend, x='day_of_week', y='engagement_rate',
                 title='Avg Engagement Rate by Day of Week', labels={'engagement_rate': 'Engagement Rate'},
                 color='engagement_rate', color_continuous_scale='Viridis')

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig1 = px.scatter(filtered_df, x='length_in_seconds', y='play_count',
                     title='Video Length vs Play Count',
                     labels={'length_in_seconds': 'Video Length (s)', 'play_count': 'Play Count'},
                     color='play_count', color_continuous_scale='Blues')

    fig2 = px.scatter(filtered_df, x='length_in_seconds', y='engagement_rate',
                     title='Video Length vs Engagement Rate',
                     labels={'length_in_seconds': 'Video Length (s)', 'engagement_rate': 'Engagement Rate'},
                     color='engagement_rate', color_continuous_scale='Teal')

    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

import plotly.express as px

# Top performing content
st.header("🌟 Top Performing Content")
top_n = st.slider("Select Number of Top Videos to Show", 5, 20, 10)

tab4, tab5, tab6 = st.tabs(["🎬 Most Viewed", "🔥 Most Engaging", "🔁 Most Shared"])

# ---------- Tab 4: Most Viewed ----------
with tab4:
    st.subheader(f"Top {top_n} Videos by Play Count")
    top_plays = filtered_df.nlargest(top_n, 'play_count')

    fig = px.bar(
        top_plays,
        x='play_count',
        y='description',
        orientation='h',
        title="Most Viewed Videos",
        hover_data=['date', 'reactions_count', 'comments_count', 'reshare_count'],
        labels={'play_count': 'Play Count', 'description': 'Video Description'},
        color='play_count',
        height=500
    )
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 5: Most Engaging ----------
with tab5:
    st.subheader(f"Top {top_n} Videos by Engagement Rate")
    top_engagement = filtered_df.nlargest(top_n, 'engagement_rate')

    fig = px.bar(
        top_engagement,
        x='engagement_rate',
        y='description',
        orientation='h',
        title="Most Engaging Videos",
        hover_data=['date', 'play_count', 'reactions_count', 'comments_count', 'reshare_count'],
        labels={'engagement_rate': 'Engagement Rate', 'description': 'Video Description'},
        color='engagement_rate',
        height=500
    )
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 6: Most Shared ----------
with tab6:
    st.subheader(f"Top {top_n} Videos by Share Count")
    top_shares = filtered_df.nlargest(top_n, 'reshare_count')

    fig = px.bar(
        top_shares,
        x='reshare_count',
        y='description',
        orientation='h',
        title="Most Shared Videos",
        hover_data=['date', 'play_count', 'reactions_count', 'comments_count'],
        labels={'reshare_count': 'Share Count', 'description': 'Video Description'},
        color='reshare_count',
        height=500
    )
    fig.update_layout(yaxis=dict(categoryorder='total ascending'))
    st.plotly_chart(fig, use_container_width=True)

fig = px.scatter(filtered_df, 
                 x='play_count', 
                 y='engagement_rate', 
                 size='reshare_count', 
                 color='reactions_count', 
                 hover_name='description',
                 title="Bubble Chart: Views vs Engagement vs Shares",
                 size_max=60)
st.plotly_chart(fig, use_container_width=True)


df['hour'] = df['date'].dt.hour
heatmap_data = df.pivot_table(index='day_of_week', columns='hour', values='play_count', aggfunc='mean')
sns.heatmap(heatmap_data, cmap='Blues')

df['virality'] = (df['reshare_count'] + df['comments_count']) / df['play_count']

# Content search
st.header("Content Keyword Analysis")
search_term = st.text_input("Search video descriptions for keyword")

if search_term:
    matched = filtered_df[filtered_df['description'].str.contains(search_term, case=False, na=False)]
    if not matched.empty:
        st.dataframe(matched[['description', 'date', 'play_count', 'reactions_count', 'comments_count', 'reshare_count']], use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Avg Play Count", f"{matched['play_count'].mean():,.0f}",
                      f"{(matched['play_count'].mean() - filtered_df['play_count'].mean())/filtered_df['play_count'].mean()*100:.1f}% vs avg")
        with col2:
            st.metric("Avg Engagement", f"{matched['engagement_rate'].mean()*100:.2f}%",
                      f"{(matched['engagement_rate'].mean() - filtered_df['engagement_rate'].mean())/filtered_df['engagement_rate'].mean()*100:.1f}% vs avg")
    else:
        st.warning(f"No videos found containing '{search_term}'")
