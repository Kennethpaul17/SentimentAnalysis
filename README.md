# Sentiment Feedback Engine

This project implements an NLP-powered engine to analyze customer sentiment in Managed Private Cloud operations. It enables real-time monitoring, automated issue categorization, and actionable alerting across service operations.

## Features

- 🧠 Sentiment Analysis using Hugging Face Transformers
- 🗂️ Topic Classification into Application, Database, and Infrastructure
- 🎫 JIRA Ticket Creation for Negative Feedback
- 🔔 Slack Notifications for High-Severity Cases
- 📦 CSV Logging of Processed Feedback
- 📊 Streamlit Dashboard for Trend Analysis

## Project Structure


## How to Run Transformers Model and the Reporting Tool StreamLit

```bash
python3 Sentiment_Analysis.HuggingFace.py
streamlit run Enhanced_Streamlit_dashboard.py
