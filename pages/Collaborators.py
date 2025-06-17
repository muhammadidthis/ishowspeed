import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import os

st.set_page_config(layout="wide")

# Load dataset
csv_file_path = 'ishowspeed_yt_dataset_all.csv'


@st.cache_data
def load_data(file_path):
    if not os.path.exists(file_path):
        st.error(f"Error: CSV file '{file_path}' not found.")
        st.stop()
    try:
        df = pd.read_csv(file_path)
        df['Date Posted'] = pd.to_datetime(df['Date Posted'])
        df['Views'] = pd.to_numeric(df['Views'], errors='coerce').fillna(0)
        df['Likes'] = pd.to_numeric(df['Likes'], errors='coerce').fillna(0)
        df['Comments'] = pd.to_numeric(
            df['Comments'], errors='coerce').fillna(0)
        return df
    except Exception as e:
        st.error(f"An error occurred while loading the data: {e}")
        st.stop()


df = load_data(csv_file_path)


st.title("🤝 Views Trend: Collaborations vs Solo Content")

# ----- COLLABORATION VS SOLO ANALYSIS -----


def parse_collaborators(collab_str):
    try:
        collab_list = ast.literal_eval(collab_str)
        if isinstance(collab_list, list):
            clean_list = list(set([x.strip()
                              for x in collab_list if x.strip() != '']))
            return clean_list
        else:
            return []
    except:
        return []


df['Collaborators List'] = df['Collaborators'].apply(parse_collaborators)
df['Is Collaboration'] = df['Collaborators List'].apply(
    lambda x: 'Yes' if len(x) > 0 else 'No')

# Create Month column
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()

# Aggregate monthly views by collaboration status
monthly_views = df.groupby(['Month', 'Is Collaboration'])[
    'Views'].sum().reset_index()

# Plot Monthly Views Line Chart
fig = px.line(
    monthly_views,
    x='Month',
    y='Views',
    color='Is Collaboration',
    labels={
        'Views': 'Total Views',
        'Month': 'Month',
        'Is Collaboration': 'Collaboration Status'
    },
    title='Monthly View Trends: Collaborations vs Solo',
    template='plotly_dark'
)
st.plotly_chart(fig, use_container_width=True)

# Total video and view counts
counts = df['Is Collaboration'].value_counts().reindex(
    ['Yes', 'No'], fill_value=0)
views = df.groupby('Is Collaboration')['Views'].sum().reindex(
    ['Yes', 'No'], fill_value=0)

col1, col2 = st.columns(2)
col1.metric("Number of Collaboration Videos", counts['Yes'])
col2.metric("Number of Solo Videos", counts['No'])

col3, col4 = st.columns(2)
col3.metric("Total Views Collaboration Videos", f"{views['Yes']:,}")
col4.metric("Total Views Solo Videos", f"{views['No']:,}")

# ----- TOP COLLABORATORS ANALYSIS -----
exploded = df.explode('Collaborators List').reset_index(drop=True)
exploded = exploded[exploded['Collaborators List'].notna() & (
    exploded['Collaborators List'] != '')]

if not exploded.empty:
    collab_views = exploded.groupby('Collaborators List')[
        'Views'].sum().reset_index()
    top_collaborators = collab_views.sort_values(
        by='Views', ascending=False).head(10)

    st.subheader("Top 10 Collaborators by Total Views")
    fig = px.bar(
        top_collaborators,
        x='Collaborators List',
        y='Views',
        title="Top 10 Collaborators by Total Views",
        labels={'Collaborators List': 'Collaborator', 'Views': 'Total Views'},
        template='plotly_dark'
    )
    st.plotly_chart(fig, use_container_width=True)

    st.write("""
    The chart above shows which collaborators brought in the highest total views across all videos.
    """)

    all_collaborators = sorted(exploded['Collaborators List'].unique())
    selected_collaborator = st.selectbox(
        "Select a Collaborator", all_collaborators)

    collab_videos = exploded[exploded['Collaborators List'] ==
                             selected_collaborator].drop_duplicates(subset=['Video ID'])

    total_videos = collab_videos['Video ID'].nunique()
    total_views = collab_videos['Views'].sum()

    col5, col6 = st.columns(2)
    with col5:
        st.metric("Total Unique Videos", total_videos)
    with col6:
        st.metric("Total Views", f"{total_views:,.0f}")

    st.subheader(f"Videos featuring {selected_collaborator}")

    collab_videos_sorted = collab_videos.sort_values(
        by='Views', ascending=False)

    for _, video in collab_videos_sorted.iterrows():
        video_url = f"https://www.youtube.com/watch?v={video['Video ID']}"
        thumbnail_url = f"https://img.youtube.com/vi/{video['Video ID']}/hqdefault.jpg"
        st.markdown(f"""
        <div style="display: flex; align-items: center; margin-bottom: 1em; padding: 10px; border-radius: 8px; background-color: #262730;">
            <a href="{video_url}" target="_blank">
                <img src="{thumbnail_url}" alt="Thumbnail" style="width: 160px; height: 90px; object-fit: cover; border-radius: 8px; margin-right: 15px;">
            </a>
            <div>
                <a href="{video_url}" target="_blank" style="font-size: 18px; font-weight: bold; color: #ADD8E6; text-decoration: none;">{video['Title']}</a><br>
                <span style="font-size: 14px; color: #B0B0B0;">
                    👁️ {int(video['Views']):,} views | 👍 {int(video['Likes']):,} likes | 💬 {int(video['Comments']):,} comments
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No collaboration data found or processed.")
