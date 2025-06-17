from sklearn.preprocessing import LabelEncoder
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from prophet import Prophet
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="YouTube Future Prediction", layout="wide")
st.title("📈 IShowSpeed YouTube: Future Prediction Dashboard")

# ----------------------------
# Load CSV from directory
# ----------------------------
df = pd.read_csv("ishowspeed_yt_dataset_all.csv")

# ----------------------------
# Data Cleaning & Feature Engineering
# ----------------------------
df["Date Posted"] = pd.to_datetime(df["Date Posted"], errors="coerce")
df["Time Posted"] = pd.to_datetime(df["Time Posted"], format='%H:%M:%S', errors='coerce').dt.hour
df["Views"] = pd.to_numeric(df["Views"], errors='coerce')
df["Likes"] = pd.to_numeric(df["Likes"], errors='coerce')
df["Comments"] = pd.to_numeric(df["Comments"], errors='coerce')

df["DayOfWeek"] = df["Date Posted"].dt.dayofweek
df["Month"] = df["Date Posted"].dt.month
df["EngagementRate"] = (df["Likes"] + df["Comments"]) / df["Views"]
df["IsLivestream"] = df["Was Livestream"].apply(lambda x: 1 if str(x).lower() == "yes" else 0)
df["WasCollab"] = df["Collaborators"].notna().astype(int)

df = df.dropna(subset=["Views"])

# ----------------------------
# Feature Selection
# ----------------------------
st.subheader("🔧 Predict Views for Future Videos")

df_encoded = pd.get_dummies(df, columns=["Content Type", "Video Type"], drop_first=True)
features = [
    "Duration (seconds)", "Time Posted", "DayOfWeek", "Month",
    "EngagementRate", "IsLivestream", "WasCollab"
] + [col for col in df_encoded.columns if "Content Type_" in col or "Video Type_" in col]

