"""
LCN Consulting — Out of Office
Team availability at a glance.

Data is stored persistently in Google Sheets when configured (recommended for
shared / cloud deployments), and falls back to a local CSV file so the app still
runs with zero setup on your machine. See README.md for the Google Sheets setup.
"""

import os
import base64
import calendar
from datetime import date, datetime

import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="LCN Consulting · Out of Office",
    page_icon="🗓️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DATA_FILE = "ooo_data.csv"
WORKSHEET = "ooo_data"
COLUMNS = ["id", "name", "start_date", "end_date", "reason", "note"]

# A small, restrained glyph + accent for each reason. Kept subtle for a
# professional feel rather than a party of emoji.
REASONS = {
    "Vacation":   {"glyph": "🏝", "tone": "calm"},
    "Sick":       {"glyph": "🩺", "tone": "alert"},
    "Personal":   {"glyph": "🌿", "tone": "calm"},
    "Holiday":    {"glyph": "🎌", "tone": "calm"},
    "WFH":        {"glyph": "🏠", "tone": "neutral"},
    "Conference": {"glyph": "🎤", "tone": "neutral"},
    "Family":     {"glyph": "👪", "tone": "calm"},
    "Other":      {"glyph": "•",  "tone": "neutral"},
}
REASON_OPTIONS = list(REASONS.keys())


def reason_glyph(reason: str) -> str:
    return REASONS.get(reason, {}).get("glyph", "•")


# ---------------------------------------------------------------------------
# Logo (embedded as a data URI so it always renders once committed to the repo)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def logo_data_uri() -> str | None:
    candidates = [
        "LCN_Logo_UPDATED_2024-1.jpg",
        "assets/LCN_Logo_UPDATED_2024-1.jpg",
        ".streamlit/LCN_Logo_UPDATED_2024-1.jpg",
    ]
    for path in candidates:
        if os.path.exists(path):
            with open(path, "rb") as fh:
                encoded = base64.b64encode(fh.read()).decode()
            return f"data:image/jpeg;base64,{encoded}"
    return None


# ---------------------------------------------------------------------------
# Theme  —  dark, professional, "dimensional" (per LCN's tagline)
# Palette is derived from the LCN logo: navy + steel blue + a maroon ember.
# ---------------------------------------------------------------------------
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
  --ink:        #0E1620;
  --panel:      #16212E;
  --panel-2:    #1E2C3D;
  --navy:       #1C3E63;
  --steel:      #7AA0CB;
  --steel-soft: rgba(122,160,203,0.16);
  --ember:      #C2495A;
  --ember-soft: rgba(194,73,90,0.16);
  --paper:      #E9EFF7;
  --muted:      #93A6BD;
  --line:       #28394D;
}

/* --- App shell --- */
.stApp { background:
    radial-gradient(1200px 600px at 85% -5%, rgba(28,62,99,0.45), transparent 60%),
    radial-gradient(900px 500px at -5% 10%, rgba(122,160,203,0.10), transparent 55%),
    var(--ink);
}
.block-container { padding-top: 1.4rem; max-width: 1180px; }

h1, h2, h3, .lcn-display { font-family: 'Space Grotesk', sans-serif; color: var(--paper); letter-spacing: -0.01em; }
.stApp, p, span, label, div { font-family: 'Inter', sans-serif; }

