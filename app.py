"""
🏖️ Out of Office Dashboard
A fun, interactive dashboard to track who's out and when.
"""

import streamlit as st
import pandas as pd
from datetime import date, datetime, timedelta
import os
import random

# ---------- Page Config ----------
st.set_page_config(
    page_title="OOO Dashboard 🏖️",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Constants ----------
DATA_FILE = "ooo_data.csv"

REASON_EMOJIS = {
    "Vacation": "🏖️",
    "Sick": "🤒",
    "Personal": "🌿",
    "Holiday": "🎉",
    "WFH": "🏠",
    "Conference": "🎤",
    "Family": "👨‍👩‍👧",
    "Other": "📌",
}

FUN_MESSAGES = [
    "Living their best life ✨",
    "Catching some rays ☀️",
    "Off the grid 🌲",
    "Recharging batteries 🔋",
    "On an adventure 🗺️",
    "Taking a breather 🌬️",
    "Out exploring 🧭",
    "Enjoying some R&R 🛌",
]

# ---------- Custom CSS ----------
st.markdown(
    """
    <style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #FFA07A);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        text-align: center;
        color: #888;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    .ooo-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border-left: 6px solid #4ECDC4;
        color: #1a1a1a;
    }
    .ooo-card-today {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-left: 6px solid #FF6B6B;
        color: #1a1a1a;
    }
    .ooo-card-upcoming {
        background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        border-left: 6px solid #4CAF50;
        color: #1a1a1a;
    }
    .ooo-name {
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
        color: #1a1a1a;
    }
    .ooo-meta {
        color: #444;
        font-size: 0.95rem;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 10px;
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Data Helpers ----------
def load_data() -> pd.DataFrame:
    """Load OOO data and auto-purge entries whose end_date has already passed."""
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(
            columns=["id", "name", "start_date", "end_date", "reason", "note"]
        )
        df.to_csv(DATA_FILE, index=False)
        return df

    df = pd.read_csv(DATA_FILE)
    if df.empty:
        return df

    df["start_date"] = pd.to_datetime(df["start_date"]).dt.date
    df["end_date"] = pd.to_datetime(df["end_date"]).dt.date

    # Auto-remove past entries (end_date strictly before today)
    today = date.today()
    before_count = len(df)
    df = df[df["end_date"] >= today].reset_index(drop=True)
    if len(df) < before_count:
        save_data(df)

    return df


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(DATA_FILE, index=False)


def add_entry(name: str, start: date, end: date, reason: str, note: str) -> None:
    df = load_data()
    new_id = (df["id"].max() + 1) if not df.empty else 1
    new_row = pd.DataFrame(
        [
            {
                "id": int(new_id),
                "name": name.strip(),
                "start_date": start,
                "end_date": end,
                "reason": reason,
                "note": note.strip(),
            }
        ]
    )
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)


def delete_entry(entry_id: int) -> None:
    df = load_data()
    df = df[df["id"] != entry_id].reset_index(drop=True)
    save_data(df)


def status_for(row, today: date) -> str:
    if row["start_date"] <= today <= row["end_date"]:
        return "today"
    if row["start_date"] > today:
        return "upcoming"
    return "past"


# ---------- Header ----------
st.markdown('<div class="main-title">🏖️ Out of Office Dashboard</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Who\'s out, who\'s in, and who\'s sipping a margarita 🍹</div>',
    unsafe_allow_html=True,
)

# ---------- Sidebar: Add Entry ----------
with st.sidebar:
    st.header("➕ Add OOO Entry")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Alex Johnson")
        col_s, col_e = st.columns(2)
        with col_s:
            start = st.date_input("Start date", value=date.today())
        with col_e:
            end = st.date_input("End date", value=date.today())
        reason = st.selectbox("Reason", list(REASON_EMOJIS.keys()))
        note = st.text_area("Note (optional)", placeholder="Back Monday! 🌴", height=80)

        submitted = st.form_submit_button("Add Entry", use_container_width=True)
        if submitted:
            if not name.strip():
                st.error("Please enter a name.")
            elif end < start:
                st.error("End date can't be before start date.")
            else:
                add_entry(name, start, end, reason, note)
                st.success(f"Added {name}'s {reason.lower()} 🎉")
                st.rerun()

    st.divider()
    st.caption(
        "🧹 Entries are automatically removed the day after they end. "
        "All data is stored in `ooo_data.csv`."
    )

# ---------- Main Data ----------
df = load_data()
today = date.today()

# ---------- Top Metrics ----------
if df.empty:
    out_today = upcoming = total = 0
else:
    out_today = df[(df["start_date"] <= today) & (df["end_date"] >= today)].shape[0]
    upcoming = df[df["start_date"] > today].shape[0]
    total = df.shape[0]

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("🏖️ Out Today", out_today)
with m2:
    st.metric("📅 Upcoming", upcoming)
with m3:
    st.metric("📊 Total Entries", total)
with m4:
    st.metric("🗓️ Today", today.strftime("%b %d"))

st.divider()

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["🏠 Dashboard", "📋 All Entries", "📅 Calendar View"])

# ---------- Tab 1: Dashboard ----------
with tab1:
    if df.empty:
        st.info("No OOO entries yet! Add one from the sidebar to get started. 👈")
        st.markdown("### 🎈 Everyone's in the office today!")
    else:
        df_sorted = df.sort_values("start_date").reset_index(drop=True)

        # Currently out
        st.subheader("🏖️ Out Today")
        out_now = df_sorted[
            (df_sorted["start_date"] <= today) & (df_sorted["end_date"] >= today)
        ]
        if out_now.empty:
            st.success("🎉 Everyone's in today! Full house.")
        else:
            cols = st.columns(min(3, len(out_now)))
            for i, (_, row) in enumerate(out_now.iterrows()):
                with cols[i % len(cols)]:
                    emoji = REASON_EMOJIS.get(row["reason"], "📌")
                    has_note = bool(row["note"]) and not pd.isna(row["note"])
                    fun = row["note"] if has_note else random.choice(FUN_MESSAGES)
                    days_left = (row["end_date"] - today).days
                    days_text = "Returns tomorrow! 🎯" if days_left == 0 else f"{days_left} day{'s' if days_left != 1 else ''} left"
                    card_html = (
                        '<div class="ooo-card ooo-card-today">'
                        f'<div class="ooo-name">{emoji} {row["name"]}</div>'
                        '<div class="ooo-meta">'
                        f'<b>{row["reason"]}</b> · {row["start_date"].strftime("%b %d")} → {row["end_date"].strftime("%b %d")}<br>'
                        f'<i>{fun}</i><br>'
                        f'⏳ {days_text}'
                        '</div>'
                        '</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

        st.markdown("&nbsp;")
        # Coming up
        st.subheader("📅 Coming Up")
        upcoming_df = df_sorted[df_sorted["start_date"] > today].head(6)
        if upcoming_df.empty:
            st.info("No upcoming OOO entries on the schedule.")
        else:
            cols = st.columns(min(3, len(upcoming_df)))
            for i, (_, row) in enumerate(upcoming_df.iterrows()):
                with cols[i % len(cols)]:
                    emoji = REASON_EMOJIS.get(row["reason"], "📌")
                    days_until = (row["start_date"] - today).days
                    when = "Tomorrow!" if days_until == 1 else f"In {days_until} days"
                    has_note = bool(row["note"]) and not pd.isna(row["note"])
                    note_html = f'<br><i>{row["note"]}</i>' if has_note else ''
                    card_html = (
                        '<div class="ooo-card ooo-card-upcoming">'
                        f'<div class="ooo-name">{emoji} {row["name"]}</div>'
                        '<div class="ooo-meta">'
                        f'<b>{row["reason"]}</b> · {row["start_date"].strftime("%b %d")} → {row["end_date"].strftime("%b %d")}<br>'
                        f'🚀 {when}'
                        f'{note_html}'
                        '</div>'
                        '</div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)

# ---------- Tab 2: All Entries ----------
with tab2:
    if df.empty:
        st.info("Nothing to show yet. Add an entry from the sidebar!")
    else:
        st.subheader("📋 All Active Entries")
        display = df.copy().sort_values("start_date").reset_index(drop=True)
        display["Status"] = display.apply(
            lambda r: "🟢 Out now" if r["start_date"] <= today <= r["end_date"]
            else ("🔵 Upcoming" if r["start_date"] > today else "⚪ Past"),
            axis=1,
        )
        display["Reason"] = display["reason"].apply(
            lambda r: f"{REASON_EMOJIS.get(r, '📌')} {r}"
        )
        display = display.rename(
            columns={
                "name": "Name",
                "start_date": "Start",
                "end_date": "End",
                "note": "Note",
            }
        )

        st.dataframe(
            display[["Name", "Reason", "Start", "End", "Status", "Note"]],
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### 🗑️ Remove an entry")
        options = {
            f"{r['name']} — {r['reason']} ({r['start_date']} → {r['end_date']})": int(r["id"])
            for _, r in df.iterrows()
        }
        if options:
            choice = st.selectbox("Select entry to remove", list(options.keys()))
            if st.button("Delete entry", type="primary"):
                delete_entry(options[choice])
                st.success("Entry removed ✅")
                st.rerun()

# ---------- Tab 3: Calendar View ----------
with tab3:
    if df.empty:
        st.info("No entries yet — calendar's wide open!")
    else:
        st.subheader("📅 Next 30 Days")
        days_ahead = 30
        date_range = [today + timedelta(days=i) for i in range(days_ahead)]

        calendar_rows = []
        for d in date_range:
            out_on_day = df[(df["start_date"] <= d) & (df["end_date"] >= d)]
            people = ", ".join(
                f"{REASON_EMOJIS.get(r['reason'], '📌')} {r['name']}"
                for _, r in out_on_day.iterrows()
            )
            calendar_rows.append(
                {
                    "Date": d.strftime("%a %b %d"),
                    "Count": len(out_on_day),
                    "Who's Out": people if people else "—",
                }
            )

        cal_df = pd.DataFrame(calendar_rows)

        # Bar chart of OOO count by day
        st.bar_chart(cal_df.set_index("Date")["Count"], height=250)

        st.dataframe(cal_df, use_container_width=True, hide_index=True)

# ---------- Footer ----------
st.divider()
st.caption(
    "Made with ❤️ and Streamlit · "
    f"Last refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
)
