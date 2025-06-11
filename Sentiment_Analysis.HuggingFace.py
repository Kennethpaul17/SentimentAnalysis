import os
import csv
import requests
from datetime import datetime
from transformers import pipeline
from jira import JIRA
import pandas as pd
import plotly.express as px
import streamlit as st

# ===== CONFIGURATION =====

JIRA_SERVER = "https://hof-university.atlassian.net"
JIRA_EMAIL = "kpaul@hof-university.de"
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = "SCRUM"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/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"

# ===== INITIALIZE MODELS =====

sentiment_model = pipeline("sentiment-analysis")
topic_model = pipeline("zero-shot-classification")
categories = ["Application", "Database", "Infrastructure"]

# ===== FUNCTIONS =====

def send_slack_alert(message):
    payload = {"text": message}
    response = requests.post(SLACK_WEBHOOK_URL, json=payload)
    if response.status_code == 200:
        print("✅ Sent alert to Slack")
    else:
        print(f"❌ Slack alert failed: {response.status_code} {response.text}")

def log_to_csv(combined_text, sentiment, score, category, confidence, jira_ticket):
    file_path = "feedback_log_with_models.csv"
    header = ["Timestamp", "Combined Input", "Sentiment", "Severity Score", "Category", "Category Confidence", "JIRA_Ticket"]

    try:
        with open(file_path, "x", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(header)
    except FileExistsError:
        pass

    with open(file_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().isoformat(),
            combined_text,
            sentiment,
            round(score, 4),
            category,
            round(confidence, 4),
            jira_ticket or "N/A"
        ])

# ===== CONNECT TO JIRA =====

jira = JIRA(
    basic_auth=(JIRA_EMAIL, JIRA_API_TOKEN),
    options={"server": JIRA_SERVER}
)

# ===== REAL-TIME FEEDBACK LOOP =====

print("\n🟢 Real-time Feedback Input Mode (type 'exit' to stop)\n")

while True:
    rating_input = input("⭐ Enter customer rating (1–5): ").strip()
    if rating_input.lower() == "exit":
        break
    try:
        rating = int(rating_input)
        if rating < 1 or rating > 5:
            raise ValueError
    except ValueError:
        print("❌ Invalid rating. Please enter a number between 1 and 5.")
        continue

    feedback = input("💬 Enter customer feedback: ").strip()
    if feedback.lower() == "exit":
        break

    summary = input("🗣️  Enter communication summary: ").strip()
    if summary.lower() == "exit":
        break

    combined_text = f"""
    Customer Rating: {rating}/5
    Customer Feedback: {feedback}
    Communication Summary: {summary}
    """

    # ----- Custom Severity Calculation -----
    rating_severity = (5 - rating) / 4  # 1 = 1.0, 5 = 0.0

    fb_sentiment = sentiment_model(feedback)[0]
    fb_score = fb_sentiment['score'] if fb_sentiment['label'] == 'NEGATIVE' else 1 - fb_sentiment['score']

    summary_sentiment = sentiment_model(summary)[0]
    summary_score = summary_sentiment['score'] if summary_sentiment['label'] == 'NEGATIVE' else 1 - summary_sentiment['score']

    # Weighted severity score
    overall_severity = 0.6 * rating_severity + 0.25 * fb_score + 0.15 * summary_score

    if overall_severity >= 0.75:
        sentiment_label = "NEGATIVE"
    elif overall_severity <= 0.4:
        sentiment_label = "POSITIVE"
    else:
        sentiment_label = "NEUTRAL"

    # ----- Topic Classification -----
    topic_result = topic_model(combined_text, candidate_labels=categories)
    top_category = topic_result["labels"][0]
    topic_confidence = topic_result["scores"][0]

    # ----- Display Summary -----
    print(f"\n→ Sentiment: {sentiment_label} (Severity Score: {overall_severity:.2f})")
    print(f"→ Category: {top_category} ({topic_confidence:.2f})")

    jira_ticket = None

    if sentiment_label == "NEGATIVE":
        issue_dict = {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": f"{top_category} issue from rated feedback",
            "description": f"{combined_text}\nSentiment: {sentiment_label} (Severity: {overall_severity:.2f})\nCategory: {top_category} ({topic_confidence:.2f})",
            "issuetype": {"name": "Task"},
            "labels": ["ai_feedback", f"category_{top_category.lower()}"]
        }
        new_issue = jira.create_issue(fields=issue_dict)
        jira_ticket = new_issue.key
        print(f"✅ JIRA ticket created: {jira_ticket}")

        slack_message = f"""
        🔔 *Negative Feedback Alert!*
        • *Rating*: {rating}/5
        • *Feedback*: {feedback}
        • *Category*: {top_category}
        • *Severity*: {overall_severity:.2f}
        • *JIRA Ticket*: {jira_ticket}
        """
        send_slack_alert(slack_message)
    else:
        print("✅ No ticket created (sentiment not negative).")

    log_to_csv(combined_text, sentiment_label, overall_severity, top_category, topic_confidence, jira_ticket)
    print("📦 Logged to CSV.\n")