X = df_encoded[features].fillna(0)
y = df_encoded["Views"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

st.write(f"**Model Performance:**")
st.write(f"- MAE: `{mae:.2f}`")
st.write(f"- RMSE: `{rmse:.2f}`")

# ----------------------------
# Feature Importance
# ----------------------------
st.subheader("📊 Top 10 Feature Importances")
importances = model.feature_importances_
importance_df = pd.DataFrame({"Feature": X.columns, "Importance": importances})
top_features = importance_df.sort_values("Importance", ascending=False).head(10)

fig_imp = px.bar(top_features, x="Importance", y="Feature", orientation="h", title="Top Predictive Features")
st.plotly_chart(fig_imp, use_container_width=True)

# ----------------------------
# Time Series Forecasting (Prophet)
# ----------------------------
st.subheader("📅 Forecast Monthly Views")

ts_df = df[["Date Posted", "Views"]].dropna()
ts_df = ts_df.groupby(ts_df["Date Posted"].dt.to_period("M"))["Views"].sum().reset_index()
ts_df["Date Posted"] = ts_df["Date Posted"].dt.to_timestamp()
ts_df.columns = ["ds", "y"]

m = Prophet()
m.fit(ts_df)
# Find how many months between last data point and Dec 2025
last_date = ts_df["ds"].max()
target_date = pd.to_datetime("2025-12-31")
months_diff = (target_date.year - last_date.year) * \
    12 + (target_date.month - last_date.month)

# Create monthly future dataframe until Dec 2025
future = m.make_future_dataframe(periods=months_diff, freq='M')

forecast = m.predict(future)

fig_forecast = go.Figure()
fig_forecast.add_trace(go.Scatter(x=ts_df["ds"], y=ts_df["y"], name="Actual", mode="lines+markers"))
fig_forecast.add_trace(go.Scatter(x=forecast["ds"], y=forecast["yhat"], name="Forecast", mode="lines"))
fig_forecast.update_layout(title="Monthly Views Forecast", xaxis_title="Date", yaxis_title="Views")
st.plotly_chart(fig_forecast, use_container_width=True)


# ----------------------------
# 📈 Total Views by End of Year (Graph)
# ----------------------------
st.subheader("📈 Projected Cumulative Views Until End of 2025")

# Merge actual + forecasted monthly views
actual = ts_df.set_index("ds").copy()
predicted = forecast.set_index("ds")[["yhat"]].copy()
combined = actual.join(predicted, how="outer").reset_index()
combined = combined[combined["ds"] <= pd.Timestamp("2025-12-31")]

# Fill gaps: use actual if exists, else predicted
combined["combined_views"] = combined.apply(
    lambda row: row["y"] if not pd.isna(row["y"]) else row["yhat"], axis=1
)
combined = combined.sort_values("ds")
combined["cumulative_views"] = combined["combined_views"].cumsum()

# Plot cumulative line chart
fig_cum = px.line(
    combined,
    x="ds",
    y="cumulative_views",
    title="Cumulative Total Views (Actual + Forecast)",
    labels={"ds": "Date", "cumulative_views": "Cumulative Views"},
    markers=True,
)
fig_cum.add_scatter(
    x=[combined["ds"].max()],
    y=[combined["cumulative_views"].max()],
    mode="markers+text",
    text=[f"{int(combined['cumulative_views'].max()):,} views"],
    textposition="top center",
    marker=dict(color="red", size=10),
    name="Projected Total"
)
st.plotly_chart(fig_cum, use_container_width=True)

# ----------------------------
# 📊 Forecasted Monthly Views Breakdown
# ----------------------------
st.subheader("📊 Forecasted Monthly Views Until End of 2025")

future_months = forecast[forecast["ds"] > ts_df["ds"].max()]
fig_month = px.bar(
    future_months,
    x="ds",
    y="yhat",
    title="Forecasted Monthly Views",
    labels={"ds": "Month", "yhat": "Predicted Views"},
    color_discrete_sequence=["#636EFA"]
)
st.plotly_chart(fig_month, use_container_width=True)


# ----------------------------
# 📆 Feature 1: Total Views by End of This Year
# ----------------------------
st.subheader("📅 Projected Views by End of This Year")

current_year = datetime.today().year
last_date = pd.to_datetime(f"{current_year}-12-31")
remaining_forecast = forecast[(forecast['ds'] >= pd.Timestamp.today()) & (forecast['ds'] <= last_date)]
total_forecast_views = remaining_forecast["yhat"].sum()

st.metric("📊 Projected Views (Remaining Months)", f"{int(total_forecast_views):,} views")

# ----------------------------
# 🌍 Feature 3: Country-wise Monthly View Trends
# ----------------------------
st.subheader("🌍 Country-wise Monthly View Trends")

# Clean country column and exclude 'Not Applicable'
df_country = df[["Date Posted", "Country", "Views"]].dropna()
df_country = df_country[df_country["Country"].str.strip(
).str.lower() != "not applicable"]

df_country["Month"] = pd.to_datetime(
    df_country["Date Posted"]).dt.to_period("M").dt.to_timestamp()
country_monthly = df_country.groupby(["Country", "Month"])[
    "Views"].sum().reset_index()

# Top 5 countries by total views
top_countries = (
    country_monthly.groupby("Country")["Views"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
    .index.tolist()
)

country_monthly_top = country_monthly[country_monthly["Country"].isin(
    top_countries)]

fig_country = px.line(
    country_monthly_top,
    x="Month", y="Views", color="Country",
    markers=True,
    title="Top 5 Countries by Monthly Views"
)
st.plotly_chart(fig_country, use_container_width=True)

# ----------------------------
# Optional: View Raw Data
# ----------------------------
with st.expander("📄 View Cleaned Data"):
    st.dataframe(df.head())
    
# ----------------------------
# ⏳ Forecast Future Average Views by Content Type
# ----------------------------
st.subheader("📅 Forecast Monthly Average Views by Top 3 Content Types")

top_cts = df["Content Type"].value_counts().head(3).index.tolist()
fig_ct = go.Figure()

for ct in top_cts:
    ct_df = df[df["Content Type"] == ct][["Date Posted", "Views"]].dropna()
    ct_df = ct_df.groupby(ct_df["Date Posted"].dt.to_period("M"))[
        "Views"].mean().reset_index()
    ct_df["Date Posted"] = ct_df["Date Posted"].dt.to_timestamp()
    ct_df.columns = ["ds", "y"]

    if len(ct_df) >= 12:  # Only forecast if enough data
        m_ct = Prophet()
        m_ct.fit(ct_df)
        future_ct = m_ct.make_future_dataframe(periods=6, freq='M')
        forecast_ct = m_ct.predict(future_ct)

        fig_ct.add_trace(go.Scatter(
            x=forecast_ct["ds"], y=forecast_ct["yhat"], mode="lines", name=f"{ct} Forecast"))
        fig_ct.add_trace(go.Scatter(
            x=ct_df["ds"], y=ct_df["y"], mode="markers", name=f"{ct} Actual"))

fig_ct.update_layout(title="Forecasted Monthly Avg Views for Top Content Types",
                     xaxis_title="Month", yaxis_title="Avg Views")
st.plotly_chart(fig_ct, use_container_width=True)

# ----------------------------
# 🎛️ What-If Simulator: Predict Views for a Future Video
# ----------------------------
st.subheader("🎥 What-If Simulator: Predict Views for a Future Video")

with st.form("predict_form"):
    col1, col2 = st.columns(2)

    with col1:
        duration = st.slider("Video Duration (seconds)",
                             30, 18000, step=30, value=600)
        time_posted = st.slider("Hour Posted (0-23)", 0, 23, value=18)
        month = st.selectbox("Month Posted", list(range(1, 13)),
                             format_func=lambda x: pd.to_datetime(f"2023-{x}-01").strftime('%B'))

    with col2:
        is_livestream = st.radio("Was Livestream?", ["Yes", "No"])
        content_types = [col.replace("Content Type_", "")
                         for col in X.columns if "Content Type_" in col]
        video_types = [col.replace("Video Type_", "")
                       for col in X.columns if "Video Type_" in col]

        content_type = st.selectbox("Content Type", content_types)
        video_type = st.selectbox("Video Type", video_types)

    submitted = st.form_submit_button("🔮 Predict Views")

    if submitted:
        # Create input for each day of the week to compare
        results = []

        for day_of_week in range(7):
            input_data = pd.DataFrame(
                [np.zeros(X.shape[1])], columns=X.columns)

            # Set values
            input_data["Duration (seconds)"] = duration
            input_data["Time Posted"] = time_posted
            input_data["DayOfWeek"] = day_of_week
            input_data["Month"] = month
            input_data["IsLivestream"] = 1 if is_livestream == "Yes" else 0
            input_data["WasCollab"] = 0  # Removed from form

            # Set one-hot encoded fields
            ct_col = f"Content Type_{content_type}"
            vt_col = f"Video Type_{video_type}"
            if ct_col in input_data.columns:
                input_data[ct_col] = 1
            if vt_col in input_data.columns:
                input_data[vt_col] = 1

            predicted_views = model.predict(input_data)[0]
            results.append((["Mon", "Tue", "Wed", "Thu", "Fri",
                           "Sat", "Sun"][day_of_week], int(predicted_views)))

        # Convert to DataFrame for plotting
        df_results = pd.DataFrame(results, columns=["Day", "Predicted Views"])

        # Show results
        st.success(
            f"📈 Predicted Views on {df_results.loc[df_results['Predicted Views'].idxmax(), 'Day']}: `{df_results['Predicted Views'].max():,}`")

        # Plot
        fig = px.bar(df_results, x="Day", y="Predicted Views",
                     title="Predicted Views by Day of Week")
        st.plotly_chart(fig, use_container_width=True)
