import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Set page config
st.set_page_config(page_title="Sentiment Dashboard", layout="wide")

# Load CSV
try:
    df = pd.read_csv("feedback_log_with_models.csv")
except FileNotFoundError:
    st.error("CSV file not found. Please make sure 'feedback_log_with_models.csv' exists.")
    st.stop()

# Preprocess
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Date"] = df["Timestamp"].dt.date

# Sidebar Filters
st.sidebar.title("🔎 Filters")
date_range = st.sidebar.date_input("Date Range", [df["Date"].min(), df["Date"].max()])
sentiments = st.sidebar.multiselect("Sentiment", df["Sentiment"].unique(), default=list(df["Sentiment"].unique()))
categories = st.sidebar.multiselect("Category", df["Category"].unique(), default=list(df["Category"].unique()))

# Filter data
filtered_df = df[(df["Date"] >= date_range[0]) & (df["Date"] <= date_range[1])]
filtered_df = filtered_df[filtered_df["Sentiment"].isin(sentiments) & filtered_df["Category"].isin(categories)]

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "📈 Trends", "🧠 Model Comparison", "📋 Logs"])

# =================== Tab 1: Overview ===================
with tab1:
    st.header("📊 Dashboard Overview")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Feedback", len(filtered_df))
    col2.metric("% Negative", f"{(len(filtered_df[filtered_df['Sentiment']=='NEGATIVE']) / len(filtered_df)*100):.1f}%")
    col3.metric("Avg. Severity", f"{filtered_df['Severity Score'].mean():.2f}")
    col4.metric("Tickets Created", len(filtered_df[filtered_df["JIRA_Ticket"] != "N/A"]))

# =================== Tab 2: Trends ===================
with tab2:
    st.header("📈 Feedback Trends")

    st.subheader("Sentiment Over Time")
    sentiment_trend = filtered_df.groupby(["Date", "Sentiment"]).size().reset_index(name="Count")
    fig1 = px.bar(sentiment_trend, x="Date", y="Count", color="Sentiment", barmode="group")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Category Over Time")
    category_trend = filtered_df.groupby(["Date", "Category"]).size().reset_index(name="Count")
    fig2 = px.line(category_trend, x="Date", y="Count", color="Category", markers=True)
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Severity Score Over Time")
    severity_trend = filtered_df.groupby("Date")["Severity Score"].mean().reset_index()
    fig3 = px.line(severity_trend, x="Date", y="Severity Score", markers=True)
    st.plotly_chart(fig3, use_container_width=True)

# =================== Tab 3: Model Comparison (Placeholder) ===================
with tab3:
    st.header("🧠 Model Comparison")

    # Check required column
    if 'Model' in filtered_df.columns:
        st.subheader("Sentiment Distribution by Model")
        sentiment_model = filtered_df.groupby(['Model', 'Sentiment']).size().reset_index(name='Count')
        fig_sentiment = px.bar(sentiment_model, x='Sentiment', y='Count', color='Model', barmode='group')
        st.plotly_chart(fig_sentiment, use_container_width=True)

        st.subheader("Average Severity by Model")
        severity_model = filtered_df.groupby('Model')["Severity Score"].mean().reset_index()
        fig_severity = px.bar(severity_model, x='Model', y='Severity Score', color='Model', text_auto=True)
        st.plotly_chart(fig_severity, use_container_width=True)

        st.subheader("Category Agreement")
        category_counts = filtered_df.groupby(['Model', 'Category']).size().reset_index(name='Count')
        fig_category = px.bar(category_counts, x='Category', y='Count', color='Model', barmode='group')
        st.plotly_chart(fig_category, use_container_width=True)
    else:
        st.warning("No model comparison available — 'Model' column not found in dataset.")

# =================== Tab 4: Logs ===================
with tab4:
    st.header("📋 Feedback Log")
    st.dataframe(filtered_df, use_container_width=True)

    st.download_button("📥 Download as CSV", data=filtered_df.to_csv(index=False), file_name="filtered_feedback.csv", mime="text/csv")