[data-testid="stSidebar"] { background: linear-gradient(180deg, #13202E 0%, #101A26 100%); border-right: 1px solid var(--line); }
[data-testid="stSidebar"] * { color: var(--paper); }

/* --- Hero --- */
.lcn-hero {
  position: relative; overflow: hidden;
  border: 1px solid var(--line); border-radius: 20px;
  background: linear-gradient(140deg, #16314E 0%, #122336 45%, #0E1A28 100%);
  padding: 1.5rem 1.7rem; margin-bottom: 1.25rem;
  box-shadow: 0 24px 50px -22px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.05);
}
.lcn-hero::before, .lcn-hero::after {
  content: ""; position: absolute; border-radius: 50%; filter: blur(2px); pointer-events: none;
}
.lcn-hero::before { width: 240px; height: 240px; right: 8%; top: -90px;
  background: radial-gradient(circle at 35% 35%, rgba(122,160,203,0.55), rgba(122,160,203,0) 70%); }
.lcn-hero::after { width: 300px; height: 300px; right: -40px; top: -40px;
  background: radial-gradient(circle at 40% 40%, rgba(28,62,99,0.85), rgba(28,62,99,0) 70%); }
.lcn-hero-row { position: relative; z-index: 2; display: flex; align-items: center; gap: 1.4rem; flex-wrap: wrap; }
.lcn-logo-plate {
  background: #F5F7FB; border-radius: 14px; padding: 14px 18px; line-height: 0;
  box-shadow: 0 14px 26px -12px rgba(0,0,0,0.75), inset 0 1px 0 rgba(255,255,255,0.9);
  transform: perspective(700px) rotateY(-4deg); transition: transform .3s ease;
}
.lcn-logo-plate:hover { transform: perspective(700px) rotateY(0deg) translateY(-2px); }
.lcn-logo-plate img { height: 58px; width: auto; display: block; }
.lcn-hero-text { display: flex; flex-direction: column; }
.lcn-eyebrow { font-family:'Space Grotesk'; font-size: .72rem; letter-spacing: .28em; text-transform: uppercase; color: var(--steel); margin-bottom: .25rem; }
.lcn-title { font-family:'Space Grotesk'; font-size: 2.15rem; font-weight: 700; color: #fff; margin: 0; line-height: 1.05; }
.lcn-sub { color: var(--muted); font-size: 1rem; margin-top: .35rem; }

/* --- Metric tiles (3D) --- */
.lcn-metrics { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin: .25rem 0 1.1rem; }
.lcn-metric {
  position: relative; border: 1px solid var(--line); border-radius: 14px;
  background: linear-gradient(160deg, var(--panel-2) 0%, var(--panel) 100%);
  padding: 1rem 1.1rem 1.05rem;
  box-shadow: 0 18px 30px -16px rgba(0,0,0,0.65), inset 0 1px 0 rgba(255,255,255,0.05);
  transform: perspective(900px) rotateX(0deg); transform-style: preserve-3d;
  transition: transform .25s ease, box-shadow .25s ease;
}
.lcn-metric:hover { transform: perspective(900px) translateY(-3px) rotateX(4deg);
  box-shadow: 0 26px 42px -18px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.07); }
.lcn-metric .v { font-family:'Space Grotesk'; font-size: 2.1rem; font-weight: 700; color: #fff; line-height: 1; }
.lcn-metric .k { font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: var(--muted); margin-top: .45rem; }
.lcn-metric .bar { height: 3px; width: 38px; border-radius: 3px; margin-top: .7rem; background: var(--steel); }
.lcn-metric.is-ember .v { color: #fff; }
.lcn-metric.is-ember .bar { background: var(--ember); }
.lcn-metric.is-ember { box-shadow: 0 18px 30px -16px rgba(0,0,0,0.65), 0 0 0 1px rgba(194,73,90,0.35), inset 0 1px 0 rgba(255,255,255,0.05); }

/* --- OOO cards (signature 3D element) --- */
.lcn-cardgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(255px, 1fr)); gap: 16px; }
.lcn-card {
  position: relative; border: 1px solid var(--line); border-radius: 16px;
  background: linear-gradient(160deg, var(--panel-2) 0%, var(--panel) 100%);
  padding: 1.05rem 1.15rem 1.1rem 1.25rem; border-left: 4px solid var(--steel);
  box-shadow: 0 20px 34px -16px rgba(0,0,0,0.62), inset 0 1px 0 rgba(255,255,255,0.05);
  transform: perspective(950px) rotateX(0deg); transform-style: preserve-3d;
  transition: transform .28s cubic-bezier(.2,.7,.2,1), box-shadow .28s ease;
}
.lcn-card:hover { transform: perspective(950px) translateY(-5px) rotateX(4deg) scale(1.012);
  box-shadow: 0 32px 50px -18px rgba(0,0,0,0.7), inset 0 1px 0 rgba(255,255,255,0.08); }
.lcn-card.is-today { border-left-color: var(--ember);
  box-shadow: 0 20px 34px -16px rgba(0,0,0,0.62), 0 0 0 1px rgba(194,73,90,0.3), inset 0 1px 0 rgba(255,255,255,0.05); }
.lcn-card .name { font-family:'Space Grotesk'; font-weight: 700; font-size: 1.18rem; color: #fff; }
.lcn-card .pill {
  display: inline-flex; align-items: center; gap: .35rem; margin-top: .5rem;
  font-size: .7rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 600;
  padding: .22rem .55rem; border-radius: 999px; background: var(--steel-soft); color: var(--steel);
}
.lcn-card.is-today .pill { background: var(--ember-soft); color: #E78A95; }
.lcn-card .dates { color: var(--paper); font-size: .92rem; margin-top: .6rem; }
.lcn-card .dates b { font-family:'Space Grotesk'; font-weight: 600; }
.lcn-card .meta { color: var(--muted); font-size: .85rem; margin-top: .35rem; }
.lcn-card .note { color: var(--paper); font-size: .85rem; margin-top: .5rem; padding-top: .5rem; border-top: 1px dashed var(--line); font-style: italic; }
.lcn-count { color: var(--steel); font-family:'Space Grotesk'; font-weight: 600; }

/* --- Calendar --- */
.cal-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 8px; margin-top: 12px; }
.cal-head { text-align: center; font-family:'Space Grotesk'; font-weight: 600; color: var(--muted);
  padding: 6px 4px; font-size: .72rem; text-transform: uppercase; letter-spacing: .12em; }
.cal-day {
  background: linear-gradient(160deg, var(--panel-2), var(--panel)); border: 1px solid var(--line);
  border-radius: 12px; padding: 8px; min-height: 96px; color: var(--paper); font-size: .85rem;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04), 0 10px 18px -12px rgba(0,0,0,0.55);
}
.cal-empty { background: transparent; border: 1px solid transparent; box-shadow: none; }
.cal-weekend { background: linear-gradient(160deg, #131D29, #0F1822); }
.cal-has { border-color: rgba(122,160,203,0.5); }
.cal-today { border: 1px solid var(--ember); box-shadow: 0 0 0 1px rgba(194,73,90,0.4), 0 12px 22px -12px rgba(0,0,0,0.6); }
.cal-num { font-family:'Space Grotesk'; font-weight: 600; font-size: .9rem; color: #fff; margin-bottom: 5px; }
.cal-today .cal-num { color: #E78A95; }
.cal-person { display:block; background: #0F1A26; border-left: 3px solid var(--steel); border-radius: 6px;
  padding: 2px 6px; margin: 3px 0; font-size: .72rem; color: var(--paper);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* --- Streamlit widget tuning --- */
.stButton>button { border-radius: 10px; font-weight: 600; border: 1px solid var(--line); background: var(--panel-2); color: var(--paper); }
.stButton>button:hover { border-color: var(--steel); color: #fff; }
[data-testid="stExpander"] { border: 1px solid var(--line); border-radius: 12px; background: var(--panel); }
[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 12px; }
hr { border-color: var(--line); }
.lcn-status { font-size: .8rem; border-radius: 10px; padding: .55rem .7rem; border: 1px solid var(--line); margin-top: .25rem; }
.lcn-status.ok { background: var(--steel-soft); border-color: rgba(122,160,203,0.4); }
.lcn-status.warn { background: var(--ember-soft); border-color: rgba(194,73,90,0.4); }

@media (max-width: 760px) {
  .lcn-metrics { grid-template-columns: repeat(2, 1fr); }
  .lcn-title { font-size: 1.7rem; }
}
@media (prefers-reduced-motion: reduce) {
  .lcn-card, .lcn-metric, .lcn-logo-plate { transition: none; }
  .lcn-card:hover, .lcn-metric:hover, .lcn-logo-plate:hover { transform: none; }
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Storage layer  —  Google Sheets when configured, else local CSV
# ---------------------------------------------------------------------------
def gsheets_configured() -> bool:
    try:
        return "connections" in st.secrets and "gsheets" in st.secrets["connections"]
    except Exception:
        return False


def _conn():
    from streamlit_gsheets import GSheetsConnection
    return st.connection("gsheets", type=GSheetsConnection)


def _read_raw() -> pd.DataFrame:
    """Return the stored rows as a DataFrame with the expected columns."""
    if gsheets_configured():
        try:
            df = _conn().read(worksheet=WORKSHEET, ttl=0)
            st.session_state["_store_error"] = None
        except Exception as exc:  # worksheet missing on first run, or auth issue
            st.session_state["_store_error"] = str(exc)
            return pd.DataFrame(columns=COLUMNS)
        df = df.dropna(how="all")
        for col in COLUMNS:
            if col not in df.columns:
                df[col] = pd.NA
        return df[COLUMNS]

    # Local CSV fallback
    if not os.path.exists(DATA_FILE):
        empty = pd.DataFrame(columns=COLUMNS)
        empty.to_csv(DATA_FILE, index=False)
        return empty
    return pd.read_csv(DATA_FILE)


def _write_raw(df: pd.DataFrame) -> None:
    """Persist the DataFrame. Dates are stored as ISO strings."""
    out = df.reindex(columns=COLUMNS).copy()
    for col in ("start_date", "end_date"):
        out[col] = pd.to_datetime(out[col], errors="coerce").dt.strftime("%Y-%m-%d")
    out["note"] = out["note"].fillna("").astype(str)
    out["id"] = pd.to_numeric(out["id"], errors="coerce").fillna(0).astype(int)

    if gsheets_configured():
        _conn().update(worksheet=WORKSHEET, data=out)
    else:
        out.to_csv(DATA_FILE, index=False)


def load_data() -> pd.DataFrame:
    """Load, clean, repair ids, and auto-purge entries whose end date has passed."""
    df = _read_raw()
    if df is None or df.empty:
        return pd.DataFrame(columns=COLUMNS)

    df = df[df["name"].notna() & (df["name"].astype(str).str.strip() != "")].copy()
    if df.empty:
        return pd.DataFrame(columns=COLUMNS)

    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce").dt.date
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce").dt.date
    df = df.dropna(subset=["start_date", "end_date"]).reset_index(drop=True)
    df["note"] = df["note"].fillna("").astype(str)

    # Repair ids if missing or duplicated so edit/delete always target one row.
    ids = pd.to_numeric(df["id"], errors="coerce")
    if ids.isna().any() or ids.duplicated().any():
        df["id"] = range(1, len(df) + 1)
        needs_write = True
    else:
        df["id"] = ids.astype(int)
        needs_write = False

    # Auto-purge: drop entries that ended before today.
    today = date.today()
    before = len(df)
    df = df[df["end_date"] >= today].reset_index(drop=True)
    if needs_write or len(df) < before:
        _write_raw(df)

    return df


def add_entry(name, start, end, reason, note) -> None:
    df = load_data()
    new_id = int(df["id"].max()) + 1 if not df.empty else 1
    row = pd.DataFrame([{
        "id": new_id, "name": name.strip(), "start_date": start,
        "end_date": end, "reason": reason, "note": (note or "").strip(),
    }])
    _write_raw(pd.concat([df, row], ignore_index=True))


def delete_entry(entry_id: int) -> None:
    df = load_data()
    _write_raw(df[df["id"] != entry_id].reset_index(drop=True))


def update_entry(entry_id, name, start, end, reason, note) -> None:
    df = load_data()
    mask = df["id"] == entry_id
    if not mask.any():
        return
    df.loc[mask, ["name", "start_date", "end_date", "reason", "note"]] = [
        name.strip(), start, end, reason, (note or "").strip(),
    ]
    _write_raw(df)


# ---------------------------------------------------------------------------
# Small render helpers
# ---------------------------------------------------------------------------
def card_html(row, today, kind: str) -> str:
    glyph = reason_glyph(row["reason"])
    is_today = kind == "today"
    klass = "lcn-card is-today" if is_today else "lcn-card"

    if is_today:
        days_left = (row["end_date"] - today).days
        meta = "Back tomorrow" if days_left == 0 else f"{days_left} day{'s' if days_left != 1 else ''} remaining"
    else:
        days_until = (row["start_date"] - today).days
        meta = "Starts tomorrow" if days_until == 1 else f"Starts in {days_until} days"

    note = str(row["note"]).strip()
    note_html = f'<div class="note">{note}</div>' if note else ""
    span = f'{row["start_date"].strftime("%b %d")} &rarr; {row["end_date"].strftime("%b %d, %Y")}'

    return (
        f'<div class="{klass}">'
        f'<div class="name">{row["name"]}</div>'
        f'<span class="pill">{glyph} {row["reason"]}</span>'
        f'<div class="dates"><b>{span}</b></div>'
        f'<div class="meta">{meta}</div>'
        f'{note_html}'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
logo = logo_data_uri()
logo_block = (
    f'<div class="lcn-logo-plate"><img src="{logo}" alt="LCN Consulting"/></div>'
    if logo else ""
)
st.markdown(
    f'''
    <div class="lcn-hero">
      <div class="lcn-hero-row">
        {logo_block}
        <div class="lcn-hero-text">
          <div class="lcn-eyebrow">Team Availability</div>
          <h1 class="lcn-title">Out of Office</h1>
          <div class="lcn-sub">Who&rsquo;s away, when they&rsquo;re back, and why &mdash; at a glance.</div>
        </div>
      </div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar: Add entry + storage status
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Add time off")
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("Name", placeholder="e.g. Alex Johnson")
        c1, c2 = st.columns(2)
        with c1:
            start = st.date_input("Start date", value=date.today())
        with c2:
            end = st.date_input("End date", value=date.today())
        reason = st.selectbox("Reason", REASON_OPTIONS)
        note = st.text_area("Note (optional)", placeholder="Back Monday", height=80)
        submitted = st.form_submit_button("Add entry", width="stretch", type="primary")

        if submitted:
            if not name.strip():
                st.error("Enter a name to add an entry.")
            elif end < start:
                st.error("End date can't be before the start date.")
            else:
                try:
                    add_entry(name, start, end, reason, note)
                    st.success(f"Added {name.strip()} — {reason.lower()}.")
                    st.rerun()
                except Exception as exc:
                    st.error(f"Couldn't save the entry. {exc}")

    st.divider()

    # Storage status — tells you whether the saving fix is active.
    if gsheets_configured():
        err = st.session_state.get("_store_error")
        if err:
            st.markdown(
                f'<div class="lcn-status warn">⚠️ Google Sheets is configured but the '
                f'connection failed. Check the sheet is shared with the service account '
                f'and that the worksheet is named <b>{WORKSHEET}</b>.</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="lcn-status ok">🟢 Synced to Google Sheets. '
                'Entries are saved and shared across everyone.</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="lcn-status warn">⚠️ Using a local file. Entries will '
            '<b>not</b> persist on Streamlit Cloud. Connect Google Sheets for shared, '
            'permanent storage — see the README.</div>',
            unsafe_allow_html=True,
        )

    st.caption("Entries are removed automatically the day after they end.")

# ---------------------------------------------------------------------------
# Data + metrics
# ---------------------------------------------------------------------------
df = load_data()
today = date.today()

if df.empty:
    out_today = upcoming = total = 0
else:
    out_today = int(df[(df["start_date"] <= today) & (df["end_date"] >= today)].shape[0])
    upcoming = int(df[df["start_date"] > today].shape[0])
    total = int(df.shape[0])

st.markdown(
    f'''
    <div class="lcn-metrics">
      <div class="lcn-metric is-ember"><div class="v">{out_today}</div><div class="k">Out today</div><div class="bar"></div></div>
      <div class="lcn-metric"><div class="v">{upcoming}</div><div class="k">Upcoming</div><div class="bar"></div></div>
      <div class="lcn-metric"><div class="v">{total}</div><div class="k">Total entries</div><div class="bar"></div></div>
      <div class="lcn-metric"><div class="v">{today.strftime("%b %d")}</div><div class="k">{today.strftime("%A")}</div><div class="bar"></div></div>
    </div>
    ''',
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Tabs
# ---------------------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Overview", "All entries", "Calendar"])

# ---- Tab 1: Overview ----
with tab1:
    if df.empty:
        st.info("No entries yet. Add time off from the sidebar to get started.")
    else:
        ordered = df.sort_values("start_date").reset_index(drop=True)

        out_now = ordered[(ordered["start_date"] <= today) & (ordered["end_date"] >= today)]
        st.markdown(f"### Out today &nbsp;<span class='lcn-count'>{len(out_now)}</span>", unsafe_allow_html=True)
        if out_now.empty:
            st.success("Full house — everyone's in today.")
        else:
            cards = "".join(card_html(r, today, "today") for _, r in out_now.iterrows())
            st.markdown(f'<div class="lcn-cardgrid">{cards}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        upcoming_df = ordered[ordered["start_date"] > today].head(9)
        st.markdown(f"### Coming up &nbsp;<span class='lcn-count'>{len(upcoming_df)}</span>", unsafe_allow_html=True)
        if upcoming_df.empty:
            st.info("Nothing on the schedule yet.")
        else:
            cards = "".join(card_html(r, today, "upcoming") for _, r in upcoming_df.iterrows())
            st.markdown(f'<div class="lcn-cardgrid">{cards}</div>', unsafe_allow_html=True)

# ---- Tab 2: All entries ----
with tab2:
    if df.empty:
        st.info("Nothing to show yet. Add an entry from the sidebar.")
    else:
        display = df.copy().sort_values("start_date").reset_index(drop=True)

        overview = display.copy()
        overview["Status"] = overview.apply(
            lambda r: "Out now" if r["start_date"] <= today <= r["end_date"]
            else ("Upcoming" if r["start_date"] > today else "Past"),
            axis=1,
        )
        overview["Reason"] = overview["reason"].apply(lambda r: f"{reason_glyph(r)} {r}")
        overview = overview.rename(columns={"name": "Name", "start_date": "Start", "end_date": "End", "note": "Note"})
        st.dataframe(
            overview[["Name", "Reason", "Start", "End", "Status", "Note"]],
            width="stretch", hide_index=True,
        )

        st.markdown("#### Edit entries")
        st.caption("Open an entry to change or remove it. Changes save right away.")

        for _, row in display.iterrows():
            entry_id = int(row["id"])
            status = ("Out now" if row["start_date"] <= today <= row["end_date"]
                      else ("Upcoming" if row["start_date"] > today else "Past"))
            label = (f"{row['name']} · {row['reason']} · "
                     f"{row['start_date'].strftime('%b %d')} → {row['end_date'].strftime('%b %d')}  ({status})")

            with st.expander(label):
                with st.form(f"edit_{entry_id}"):
                    e1, e2 = st.columns(2)
                    with e1:
                        new_name = st.text_input("Name", value=row["name"], key=f"n_{entry_id}")
                        new_start = st.date_input("Start date", value=row["start_date"], key=f"s_{entry_id}")
                        new_reason = st.selectbox(
                            "Reason", REASON_OPTIONS,
                            index=REASON_OPTIONS.index(row["reason"]) if row["reason"] in REASON_OPTIONS else 0,
                            key=f"r_{entry_id}",
                        )
                    with e2:
                        new_end = st.date_input("End date", value=row["end_date"], key=f"e_{entry_id}")
                        new_note = st.text_area("Note", value=str(row["note"]), key=f"nt_{entry_id}", height=100)

                    sc, dc = st.columns(2)
                    with sc:
                        save_clicked = st.form_submit_button("Save changes", width="stretch", type="primary")
                    with dc:
                        delete_clicked = st.form_submit_button("Delete entry", width="stretch")

                    if save_clicked:
                        if not new_name.strip():
                            st.error("Name can't be empty.")
                        elif new_end < new_start:
                            st.error("End date can't be before the start date.")
                        else:
                            try:
                                update_entry(entry_id, new_name, new_start, new_end, new_reason, new_note)
                                st.success("Saved.")
                                st.rerun()
                            except Exception as exc:
                                st.error(f"Couldn't save changes. {exc}")
                    if delete_clicked:
                        try:
                            delete_entry(entry_id)
                            st.success("Entry removed.")
                            st.rerun()
                        except Exception as exc:
                            st.error(f"Couldn't delete the entry. {exc}")

# ---- Tab 3: Calendar ----
with tab3:
    if df.empty:
        st.info("No entries yet — the calendar's wide open.")
    else:
        if "cal_year" not in st.session_state:
            st.session_state.cal_year = today.year
        if "cal_month" not in st.session_state:
            st.session_state.cal_month = today.month

        def shift_month(delta: int) -> None:
            m = st.session_state.cal_month + delta
            y = st.session_state.cal_year
            while m < 1:
                m += 12; y -= 1
            while m > 12:
                m -= 12; y += 1
            st.session_state.cal_year, st.session_state.cal_month = y, m

        nav_l, nav_c, nav_r = st.columns([1, 3, 1])
        with nav_l:
            if st.button("◀ Prev", width="stretch"):
                shift_month(-1); st.rerun()
        with nav_c:
            month_name = calendar.month_name[st.session_state.cal_month]
            st.markdown(
                f"<h3 style='text-align:center;margin:.2rem 0;'>{month_name} {st.session_state.cal_year}</h3>",
                unsafe_allow_html=True,
            )
        with nav_r:
            if st.button("Next ▶", width="stretch"):
                shift_month(1); st.rerun()

        if st.button("Jump to today"):
            st.session_state.cal_year, st.session_state.cal_month = today.year, today.month
            st.rerun()

        cal = calendar.Calendar(firstweekday=6)  # Sunday first
        weeks = cal.monthdatescalendar(st.session_state.cal_year, st.session_state.cal_month)
        cur_month = st.session_state.cal_month

        heads = "".join(f'<div class="cal-head">{d}</div>'
                        for d in ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"])

        cells = ""
        for week in weeks:
            for day in week:
                if day.month != cur_month:
                    cells += '<div class="cal-day cal-empty"></div>'
                    continue
                out_on = df[(df["start_date"] <= day) & (df["end_date"] >= day)]
                classes = ["cal-day"]
                if day == today:
                    classes.append("cal-today")
                elif len(out_on) > 0:
                    classes.append("cal-has")
                elif day.weekday() >= 5:
                    classes.append("cal-weekend")
                people = "".join(
                    f'<span class="cal-person">{reason_glyph(r["reason"])} {r["name"]}</span>'
                    for _, r in out_on.iterrows()
                )
                cells += (f'<div class="{" ".join(classes)}">'
                          f'<div class="cal-num">{day.day}</div>{people}</div>')

        st.markdown(f'<div class="cal-grid">{heads}{cells}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Ember ring = today · blue outline = someone's out · use Prev / Next to change months.")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.divider()
st.caption(
    f"LCN Consulting · Out of Office · refreshed {datetime.now().strftime('%b %d, %Y at %I:%M %p')}"
)
