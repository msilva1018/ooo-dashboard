# 🏖️ Out of Office Dashboard

A fun, interactive Streamlit dashboard to track who's out of the office, when they'll be back, and why. Entries are automatically cleaned up the day after they end — no manual housekeeping required.

## ✨ Features

- ➕ **Add OOO entries** with name, dates, reason, and optional note
- 🏖️ **"Out Today"** view with colorful cards and countdown
- 📅 **"Coming Up"** section for upcoming time off
- 📋 **All Entries** table with status filters and one-click delete
- 📅 **30-day calendar view** with a bar chart of daily OOO counts
- 🧹 **Auto-purge**: entries vanish automatically after their end date
- 🎨 Reason emojis (Vacation 🏖️, Sick 🤒, WFH 🏠, Conference 🎤, etc.)
- 💾 Data persists to a simple `ooo_data.csv` file

## 🚀 Quick Start (Local)

```bash
# 1. Clone your repo
git clone https://github.com/YOUR-USERNAME/ooo-dashboard.git
cd ooo-dashboard

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`.

## ☁️ Deploy to Streamlit Community Cloud

1. **Push this project to GitHub** (a public or private repo both work).
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **"New app"**, select your repo, branch (`main`), and set the main file path to `app.py`.
4. Click **Deploy** — you'll have a live URL in about a minute.

### One-time GitHub setup

```bash
cd ooo-dashboard
git init
git add .
git commit -m "Initial commit: OOO dashboard"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/ooo-dashboard.git
git push -u origin main
```

## 📁 Project Structure

```
ooo-dashboard/
├── app.py              # Main Streamlit app
├── requirements.txt    # Python dependencies
├── ooo_data.csv        # Auto-created on first run (don't commit if private)
├── .gitignore
└── README.md
```

## 🧠 How auto-removal works

Every time the app loads, it reads `ooo_data.csv` and filters out any row whose `end_date` is earlier than today. The cleaned data is then written back to the CSV. So entries silently disappear the day after a person returns.

## ⚠️ Note on Streamlit Cloud + persistence

Streamlit Community Cloud uses **ephemeral storage** — the `ooo_data.csv` may reset when the app restarts. For a small team this often works fine, but for production-grade persistence consider:

- Connecting to Google Sheets via `st-gsheets-connection`
- Using a hosted database (Supabase, Neon, etc.)
- Storing data in S3 or similar

## 🎨 Customize

- **Add more reasons**: edit the `REASON_EMOJIS` dict at the top of `app.py`
- **Change the color palette**: tweak the CSS gradient in the custom CSS block
- **Add fun messages**: extend the `FUN_MESSAGES` list

## 📝 License

MIT — do whatever you like with it.
