import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
# --- Streamlit page setup ---
st.set_page_config(layout="wide")
st.title("🌍 Where Might IShowSpeed Go Next?")

# --- Load dataset ---
@st.cache_data
def load_data():
    df = pd.read_csv('ishowspeed_yt_dataset_all.csv', parse_dates=['Date Posted'])
    df['Views'] = pd.to_numeric(df['Views'], errors='coerce').fillna(0)
    df = df[df['Country'].notna()]
    df = df[df['Country'] != 'Not Applicable']
    return df

df = load_data()

# --- Filter data for the last 6 months ---
latest_date = df['Date Posted'].max()
six_months_ago = latest_date - pd.DateOffset(months=6)
recent_df = df[df['Date Posted'] >= six_months_ago]

# --- Group by month and country ---
recent_df['Month'] = recent_df['Date Posted'].dt.to_period('M').dt.to_timestamp()
monthly_views = recent_df.groupby(['Month', 'Country'])['Views'].sum().reset_index()

# --- Calculate average view growth per country ---
trend = monthly_views.pivot(index='Month', columns='Country', values='Views').fillna(0)
avg_growth = trend.diff().mean().sort_values(ascending=False).head(3).reset_index()
avg_growth.columns = ['Country', 'Average Monthly View Growth']

# --- Plot ---
fig = px.bar(
    avg_growth,
    x='Country',
    y='Average Monthly View Growth',
    title="Top 3 Fastest Growing Countries (Last 6 Months)",
    labels={'Average Monthly View Growth': 'Avg Monthly Increase in Views'},
    template='plotly_dark'
)

st.plotly_chart(fig, use_container_width=True)
st.title("🌍 Predicting IShowSpeed's Next Country – Score Analysis")

# --- Load Data ---
df = pd.read_csv("ishowspeed_yt_dataset_all.csv", parse_dates=["Date Posted"])

# Filter out unusable countries
df = df[df['Country'].notna()]
df = df[df['Country'] != 'Not Applicable']

# --- View Growth Score ---
st.subheader("📈 View Growth Score")
st.markdown("Measures how quickly viewership is growing in each country.")

# Group by Country and Month to calculate view growth
df['Month'] = df['Date Posted'].dt.to_period("M").dt.to_timestamp()
monthly_views = df.groupby(['Country', 'Month'])['Views'].sum().reset_index()
monthly_views['Previous Views'] = monthly_views.groupby('Country')[
    'Views'].shift(1)
monthly_views['Growth Rate'] = (
    (monthly_views['Views'] - monthly_views['Previous Views']) / monthly_views['Previous Views']) * 100
monthly_views = monthly_views.dropna()

# Average growth per country
view_growth_score = monthly_views.groupby(
    'Country')['Growth Rate'].mean().reset_index()
view_growth_score = view_growth_score.sort_values(
    by='Growth Rate', ascending=False).head(3)

fig_growth = px.bar(
    view_growth_score,
    x='Country',
    y='Growth Rate',
    title='Top 3 Countries by View Growth Rate',
    labels={'Growth Rate': 'Avg Monthly Growth (%)'},
    template='plotly_dark',
    color='Growth Rate'
)
st.plotly_chart(fig_growth, use_container_width=True)

# --- Engagement Score ---
st.subheader("🔥 Engagement Score")
st.markdown(
    "Calculated as the average of likes and comments per video per country.")

engagement = df.groupby('Country')[['Likes', 'Comments']].mean()
engagement['Engagement Score'] = (
    engagement['Likes'] + engagement['Comments']) / 2
engagement_score = engagement['Engagement Score'].reset_index(
).sort_values(by='Engagement Score', ascending=False).head(3)

fig_engagement = px.bar(
    engagement_score,
    x='Country',
    y='Engagement Score',
    title='Top 3 Countries by Engagement Score',
    labels={'Engagement Score': 'Avg (Likes + Comments) per Video'},
    template='plotly_dark',
    color='Engagement Score'
)
st.plotly_chart(fig_engagement, use_container_width=True)