# ===== STREAMLIT DASHBOARD (Trend Analysis) =====

st.set_page_config(page_title="Feedback Trend Dashboard", layout="wide")

try:
    df = pd.read_csv("feedback_log_with_models.csv")
except FileNotFoundError:
    st.error("CSV log file not found. Please run the feedback processing script first.")
    st.stop()

# Convert timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"])
df["Date"] = df["Timestamp"].dt.date

# Sidebar filters
with st.sidebar:
    st.header("🔍 Filter Options")
    sentiment_filter = st.multiselect("Sentiment", options=df["Sentiment"].unique(), default=list(df["Sentiment"].unique()))
    category_filter = st.multiselect("Category", options=df["Category"].unique(), default=list(df["Category"].unique()))

# Apply filters
filtered_df = df[df["Sentiment"].isin(sentiment_filter) & df["Category"].isin(category_filter)]

# Header
st.title("📊 Feedback Monitoring & Trend Analysis Dashboard")
st.markdown("This dashboard analyzes real-time customer feedback trends using sentiment and category breakdowns.")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Feedbacks", len(filtered_df))
col2.metric("Negative Feedbacks", len(filtered_df[filtered_df["Sentiment"] == "NEGATIVE"]))
col3.metric("Tickets Created", len(filtered_df[filtered_df["JIRA_Ticket"] != "N/A"]))

# Data Table
st.subheader("📋 Feedback Log")
st.dataframe(filtered_df, use_container_width=True)

# Sentiment Trend Over Time
st.subheader("📈 Sentiment Trend Over Time")
sentiment_trend = filtered_df.groupby(["Date", "Sentiment"]).size().reset_index(name="Count")
fig = px.line(sentiment_trend, x="Date", y="Count", color="Sentiment", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Category Trend Over Time
st.subheader("🗂️ Category Trend Over Time")
category_trend = filtered_df.groupby(["Date", "Category"]).size().reset_index(name="Count")
fig = px.line(category_trend, x="Date", y="Count", color="Category", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Severity Score Trend
st.subheader("🔥 Average Severity Score Trend")
severity_trend = filtered_df.groupby("Date")["Severity Score"].mean().reset_index()
fig = px.line(severity_trend, x="Date", y="Severity Score", markers=True)
st.plotly_chart(fig, use_container_width=True)

# Ticket Volume Over Time
st.subheader("🎫 JIRA Tickets Created Over Time")
filtered_df["Ticket Created"] = filtered_df["JIRA_Ticket"].apply(lambda x: x != "N/A")
ticket_trend = filtered_df[filtered_df["Ticket Created"]].groupby("Date").size().reset_index(name="Tickets")
fig = px.bar(ticket_trend, x="Date", y="Tickets")
st.plotly_chart(fig, use_container_width=True)

st.success("Dashboard updated successfully.")

