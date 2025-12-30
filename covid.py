# -----------------------------
# COVID-19 Global Data Analysis & Dashboard
# -----------------------------
# Author: Khushi Dave
# Objective: Analyze COVID-19 trends globally, derive insights, visualize data, and build an interactive dashboard

# -----------------------------
# Step 1: Import Libraries
# -----------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import streamlit as st

# -----------------------------
# Step 2: Load Dataset
# -----------------------------
@st.cache_data
def load_data(local_path: str | None = None):
    """Load OWID COVID dataset. If local_path provided, load that; else fetch from OWID URL."""
    url = r"https://www.kaggle.com/datasets/caesarmario/our-world-in-data-covid19-dataset"
    try:
        if local_path:
            df = pd.read_csv(local_path)
        else:
            df = pd.read_csv(url, low_memory=False)
    except Exception as e:
        # fallback: try local data folder
        if local_path is None:
            try:
                df = pd.read_csv(r"C:\Users\Bhumi\Desktop\python project\owid-covid-data.csv", low_memory=False)
            except Exception as e2:
                raise RuntimeError("Could not load dataset from URL or data/ folder.") from e2
        else:
            raise
    # keep only needed columns if they exist
    columns_needed = [
        'location', 'date', 'total_cases', 'new_cases',
        'total_deaths', 'new_deaths',
        'total_vaccinations', 'people_vaccinated', 'population'
    ]
    df = df[[c for c in columns_needed if c in df.columns]]
    df['date'] = pd.to_datetime(df['date'])
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df


df = load_data()

# -----------------------------
# Step 3: Streamlit Layout
# -----------------------------
st.title("🌎 COVID-19 Data Analysis & Interactive Dashboard")
st.markdown("""
Analyze global COVID-19 trends with both static analysis and interactive charts.
""")

# -----------------------------
# Step 4: Static Insights (EDA with Matplotlib/Seaborn)
# -----------------------------
st.header("📊 Static Global Insights")

# Top 10 countries by total cases
st.subheader("Top 10 Countries by Total COVID-19 Cases")
top_cases = df.groupby('location')['total_cases'].max().sort_values(ascending=False).head(10)
fig1, ax1 = plt.subplots(figsize=(12,6))
sns.barplot(x=top_cases.index, y=top_cases.values, palette="viridis", ax=ax1)
ax1.set_title("Top 10 Countries by Total COVID-19 Cases")
ax1.set_ylabel("Total Cases")
plt.xticks(rotation=20)
st.pyplot(fig1)

# Global daily new cases trend
st.subheader("Global Daily New Cases Trend")
global_cases = df.groupby('date')['new_cases'].sum()
fig2, ax2 = plt.subplots(figsize=(14,6))
ax2.plot(global_cases.index, global_cases.values, color="red")
ax2.set_title("Global Daily New Cases Over Time")
ax2.set_xlabel("Date")
ax2.set_ylabel("New Cases")
st.pyplot(fig2)

# -----------------------------
# Step 5: Interactive Dashboard
# -----------------------------
st.header("🎛 Interactive Dashboard")

# Country selection
countries = df['location'].unique()
selected_countries = st.multiselect("Select Countries", countries, default=['India', 'United States', 'Brazil'])

# Date range filter
min_date = df['date'].min()
max_date = df['date'].max()
start_date, end_date = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

# Filter data
filtered_df = df[(df['location'].isin(selected_countries)) &
                 (df['date'] >= pd.to_datetime(start_date)) &
                 (df['date'] <= pd.to_datetime(end_date))]

# Total cases trend
st.subheader("📈 Total COVID-19 Cases Over Time")
fig_cases = px.line(filtered_df, x='date', y='total_cases', color='location',
                    labels={'total_cases':'Total Cases', 'date':'Date', 'location':'Country'},
                    title="Total COVID-19 Cases Trend")
st.plotly_chart(fig_cases)

# Daily new cases trend
st.subheader("⚡ Daily New Cases Over Time")
fig_new_cases = px.line(filtered_df, x='date', y='new_cases', color='location',
                        labels={'new_cases':'Daily New Cases', 'date':'Date', 'location':'Country'},
                        title="Daily New Cases Trend")
st.plotly_chart(fig_new_cases)

# Vaccination progress
if "people_vaccinated" in df.columns:
    st.subheader("💉 Vaccination Progress")
    fig_vacc = px.line(filtered_df, x='date', y='people_vaccinated', color='location',
                       labels={'people_vaccinated':'People Vaccinated', 'date':'Date', 'location':'Country'},
                       title="Vaccination Trend")
    st.plotly_chart(fig_vacc)

# -----------------------------
# Step 6: Latest Comparison Table
# -----------------------------
st.header("📌 Latest COVID-19 Statistics")
latest_data = filtered_df.sort_values('date').groupby('location').tail(1)[
    ['location','total_cases','new_cases','total_deaths','new_deaths','total_vaccinations','people_vaccinated']]
st.dataframe(latest_data)

# -----------------------------
# Step 7: Insights Summary
# -----------------------------
st.header("📝 Insights")
st.markdown(f"""
- **Top 5 countries with highest cases:**  
{top_cases.head().to_markdown()}

- **Date range analyzed:** {start_date} to {end_date}  
""")

# Export cleaned data option
st.download_button("Download Cleaned Data (CSV)", df.to_csv(index=False), "Cleaned_COVID19_Data.csv", "text/csv")

