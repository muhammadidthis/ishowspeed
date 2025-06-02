import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import os

# Must be the first Streamlit command
st.set_page_config(layout="wide")
st.title("🌍 Country-wise Content Analysis")

# --- Load dataset ---
csv_file_path = 'ishowspeed_yt_dataset_all.csv'


@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"CSV file '{file_path}' not found.")
        st.stop()
    df = pd.read_csv(file_path)
    df['Date Posted'] = pd.to_datetime(df['Date Posted'])
    df['Views'] = pd.to_numeric(df['Views'], errors='coerce').fillna(0)
    df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0)
    df['Comments'] = pd.to_numeric(df['Comments'], errors='coerce').fillna(0)
    return df


df = load_data(csv_file_path)
df = df[df['Country'] != 'Not Applicable']


# Total Views by Country (Bar Chart)
views_by_country = df.groupby('Country')['Views'].sum(
).sort_values(ascending=False).reset_index()

st.subheader("Total Views by Country")
fig1 = px.bar(
    views_by_country.head(10),  # top 10 countries
    x='Country',
    y='Views',
    title="Top 10 Countries by Total Views",
    labels={'Views': 'Total Views'},
    template='plotly_dark'
)
st.plotly_chart(fig1, use_container_width=True)

# Number of Videos per country
video_counts = df['Country'].value_counts().reset_index()
video_counts.columns = ['Country', 'Video Count']

st.subheader("Number of Videos by Country")
fig2 = px.bar(
    video_counts.head(10),
    x='Country',
    y='Video Count',
    title="Top 10 Countries by Number of Videos",
    template='plotly_dark'
)
st.plotly_chart(fig2, use_container_width=True)


country_views = df.groupby('Country')['Views'].sum().reset_index()

fig = px.choropleth(
    country_views,
    locations='Country',
    locationmode='country names',
    color='Views',
    color_continuous_scale=px.colors.sequential.Magma,
    title='Total Views by Country',
    labels={'Views': 'Total Views'},
    template='plotly_white'
)

fig.update_layout(
    geo=dict(showframe=True, showcoastlines=True),
    width=900,
    height=600
)



st.subheader("Total Views Heatmap (White Background)")
st.plotly_chart(fig, use_container_width=True)

# Top Performing Video per Country
top_videos = df.sort_values(
    'Views', ascending=False).drop_duplicates('Country')

st.subheader("Top Performing Video from Each Country")
for _, row in top_videos.iterrows():
    video_url = f"https://www.youtube.com/watch?v={row['Video ID']}"
    thumbnail_url = f"https://img.youtube.com/vi/{row['Video ID']}/hqdefault.jpg"
    st.markdown(f"""
    <div style="display: flex; align-items: center; margin-bottom: 1em; background-color: #262730; padding: 10px; border-radius: 8px;">
        <a href="{video_url}" target="_blank">
            <img src="{thumbnail_url}" style="width: 160px; height: 90px; object-fit: cover; border-radius: 8px; margin-right: 15px;">
        </a>
        <div>
            <a href="{video_url}" target="_blank" style="font-size: 18px; font-weight: bold; color: #ADD8E6;">{row['Title']}</a><br>
            <span style="font-size: 14px; color: #B0B0B0;">
                🌍 {row['Country']} | 👁️ {int(row['Views']):,} views | 👍 {int(row['Likes']):,} likes | 💬 {int(row['Comments']):,} comments
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
