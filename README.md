# ai-news-aggregator
# 📰 AI News Aggregator

An AI-powered news aggregation platform that collects news from multiple sources, categorizes articles, and presents the latest updates in an organized and easy-to-read interface.

The project is designed to bring news from different categories into a single platform while using automation and AI-based processing to improve how news is collected and presented.

---

## ✨ Features

- 📰 Aggregate news from multiple sources
- 🤖 AI-powered news processing
- 🗂️ Categorization of news articles
- 🔍 Organized and searchable news content
- 📊 News analysis and metrics
- 📈 Results and performance visualization
- 💾 Local database for storing news data
- 🔐 Environment-variable based configuration
- 🐳 Docker support
- 📄 Generate reports and result charts

---

## 🛠️ Tech Stack

- **Python**
- **AI / Machine Learning**
- **SQLite**
- **HTML / CSS / JavaScript**
- **Docker**
- **REST APIs**
- **Python libraries listed in `requirements.txt`**

---

## 📁 Project Structure

```text
ai-news-aggregator/
│
├── app/                       # Main application code
│
├── docker/                    # Docker-related configuration
│
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignored files
├── ai_news.db                 # Local SQLite database
│
├── main.py                    # Application entry point
│
├── generate_pdf.py             # Generates PDF reports
├── generate_results_charts.py  # Generates result charts
├── reset_db.py                 # Resets the local database
│
├── project_presentation_guide.pdf
├── project_results_and_metrics_report.pdf
├── results_metrics_chart.png
│
├── render.yaml                 # Deployment configuration
├── requirements.txt            # Python dependencies
│
└── README.md
