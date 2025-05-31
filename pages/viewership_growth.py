import streamlit as st
import pandas as pd
import plotly.express as px

# Load dataset
df = pd.read_csv('ishowspeed_yt_dataset_all.csv', parse_dates=['Date Posted'])

# Extract year and month
df['Year'] = df['Date Posted'].dt.year
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()

# Group by month
monthly_stats = df.groupby('Month')['Views'].agg(
    ['sum', 'count']).reset_index()
monthly_stats.rename(
    columns={'sum': 'Total Views', 'count': 'Video Count'}, inplace=True)

# Calculate monthly growth rate
monthly_stats['Growth Rate (%)'] = monthly_stats['Total Views'].pct_change(
).fillna(0) * 100

# Find spike months (growth > 50%)
monthly_stats['Spike'] = monthly_stats['Growth Rate (%)'] > 50

# UI: Page title
st.title("📈 Viewership Growth")

st.markdown(
    "Analyze IShowSpeed’s monthly YouTube viewership and identify key growth spikes.")

# UI: Year dropdown filter at the top
years = sorted(df['Year'].unique())
selected_year = st.selectbox("Select Year", years, index=len(years)-1)

filtered_stats = monthly_stats[monthly_stats['Month'].dt.year == selected_year]

# Line chart: Total views per month
fig = px.line(
    filtered_stats,
    x='Month',
    y='Total Views',
    title=f'Total Monthly Views ({selected_year})',
    markers=True,
    hover_data={'Month': True, 'Total Views': ':.0f',
                'Growth Rate (%)': ':.2f'},
)

# Highlight spikes
spike_months = filtered_stats[filtered_stats['Spike']]
fig.add_scatter(
    x=spike_months['Month'],
    y=spike_months['Total Views'],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='Spike Months'
)

st.plotly_chart(fig, use_container_width=True)

# Bar chart: Monthly growth rate
st.subheader("📊 Monthly Viewership Growth Rate (%)")
fig2 = px.bar(
    filtered_stats,
    x='Month',
    y='Growth Rate (%)',
    color='Growth Rate (%)',
    color_continuous_scale='Viridis',
    title=f'Monthly Growth Rate in Views ({selected_year})'
)
st.plotly_chart(fig2, use_container_width=True)

# KPIs
st.subheader("📌 Key Stats")
col1, col2, col3 = st.columns(3)
col1.metric("Total Views", f"{int(filtered_stats['Total Views'].sum()):,}")
col2.metric("Avg Views/Month",
            f"{int(filtered_stats['Total Views'].mean()):,}")
col3.metric("Total Videos", f"{int(filtered_stats['Video Count'].sum()):,}")
