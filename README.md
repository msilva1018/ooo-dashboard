# LCN Consulting — Out of Office

A dark, professional Streamlit dashboard for tracking who's away, when they're
back, and why. Entries are stored in **Google Sheets** so they're shared across
the team and survive restarts, and they're cleaned up automatically the day
after they end.

## What's inside

- **Persistent storage** via Google Sheets (with a local CSV fallback for quick local runs)
- **Overview** — "Out today" and "Coming up" shown as dimensional cards
- **All entries** — sortable table plus inline edit / delete
- **Calendar** — month view of who's out on each day
- **Auto-cleanup** — entries disappear the day after their end date
- **On-brand dark theme** built from the LCN palette (navy, steel blue, maroon)

---

## ⚠️ Read this first: why entries weren't saving

The previous version wrote to a local `ooo_data.csv`. **Streamlit Community
Cloud uses ephemeral storage** — that file is wiped whenever the app reboots,
redeploys, or wakes from sleep, so anything added through the app vanished.

This version fixes that by saving to **Google Sheets**. The local CSV is kept
only as a zero-setup fallback for running on your own machine. The sidebar shows
a live status badge:

- 🟢 **Synced to Google Sheets** — saving is working and shared
- ⚠️ **Using a local file** — finish the Google Sheets setup below

---

## 🔑 Set up persistent storage (Google Sheets)

You'll create a free Google service account, share one spreadsheet with it, and
paste the credentials into Streamlit. ~10 minutes, one time.

**1. Create the spreadsheet**
   - Make a new Google Sheet.
   - Rename the first tab to exactly `ooo_data`.
   - In row 1, add these headers (one per column):
     `id`, `name`, `start_date`, `end_date`, `reason`, `note`

**2. Create a service account**
   - Go to <https://console.cloud.google.com/> → create (or pick) a project.
   - Enable the **Google Sheets API** and **Google Drive API** for that project.
   - **APIs & Services → Credentials → Create credentials → Service account.**
   - Open the new service account → **Keys → Add key → JSON**. A `.json` file downloads.

**3. Share the sheet with the service account**
   - Open the JSON file and copy the `client_email` (looks like
     `something@your-project.iam.gserviceaccount.com`).
   - In the Google Sheet, click **Share** and give that email **Editor** access.

**4. Add the credentials to Streamlit**
   - Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and fill
     in the values from your JSON file, plus your sheet's URL.
   - On **Streamlit Cloud**, instead paste the same content into
     **App → Settings → Secrets**.
   - `secrets.toml` is gitignored — never commit real keys.

Reload the app. The badge should turn green, and every add/edit/delete now
writes straight to the sheet.

> Prefer a database instead? The storage layer in `app.py` is isolated in
> `_read_raw()` / `_write_raw()`, so swapping in Supabase, Neon, or Postgres is a
> small change in those two functions.

---

## 🚀 Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Opens at `http://localhost:8501`. Without Google Sheets configured it uses the
local `ooo_data.csv` — fine for testing, just not persistent in the cloud.

## ☁️ Deploy to Streamlit Community Cloud

1. Push this project to GitHub (keep `LCN_Logo_UPDATED_2024-1.jpg` in the repo so the logo renders).
2. Go to <https://share.streamlit.io>, sign in with GitHub, click **New app**.
3. Pick the repo and branch, set the main file to `app.py`, and **Deploy**.
4. Add your Google Sheets credentials under **Settings → Secrets** (see above).

## 📁 Project structure

```
ooo-dashboard/
├── app.py                         # Main app
├── requirements.txt               # Dependencies
├── LCN_Logo_UPDATED_2024-1.jpg    # Logo (shown in the header)
├── ooo_data.csv                   # Local fallback only
├── .streamlit/
│   ├── config.toml                # Dark on-brand theme
│   └── secrets.toml.example       # Google Sheets credentials template
├── .gitignore
└── README.md
```

## 🎨 Customize

- **Theme colors:** edit the `:root` variables in the CSS block near the top of `app.py`, and the matching values in `.streamlit/config.toml`.
- **Reasons:** edit the `REASONS` dictionary in `app.py`.
- **Logo:** replace the `.jpg`; the header reads it automatically.

## 📝 License

MIT — do whatever you like with it.
