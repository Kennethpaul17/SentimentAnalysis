<<<<<<< HEAD
# SentimentAnalysis
Sentiment Analysis

# Sentiment Feedback Engine

This project uses AI-powered sentiment analysis to optimize service operations by:
- Analyzing customer feedback
- Categorizing issues (Application, Database, Infrastructure)
- Creating JIRA tickets based on severity
- Sending alerts to Slack
- Logging results to CSV
- Visualizing trends in a Streamlit dashboard

## Tech Stack
- Python, Hugging Face Transformers
- Streamlit, Plotly
- JIRA API, Slack Webhook
- GitHub for version control

## How to Run

```bash
streamlit run Sentiment_Analysis.py.HuggingFace

=======
cat <<EOF > README.md
# Sentiment Feedback Engine

This project implements an AI-driven engine to analyze customer sentiment in Managed Private Cloud (MPC) operations. It enables real-time monitoring, automated issue categorization, JIRA ticket creation, Slack alerting, and dashboard-based trend visualization.

## 🚀 Key Features

- 🧠 Sentiment Analysis using Hugging Face Transformers
- 🗂️ Topic Classification into Application, Database, and Infrastructure
- 🎫 Automatic JIRA Ticket Creation for Negative Sentiment
- 🔔 Real-time Slack Notifications for High-Severity Feedback
- 📦 CSV Logging of Processed Feedback
- 📊 Trend Monitoring via Streamlit Dashboard

## 🗂️ Project Structure

\`\`\`
├── src/                            # Core feedback engine scripts
│   ├── Sentiment_Analysis.HuggingFace.py
│   └── train_sentiment_model.py
│
├── dashboard/                     # Streamlit dashboard app
│   └── Enhanced_Streamlit_dashboard.py
│
├── data/                          # Logs and feedback history
│   └── feedback_log_with_models.csv
│
├── .gitignore
├── README.md
\`\`\`


## 📦 Dependencies

- Python 3.8+
- \`transformers\`, \`streamlit\`, \`jira\`, \`pandas\`, \`plotly\`, \`requests\`

## 👤 Author

**Kenneth Paul**  
MBA – Hochschule Hof, Germany  

## 📄 License

_This project is part of academic research.
EOF



## How to Run Transformers Model and the Reporting Tool StreamLit

cd /Users/kennethpaul17/feedback_engine
```bash
python3 Sentiment_Analysis.HuggingFace.py
streamlit run Enhanced_Streamlit_dashboard.py