# --- Frequency Score ---
st.subheader("📅 Upload Frequency Score")
st.markdown(
    "Measures how often videos are uploaded from each country (uploads per month).")

monthly_counts = df.groupby(['Country', 'Month'])[
    'Video ID'].count().reset_index()
monthly_avg = monthly_counts.groupby(
    'Country')['Video ID'].mean().reset_index()
monthly_avg.columns = ['Country', 'Frequency Score']
frequency_score = monthly_avg.sort_values(
    by='Frequency Score', ascending=False).head(3)

fig_frequency = px.bar(
    frequency_score,
    x='Country',
    y='Frequency Score',
    title='Top 3 Countries by Upload Frequency',
    labels={'Frequency Score': 'Avg Videos per Month'},
    template='plotly_dark',
    color='Frequency Score'
)
st.plotly_chart(fig_frequency, use_container_width=True)

# --- Summary Note ---
st.markdown("""
###
These metrics together help estimate where IShowSpeed’s content might gain the most momentum next. 
You can combine these scores manually or weight them in a scoring formula if desired.
""")






st.title("📊Analysis: Scoring Countries Based on Future Potential")

# Load Data
df = pd.read_csv("ishowspeed_yt_dataset_all.csv", parse_dates=["Date Posted"])
df = df[df['Country'].notna()]
df = df[df['Country'] != 'Not Applicable']

# Prepare month
df['Month'] = df['Date Posted'].dt.to_period("M").dt.to_timestamp()

# --- View Growth Score ---
monthly_views = df.groupby(['Country', 'Month'])['Views'].sum().reset_index()
monthly_views['Prev'] = monthly_views.groupby('Country')['Views'].shift(1)
monthly_views['Growth Rate'] = (
    (monthly_views['Views'] - monthly_views['Prev']) / monthly_views['Prev']) * 100
view_growth = monthly_views.dropna().groupby(
    'Country')['Growth Rate'].mean().reset_index()
view_growth.columns = ['Country', 'View Growth Score']

# --- Engagement Score ---
engagement = df.groupby('Country')[['Likes', 'Comments']].mean().reset_index()
engagement['Engagement Score'] = (
    engagement['Likes'] + engagement['Comments']) / 2
engagement = engagement[['Country', 'Engagement Score']]

# --- Frequency Score ---
upload_freq = df.groupby(['Country', 'Month'])[
    'Video ID'].count().reset_index()
upload_freq = upload_freq.groupby('Country')['Video ID'].mean().reset_index()
upload_freq.columns = ['Country', 'Frequency Score']

# --- Merge all scores ---
scores = view_growth.merge(engagement, on='Country', how='inner').merge(
    upload_freq, on='Country', how='inner')

# --- Normalize scores to 0–100 ---
scaler = MinMaxScaler()
scores[['View Growth Score', 'Engagement Score', 'Frequency Score']] = scaler.fit_transform(
    scores[['View Growth Score', 'Engagement Score', 'Frequency Score']]
) * 100

# --- Combined Score (equal weights) ---
scores['Combined Score'] = scores[['View Growth Score',
                                   'Engagement Score', 'Frequency Score']].mean(axis=1)
top_scores = scores.sort_values(by='Combined Score', ascending=False).head(10)

# --- Plot ---
fig = px.bar(
    top_scores,
    x='Country',
    y='Combined Score',
    color='Combined Score',
    title='🏆 Top 10 Countries by Combined Growth Potential Score',
    template='plotly_dark',
    labels={'Combined Score': 'Score (0–100)'}
)
st.plotly_chart(fig, use_container_width=True)

# --- Explanation Section ---
st.markdown("""
### 🧠 How Scores Were Calculated:

- **View Growth Score**: Measures average monthly growth in views.
- **Engagement Score**: Average likes and comments per video.
- **Frequency Score**: How often content is uploaded (videos per month).
- Each score was normalized to a **0–100 scale**, then combined using equal weighting.
- The **Combined Score** helps predict where IShowSpeed might gain future momentum.

You can customize the weights if needed (e.g., prioritize engagement more).
""")
