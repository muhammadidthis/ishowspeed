import streamlit as st
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.express as px

# --- Load and Prepare Data ---
df = pd.read_csv("ishowspeed_cleaned_processed.csv", parse_dates=['Date Posted'])

# Rename for consistency
df.rename(columns={
    'Date': 'Date Posted',
    'views': 'Views',
    'likes': 'Likes',
    'comments': 'Comments',
    'text': 'Title',
    'videoUrl': 'Video ID'
}, inplace=True)

# Drop rows without dates
df = df[df['Date Posted'].notna()]

# Monthly aggregation
df['Month'] = df['Date Posted'].dt.to_period('M').dt.to_timestamp()
monthly_df = df.groupby('Month')[['Views', 'Likes', 'Comments']].sum().reset_index()

# Engagement rate: (Likes + Comments) / Views
monthly_df['Engagement Rate'] = (monthly_df['Likes'] + monthly_df['Comments']) / monthly_df['Views'] * 100

# Streamlit layout
st.set_page_config(layout="wide")
st.title("🔮 Future Predictions for IShowSpeed's TikTok Performance")
st.markdown("Forecasting future monthly trends in views, likes, comments, and engagement.")

# Select forecast target
target = st.selectbox("📊 Choose what to predict:", ['Views', 'Likes', 'Comments', 'Engagement Rate'])

# Prepare data for Prophet
prophet_df = monthly_df[['Month', target]].rename(columns={'Month': 'ds', target: 'y'})

# Create and fit the model
model = Prophet()
model.fit(prophet_df)

# Make future dataframe
periods = st.slider("📆 How many months to forecast?", min_value=3, max_value=24, value=6)
future = model.make_future_dataframe(periods=periods, freq='M')
forecast = model.predict(future)

# Display forecast plot
st.subheader(f"📈 Forecast for {target}")
fig = plot_plotly(model, forecast)
st.plotly_chart(fig, use_container_width=True)



# Optional: historical + predicted in one chart
st.subheader("📉 Past vs Predicted Comparison")
historical = prophet_df.rename(columns={'ds': 'Month', 'y': f'Actual {target}'})
predicted = forecast[['ds', 'yhat']].rename(columns={'ds': 'Month', 'yhat': f'Predicted {target}'})
combined = pd.merge(historical, predicted, on='Month', how='outer')

fig_combined = px.line(combined, x='Month', y=[f'Actual {target}', f'Predicted {target}'],
                       labels={'value': target, 'Month': 'Month'},
                       title=f"{target}: Actual vs Forecast")
st.plotly_chart(fig_combined, use_container_width=True)
