# 🔍 AI Resume Analyzer & ATS Optimizer

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/)

> **🚀 Live Demo:** [https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/](https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/)

---

## 📌 Overview

An AI-powered resume analysis tool that evaluates how well your resume matches a given job description. It provides a deterministic ATS match score, qualitative feedback, skill gap analysis, and project recommendations — all powered by Google Gemini.

---

## ✨ Features

- 📄 **PDF Resume Parsing** — Upload your resume and extract text automatically
- 📊 **ATS Match Score** — Deterministic scoring across skills, experience, and education
- 🤖 **AI Evaluation** — Google Gemini generates strengths, weaknesses, and actionable suggestions
- 🛠️ **Project Recommendations** — Personalized projects to bridge skill gaps
- 📜 **Analysis History** — Save and revisit past evaluations
- 📥 **PDF Report Download** — Export your full analysis as a formatted PDF report
- 🌓 **Dark / Light Mode** — Toggle between themes
- 🔐 **User Authentication** — Secure login and registration with PostgreSQL (Supabase)

---

## 🛠️ Tech Stack

| Layer       | Technology                          |
|-------------|--------------------------------------|
| Frontend    | Streamlit                            |
| AI / LLM    | Google Gemini (`google-genai` SDK)   |
| Database    | PostgreSQL via Supabase              |
| PDF Parsing | PyPDF                                |
| PDF Reports | ReportLab                            |
| Hosting     | Streamlit Community Cloud            |

---

## 🚀 Running Locally

### 1. Clone the repository
```bash
git clone https://github.com/bishtprateek270-hue/resume-analyzer.git
cd resume-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=your_supabase_postgres_connection_string
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Deployment

This app is deployed on **Streamlit Community Cloud**.

🔗 **Live App:** [https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/](https://resume-analyzer-nejevwpy2bcvrvuag9schr.streamlit.app/)

Secrets (`GEMINI_API_KEY` and `DATABASE_URL`) are configured via Streamlit Cloud's **Secrets Manager** under `Settings → Secrets`.

---

## ⏰ Automated Keep-Alive (Prevent Streamlit Sleep)

Streamlit Community Cloud automatically hibernates free apps after **7 days of inactivity** (displaying a `"Zzzz - This app has gone to sleep"` page). 

To solve this issue permanently and keep the live app awake 24/7, this repository includes an automated **GitHub Actions Workflow** using Playwright:

* 🤖 **Playwright Wake Script** — [`scripts/keep_alive.py`](scripts/keep_alive.py) launches a headless browser, visits the live app, and automatically clicks the *"Yes, get this app back up!"* button if the app is sleeping.
* 📅 **Scheduled Cron Job** — [`.github/workflows/keep_alive.yml`](.github/workflows/keep_alive.yml) runs every 3 days (`0 0 */3 * *`) to stay ahead of Streamlit's 7-day hibernation threshold.
* 🔘 **Manual Trigger** — Supports `workflow_dispatch` so you can wake up the app anytime on-demand from the GitHub Actions tab.

### 🛠️ How to use this solution in your own Streamlit app:
1. Copy [`.github/workflows/keep_alive.yml`](.github/workflows/keep_alive.yml) and [`scripts/keep_alive.py`](scripts/keep_alive.py) to your repo.
2. Update the `APP_URL` variable in `scripts/keep_alive.py` with your Streamlit Cloud URL.
3. Push to GitHub — your app will now stay awake 24/7 automatically!

---

## 📁 Project Structure

```
resume-analyzer/
├── .github/workflows/
│   └── keep_alive.yml  # GitHub Actions workflow for keeping Streamlit awake
├── scripts/
│   └── keep_alive.py    # Playwright headless browser wake-up script
├── app.py              # Main Streamlit application
├── analyzer.py         # ATS scoring algorithm
├── llm_helper.py       # Gemini LLM integration
├── parser.py           # PDF text extraction
├── database.py         # PostgreSQL database layer
├── auth.py             # User authentication logic
├── report_generator.py # PDF report generation
├── requirements.txt    # Python dependencies
└── .env                # Local environment variables (not committed)
```

---

## 📄 License

MIT License — feel free to fork and build on top of this project.
