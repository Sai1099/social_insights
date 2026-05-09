import csv
import io
import json
import os
import re
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse
import dotenv
dotenv.load_dotenv()

VM_API_URL = os.getenv("VM_API_URL", "")
VM_API_KEY = os.getenv("VM_API_KEY", "")

st.set_page_config(
    page_title="Social Insights",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #0a0a0a; }
[data-testid="stSidebar"] {
    background: #0f0f0f;
    border-right: 1px solid #1c1c1c;
}
section.main > div { padding-top: 1rem; }
.block-container { padding: 1.5rem 2.5rem 2rem 2.5rem; }
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* Sidebar text */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label { color: #aaa !important; font-size: 0.82rem !important; }

/* Nav card */
.nav-card {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 14px;
    border-radius: 10px;
    border: 1px solid transparent;
    margin-bottom: 6px;
    cursor: pointer;
    font-size: 0.85rem;
    font-weight: 500;
    color: #aaa;
    background: transparent;
    transition: all 0.15s;
    text-decoration: none;
}
.nav-card:hover { background: #181818; border-color: #242424; color: #fff; }
.nav-card.active {
    background: #1a1a1a;
    border-color: #2a2a2a;
    color: #fff;
}
.nav-icon { font-size: 1rem; width: 22px; text-align: center; }

/* Sidebar post item */
.sb-item {
    padding: 10px 12px;
    border-radius: 8px;
    background: #141414;
    border: 1px solid #1c1c1c;
    margin-bottom: 6px;
}
.sb-item-text { font-size: 0.78rem; color: #bbb; line-height: 1.45; }
.sb-item-ts   { font-size: 0.7rem;  color: #444; margin-top: 4px; }

/* Divider */
.sb-divider { border-top: 1px solid #1c1c1c; margin: 14px 0 10px 0; }

/* Main page header */
.page-title { font-size: 1.6rem; font-weight: 700; color: #f0f0f0; margin: 0; }
.page-sub   { font-size: 0.8rem; color: #444; margin-top: 2px; }

/* Post card */
.post-card {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 14px;
    padding: 20px 22px;
    margin-bottom: 28px;
}

/* Tweet bubble */
.tweet-bubble {
    background: #0a0a0a;
    border-left: 3px solid #1d9bf0;
    border-radius: 0 8px 8px 0;
    padding: 14px 18px;
    margin: 8px 0;
    font-size: 1.08rem;
    font-weight: 600;
    line-height: 1.7;
    color: #f0f0f0;
    white-space: pre-wrap;
    letter-spacing: 0.01em;
}

/* Thread index */
.thread-idx {
    font-size: 0.68rem;
    color: #444;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-top: 10px;
    margin-bottom: 1px;
}

/* Meta row */
.meta-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-top: 12px;
    flex-wrap: wrap;
}
.meta-item { font-size: 0.75rem; color: #444; }
.meta-link { font-size: 0.75rem; color: #1d9bf0; text-decoration: none; }
.meta-link:hover { text-decoration: underline; }

/* Chips */
.chip {
    display: inline-block;
    background: #181818;
    border: 1px solid #262626;
    border-radius: 6px;
    padding: 2px 8px;
    font-size: 0.72rem;
    color: #777;
    margin: 2px 3px 2px 0;
}
.chip-green {
    background: #0c1f13;
    border-color: #1a3a24;
    color: #4ade80;
    font-family: monospace;
}

/* Source + article reference grid */
.ref-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 6px;
}
@media (max-width: 700px) { .ref-grid { grid-template-columns: 1fr; } }

.ref-col-label {
    font-size: 0.65rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #2a2a2a;
    margin-bottom: 5px;
    font-weight: 600;
}

/* X source row */
.src-row {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    padding: 8px 10px;
    background: #0d1117;
    border: 1px solid #1a2030;
    border-radius: 7px;
    margin-bottom: 5px;
}
.src-avatar {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #1d9bf022;
    border: 1px solid #1d9bf033;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    color: #1d9bf0;
    font-weight: 700;
    flex-shrink: 0;
}
.src-body { flex: 1; min-width: 0; }
.src-handle {
    font-size: 0.78rem;
    font-weight: 600;
    color: #1d9bf0;
    text-decoration: none;
}
.src-handle:hover { text-decoration: underline; }
.src-meta {
    font-size: 0.68rem;
    color: #2a3a4a;
    margin-top: 2px;
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    align-items: center;
}
.src-tweet-link {
    font-size: 0.68rem;
    color: #1a4060;
    text-decoration: none;
}
.src-tweet-link:hover { color: #1d9bf0; text-decoration: underline; }
.src-unavail { font-size: 0.7rem; color: #1e2a1e; font-style: italic; }

/* Article card */
.art-card {
    background: #0d1218;
    border: 1px solid #1a2535;
    border-radius: 7px;
    padding: 8px 12px;
    margin-bottom: 5px;
}
.art-card-title {
    font-size: 0.78rem;
    color: #5ba3d9;
    text-decoration: none;
    font-weight: 500;
    line-height: 1.4;
    display: block;
}
.art-card-title:hover { color: #1d9bf0; text-decoration: underline; }
.art-card-meta {
    font-size: 0.68rem;
    color: #1f3040;
    margin-top: 3px;
    display: flex;
    gap: 6px;
    align-items: center;
}
.art-domain { font-family: monospace; color: #1a3a52; }
.art-unavail { font-size: 0.7rem; color: #1e2a1e; font-style: italic; padding: 8px 0; }

/* Section row label */
.row-label {
    font-size: 0.68rem;
    color: #333;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    margin: 10px 0 4px 0;
}

/* Engagement stat card */
.eg-card {
    background: #111;
    border: 1px solid #1e1e1e;
    border-radius: 14px;
    padding: 24px 22px;
    text-align: center;
}
.eg-card-val  { font-size: 2rem; font-weight: 700; color: #f0f0f0; }
.eg-card-label{ font-size: 0.75rem; color: #444; margin-top: 4px; letter-spacing: 0.05em; text-transform: uppercase; }

/* Inline engagement row on post cards */
.eng-row { display: flex; gap: 18px; margin-top: 12px; flex-wrap: wrap; }
.eng-stat { font-size: 0.82rem; color: #555; }
.eng-stat span { color: #ccc; font-weight: 600; margin-left: 4px; }

/* Welcome */
.welcome-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 60vh;
    text-align: center;
}
.welcome-flower { font-size: 4rem; margin-bottom: 20px; }
.welcome-title  { font-size: 1.8rem; font-weight: 700; color: #f0f0f0; margin-bottom: 10px; }
.welcome-sub    { font-size: 0.95rem; color: #444; max-width: 420px; line-height: 1.6; }

/* Input overrides */
.stTextInput > div > div { background: #141414 !important; border-color: #222 !important; color: #ccc !important; }
.stSelectbox > div > div { background: #141414 !important; border-color: #222 !important; }
div[data-baseweb="select"] { background: #141414 !important; }
</style>
""", unsafe_allow_html=True)

CSV_PATH = Path(__file__).parent / "posted_tweets.csv"


def _fetch_csv_raw() -> str:
    """Fetch CSV from Oracle VM API; fall back to local file."""
    if VM_API_URL and VM_API_KEY:
        try:
            import requests as _req
            resp = _req.get(
                f"{VM_API_URL}/data",
                headers={"X-API-Key": VM_API_KEY},
                timeout=15,
            )
            resp.raise_for_status()
            return resp.text
        except Exception:
            pass
    # Local fallback
    if CSV_PATH.exists():
        return CSV_PATH.read_text(encoding="utf-8")
    return ""


@st.cache_data(ttl=30)
def load_data():
    raw = _fetch_csv_raw()
    if not raw:
        return pd.DataFrame()
    all_rows = list(csv.reader(io.StringIO(raw)))
    if not all_rows:
        return pd.DataFrame()

    header = all_rows[0]

    # The CSV accumulated rows from multiple pipeline versions with incompatible
    # column orderings.  Rather than per-version heuristics, we use a single
    # scan-based recovery for every row that is longer than the 31-column header:
    #   1. Scan positions 5-25 for the first value that looks like a Twitter handle.
    #   2. Read src blocks of 7 fields from there (handle, original_date, category,
    #      likes, views, text, summary) until a non-handle is encountered.
    #   3. For formats where our_* metrics sit immediately before the src block
    #      (handle_pos >= 17), read them from (handle_pos-5)..(handle_pos-1).
    # Tweet-text correction (is_thread leaked to pos 2) is handled separately.

    _HANDLE_RE_SCAN  = re.compile(r'^[A-Za-z][A-Za-z0-9_]{2,49}$')
    _BAD_SCAN        = frozenset({"true", "false", "none", "nan", "null", ""})
    _CAT_SCAN        = frozenset({"stock_specific", "news_event", "market_general", "other"})
    _SRC_FIELDS      = ("handle", "original_date", "category", "likes", "views", "text", "summary")

    def _find_src_start(rr):
        """Return index of first valid Twitter handle in rr, scanning positions 5-25.
        Requires position +2 to be a known category to avoid false positives in
        content fields (yf_prices, article_summary, etc.) that happen to look like handles."""
        for i in range(5, min(len(rr) - 2, 26)):
            v = rr[i].strip()
            if (v
                    and not v.isdigit()
                    and _HANDLE_RE_SCAN.match(v)
                    and v.lower() not in _BAD_SCAN
                    and v not in _CAT_SCAN
                    and rr[i + 2].strip() in _CAT_SCAN):
                return i
        return None

    records = []
    for raw_row in all_rows[1:]:
        if not raw_row:
            continue
        rec = dict(zip(header, raw_row))

        # Fix tweet_text when is_thread leaked into position 2 (Type-A rows)
        if rec.get("tweet_text", "") in ("True", "False", "true", "false") and len(raw_row) > 4:
            rec["tweet_text"] = raw_row[4]
            for _mc in ("our_likes", "our_views", "our_replies", "our_retweets", "our_quotes"):
                rec[_mc] = "0"

        # Recover src handles for any row wider than the 31-col header
        if len(raw_row) > 31:
            _src_pos = _find_src_start(raw_row)
            if _src_pos is not None:
                # Clear all src slots so dict(zip) garbage doesn't survive
                for _si in range(1, 9):
                    for _f in _SRC_FIELDS:
                        rec[f"src{_si}_{_f}"] = ""
                # In formats where our_* precede the src block (handle_pos >= 17),
                # dict(zip) maps the wrong raw positions → fix them now.
                # Also fix when dict(zip) gave a non-numeric value (leaked date etc.)
                _ov_zip = str(rec.get("our_views", "")).strip()
                _ov_zip_bad = not _ov_zip.isdigit()
                _om = _src_pos - 5
                if (_src_pos >= 17 or _ov_zip_bad) and _om >= 0:
                    _cand_views = raw_row[_om + 1] if _om + 1 < len(raw_row) else ""
                    # Sanity-check: only override if candidate is numeric or we're in
                    # a known new-format layout (src_pos >= 17)
                    if _src_pos >= 17 or _cand_views.strip().isdigit():
                        rec["our_likes"]    = raw_row[_om]     if _om     < len(raw_row) else "0"
                        rec["our_views"]    = _cand_views
                        rec["our_replies"]  = raw_row[_om + 2] if _om + 2 < len(raw_row) else "0"
                        rec["our_retweets"] = raw_row[_om + 3] if _om + 3 < len(raw_row) else "0"
                        rec["our_quotes"]   = raw_row[_om + 4] if _om + 4 < len(raw_row) else "0"
                # Recover src blocks (7 fields each)
                for _si in range(1, 9):
                    _base = _src_pos + (_si - 1) * 7
                    if _base >= len(raw_row):
                        break
                    _h = raw_row[_base].strip()
                    if not _h or _h.startswith("http"):
                        break
                    rec[f"src{_si}_handle"]        = _h
                    rec[f"src{_si}_original_date"] = raw_row[_base + 1] if _base + 1 < len(raw_row) else ""
                    rec[f"src{_si}_category"]      = raw_row[_base + 2] if _base + 2 < len(raw_row) else ""
                    rec[f"src{_si}_likes"]         = raw_row[_base + 3] if _base + 3 < len(raw_row) else ""
                    rec[f"src{_si}_views"]         = raw_row[_base + 4] if _base + 4 < len(raw_row) else ""
                    rec[f"src{_si}_text"]          = raw_row[_base + 5] if _base + 5 < len(raw_row) else ""
                    rec[f"src{_si}_summary"]       = raw_row[_base + 6] if _base + 6 < len(raw_row) else ""

        records.append(rec)

    if not records:
        return pd.DataFrame()

    df = pd.DataFrame(records)
    df["posted_at"] = pd.to_datetime(df.get("posted_at", ""), errors="coerce")
    df["char_count"] = pd.to_numeric(df.get("char_count", pd.Series(dtype=str)), errors="coerce")

    # Derive thread_count from tweet_text — avoids any NaN-to-int errors
    df["thread_count"] = df["tweet_text"].apply(
        lambda t: len([x for x in str(t).split(" || ") if x.strip()]) if pd.notna(t) else 1
    )

    _handle_re = re.compile(r'^[A-Za-z0-9_]{3,50}$')
    _bad_handles = frozenset({"true", "false", "none", "nan", "null", ""})
    def _valid_handle(h):
        h = str(h).strip()
        if not _handle_re.match(h):
            return ""
        if h.lower() in _bad_handles:
            return ""
        if h.isdigit():
            return ""
        # Category strings are all-lowercase with underscores (e.g. "news_event")
        if "_" in h and h == h.lower():
            return ""
        return h
    for i in range(1, 9):
        h_col = f"src{i}_handle"
        if h_col in df.columns:
            df[h_col] = df[h_col].apply(_valid_handle)
        for col in [f"src{i}_likes", f"src{i}_views"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    if "articles_fetched" in df.columns:
        df["articles_fetched"] = pd.to_numeric(df["articles_fetched"], errors="coerce").fillna(0).astype(int)
    else:
        df["articles_fetched"] = 0

    for col in ("our_likes", "our_views", "our_replies", "our_retweets", "our_quotes", "our_followers"):
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
        else:
            df[col] = 0

    return df.sort_values("posted_at", ascending=False).reset_index(drop=True)


def _get_followers(df: pd.DataFrame) -> int | None:
    """Read follower count from the most recent row that has our_followers > 0.
    Falls back to a live twikit fetch if the column is absent or all zeros."""
    if not df.empty and "our_followers" in df.columns:
        val = df.loc[df["our_followers"] > 0, "our_followers"]
        if not val.empty:
            return int(val.iloc[0])   # df is already sorted newest-first
    # Fallback: live fetch via twikit
    try:
        import asyncio
        from twikit import Client as _TC
        cookies_path = Path(__file__).parent / "cookies.json"
        if not cookies_path.exists():
            return None
        async def _get():
            c = _TC("en-US")
            c.load_cookies(str(cookies_path))
            me = await c.get_user_by_screen_name(
                os.getenv("X_USERNAME", "FiDecoded")
            )
            return me.followers_count
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(_get())
        finally:
            loop.close()
    except Exception:
        return None


def fmt_ts(dt):
    if pd.isna(dt):
        return "—"
    now = datetime.now()
    diff = now - dt.to_pydatetime().replace(tzinfo=None)
    if diff < timedelta(minutes=1):
        return "just now"
    if diff < timedelta(hours=1):
        return f"{int(diff.seconds // 60)}m ago"
    if diff < timedelta(days=1):
        return f"{int(diff.seconds // 3600)}h ago"
    if diff < timedelta(days=7):
        return f"{diff.days}d ago"
    return dt.strftime("%d %b %Y · %H:%M")


df = load_data()

# ── Session state: active nav page ───────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div style='padding:8px 4px 4px 4px;font-size:1rem;font-weight:700;color:#f0f0f0'>Social Insights</div>", unsafe_allow_html=True)
    st.markdown("<div style='font-size:0.72rem;color:#333;padding-bottom:12px'>Social Media Manager</div>", unsafe_allow_html=True)

    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)

    # Navigation
    pages = [
        ("home",       "🏠", "Home"),
        ("posts",      "📝", "Posts"),
        ("engagement", "📊", "Engagement Metrics"),
        ("pipeline",   "⚙️", "Pipeline Log"),
    ]
    for key, icon, label in pages:
        active_cls = "active" if st.session_state.page == key else ""
        if st.button(
            f"{icon}  {label}",
            key=f"nav_{key}",
            use_container_width=True,
            type="primary" if st.session_state.page == key else "secondary",
        ):
            st.session_state.page = key
            st.rerun()

    st.markdown("<div class='sb-divider'></div>", unsafe_allow_html=True)

    # Post list (always visible below nav)
    if not df.empty:
        st.markdown("<div style='font-size:0.68rem;color:#333;text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px'>Recent Posts</div>", unsafe_allow_html=True)

        for _, row in df.head(15).iterrows():
            parts = [t.strip() for t in str(row.get("tweet_text", "")).split(" || ") if t.strip()]
            preview = parts[0][:80] + "…" if parts and len(parts[0]) > 80 else (parts[0] if parts else "—")
            ts = fmt_ts(row["posted_at"])
            n_t = int(row.get("thread_count", 1))
            thread_tag = f" · 🧵{n_t}" if n_t > 1 else ""
            st.markdown(
                f'<div class="sb-item">'
                f'<div class="sb-item-text">{preview}</div>'
                f'<div class="sb-item-ts">𝕏 · {ts}{thread_tag}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

# ── Main area: route by page ──────────────────────────────────────────────────
page = st.session_state.page

# ── HOME ──────────────────────────────────────────────────────────────────────
if page == "home":
    st.markdown('<p class="page-title">Social Insights</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">@FiDecoded · 𝕏 Twitter</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    followers = _get_followers(df)
    total_posts   = len(df) if not df.empty else 0
    total_views   = int(df["our_views"].sum()) if not df.empty else 0
    total_likes   = int(df["our_likes"].sum()) if not df.empty else 0
    total_engage  = int((df["our_likes"] + df["our_replies"] + df["our_retweets"]).sum()) if not df.empty else 0
    eng_rate      = f"{(total_engage / total_views * 100):.1f}%" if total_views > 0 else "—"
    follower_str  = f"{followers:,}" if followers is not None else "—"

    h1, h2, h3, h4, h5 = st.columns(5)
    for col, val, label, color in [
        (h1, follower_str,        "Followers",       "#1d9bf0"),
        (h2, f"{total_posts:,}",  "Total Posts",     "#f0f0f0"),
        (h3, f"{total_views:,}",  "Total Views",     "#f0f0f0"),
        (h4, f"{total_likes:,}",  "Total Likes",     "#f0f0f0"),
        (h5, eng_rate,            "Engagement Rate", "#4ade80"),
    ]:
        with col:
            st.markdown(
                f'<div class="eg-card">'
                f'<div class="eg-card-val" style="color:{color}">{val}</div>'
                f'<div class="eg-card-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # Top performing post by views
    if not df.empty and df["our_views"].max() > 0:
        top = df.loc[df["our_views"].idxmax()]
        parts = [t.strip() for t in str(top.get("tweet_text", "")).split(" || ") if t.strip()]
        ts_full = top["posted_at"].strftime("%d %b %Y · %H:%M") if pd.notna(top["posted_at"]) else "—"
        tweet_id = str(top.get("tweet_id", "")).strip()
        view_link = f'<a class="meta-link" href="https://x.com/i/web/status/{tweet_id}" target="_blank">View on X ↗</a>' if tweet_id and tweet_id != "nan" else ""
        o_views   = int(top.get("our_views",   0) or 0)
        o_likes   = int(top.get("our_likes",   0) or 0)
        o_replies = int(top.get("our_replies", 0) or 0)

        st.markdown('<p class="page-sub" style="font-size:0.8rem;color:#555;margin-bottom:8px;letter-spacing:.07em;text-transform:uppercase">🏆 Top Performing Post</p>', unsafe_allow_html=True)

        card = '<div class="post-card">'
        card += (
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">'
            f'<span style="font-size:0.78rem;color:#333;font-weight:600;letter-spacing:0.04em">𝕏 &nbsp;TWITTER</span>'
            f'<span style="display:flex;align-items:center;gap:14px">'
            f'<span style="background:#1a3a24;color:#4ade80;padding:2px 8px;border-radius:4px;font-size:.72rem;font-weight:700">👁 {o_views:,} views</span>'
            f'<span style="font-size:0.78rem;color:#333">{ts_full}</span>'
            f'{view_link}'
            f'</span>'
            f'</div>'
        )
        n_threads = len(parts)
        if n_threads > 1:
            card += f'<div style="font-size:0.7rem;color:#555;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px">🧵 Thread · {n_threads} tweets</div>'
        for i, part in enumerate(parts[:2]):
            if n_threads > 1:
                card += f'<div class="thread-idx">{i+1} / {n_threads}</div>'
            card += f'<div class="tweet-bubble">{part}</div>'
        if n_threads > 2:
            card += f'<div style="font-size:0.75rem;color:#444;margin-top:6px">+{n_threads-2} more tweets in thread</div>'
        card += (
            f'<div class="eng-row">'
            f'<span class="eng-stat">👁<span>{o_views:,}</span></span>'
            f'<span class="eng-stat">❤<span>{o_likes:,}</span></span>'
            f'<span class="eng-stat">💬<span>{o_replies:,}</span></span>'
            f'</div>'
        )
        card += '</div>'
        st.markdown(card, unsafe_allow_html=True)
    else:
        st.markdown(
            '<div style="text-align:center;padding:48px;color:#2a2a2a;font-size:0.9rem;'
            'border:1px dashed #1e1e1e;border-radius:14px">'
            'Engagement metrics will appear after the next pipeline run</div>',
            unsafe_allow_html=True,
        )

# ── POSTS ─────────────────────────────────────────────────────────────────────
elif page == "posts":
    top_row = st.columns([5, 1])
    with top_row[0]:
        st.markdown('<p class="page-title">Posts</p>', unsafe_allow_html=True)
    with top_row[1]:
        if st.button("↺ Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    # Filters inline under title
    f1, f2, f3 = st.columns([3, 2, 2])
    with f1:
        search_q = st.text_input("", placeholder="Search posts…", label_visibility="collapsed")
    with f2:
        date_filter = st.selectbox("", ["All time", "Today", "Last 7 days", "Last 30 days"], label_visibility="collapsed")
    with f3:
        model_opts = ["All models"] + sorted(df["ai_model"].dropna().unique().tolist()) if "ai_model" in df.columns else ["All models"]
        model_filter = st.selectbox("", model_opts, label_visibility="collapsed")

    filtered = df.copy()
    if search_q:
        filtered = filtered[filtered["tweet_text"].str.contains(search_q, case=False, na=False)]
    if date_filter == "Today":
        filtered = filtered[filtered["posted_at"].dt.date == datetime.now().date()]
    elif date_filter == "Last 7 days":
        filtered = filtered[filtered["posted_at"] >= datetime.now() - timedelta(days=7)]
    elif date_filter == "Last 30 days":
        filtered = filtered[filtered["posted_at"] >= datetime.now() - timedelta(days=30)]
    if model_filter != "All models" and "ai_model" in filtered.columns:
        filtered = filtered[filtered["ai_model"] == model_filter]
    filtered = filtered.reset_index(drop=True)

    st.markdown(f'<p class="page-sub">{len(filtered)} post{"s" if len(filtered) != 1 else ""} · 𝕏 Twitter</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    if filtered.empty:
        st.markdown('<div style="text-align:center;padding:80px;color:#2a2a2a;font-size:1rem;">No posts found</div>', unsafe_allow_html=True)
    else:
        for _, row in filtered.iterrows():
            parts = [t.strip() for t in str(row.get("tweet_text", "")).split(" || ") if t.strip()]
            if not parts:
                continue

            ts_full = row["posted_at"].strftime("%d %b %Y · %H:%M") if pd.notna(row["posted_at"]) else "—"
            ts_rel  = fmt_ts(row["posted_at"])
            n_threads = int(row.get("thread_count", 1))
            model_s  = str(row.get("ai_model", "")).split("/")[-1]
            tweet_id = str(row.get("tweet_id", "")).strip()
            view_link = f'<a class="meta-link" href="https://x.com/i/web/status/{tweet_id}" target="_blank">View on X ↗</a>' if tweet_id and tweet_id != "nan" else ""

            card = '<div class="post-card">'

            # Header: platform + timestamp + link
            card += (
                f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px">'
                f'<span style="font-size:0.78rem;color:#333;font-weight:600;letter-spacing:0.04em">𝕏 &nbsp;TWITTER</span>'
                f'<span style="display:flex;align-items:center;gap:14px">'
                f'<span style="font-size:0.78rem;color:#333" title="{ts_full}">{ts_rel}</span>'
                f'{view_link}'
                f'</span>'
                f'</div>'
            )

            # Thread label
            if n_threads > 1:
                card += f'<div style="font-size:0.7rem;color:#555;letter-spacing:0.05em;text-transform:uppercase;margin-bottom:4px">🧵 Thread · {n_threads} tweets</div>'

            # Tweet bubbles
            for i, part in enumerate(parts):
                if n_threads > 1:
                    card += f'<div class="thread-idx">{i+1} / {len(parts)}</div>'
                card += f'<div class="tweet-bubble">{part}</div>'

            # Engagement stats inline
            o_likes   = int(row.get("our_likes",   0) or 0)
            o_views   = int(row.get("our_views",   0) or 0)
            o_replies = int(row.get("our_replies", 0) or 0)
            card += (
                f'<div class="eng-row">'
                f'<span class="eng-stat">❤<span>{o_likes:,}</span></span>'
                f'<span class="eng-stat">👁<span>{o_views:,}</span></span>'
                f'<span class="eng-stat">💬<span>{o_replies:,}</span></span>'
                f'</div>'
            )

            # Meta row
            card += (
                f'<div class="meta-row">'
                f'<span class="meta-item">{ts_full}</span>'
                f'<span class="meta-item">·</span>'
                f'<span class="meta-item">via {model_s}</span>'
                f'</div>'
            )

            # ── Sources + Articles two-column reference block ────────────────
            # Collect unique X sources (deduplicated by handle)
            seen_src: dict = {}   # handle -> {tweet_id, views, likes}
            for i in range(1, 9):
                h = str(row.get(f"src{i}_handle", "")).strip()
                if not h or h in ("", "nan"):
                    continue
                sv  = int(row.get(f"src{i}_views", 0) or 0)
                sl  = int(row.get(f"src{i}_likes", 0) or 0)
                tid = str(row.get(f"src{i}_tweet_id", "")).strip()
                if h not in seen_src:
                    seen_src[h] = {"tid": tid, "views": sv, "likes": sl}
                else:
                    if sv > seen_src[h]["views"]:
                        seen_src[h] = {"tid": tid, "views": sv, "likes": sl}

            # Build X source rows HTML
            x_html = ""
            for h, info in seen_src.items():
                initials = h[:2].upper()
                profile_url = f"https://x.com/{h}"
                sv, sl = info["views"], info["likes"]
                tid = info["tid"]
                tweet_url = f"https://x.com/{h}/status/{tid}" if tid and tid not in ("", "nan") else ""
                stats = ""
                if sv > 0 or sl > 0:
                    stats = f'<span>{sv:,}👁</span><span>{sl:,}❤</span>'
                tweet_link = (
                    f'<a class="src-tweet-link" href="{tweet_url}" target="_blank">View post ↗</a>'
                    if tweet_url else
                    '<span class="src-tweet-link" style="color:#1a2a1a">Link unavailable</span>'
                )
                x_html += (
                    f'<div class="src-row">'
                    f'<div class="src-avatar">{initials}</div>'
                    f'<div class="src-body">'
                    f'<a class="src-handle" href="{profile_url}" target="_blank">@{h}</a>'
                    f'<div class="src-meta">{stats}{tweet_link}</div>'
                    f'</div></div>'
                )
            if not x_html:
                x_html = '<div class="src-unavail">X sources unavailable</div>'

            # Collect news articles
            n_art = int(row.get("articles_fetched", 0) or 0)
            art_html = ""
            for i in range(1, n_art + 1):
                url   = str(row.get(f"art{i}_url",   "")).strip()
                title = str(row.get(f"art{i}_title", "")).strip()
                date  = str(row.get(f"art{i}_date",  "")).strip()
                if not url or url in ("", "nan"):
                    continue
                domain = urlparse(url).netloc.lstrip("www.") or url[:40]
                display_title = (title[:80] + "…" if len(title) > 80 else title) if title and title != "nan" else domain
                date_str = ""
                if date and date not in ("", "nan"):
                    try:
                        _d = datetime.fromisoformat(date[:10])
                        date_str = f"{_d.day} {_d.strftime('%b %Y')}"
                    except Exception:
                        date_str = date[:10]
                meta = f'<span class="art-domain">{domain}</span>'
                if date_str:
                    meta += f'<span>·</span><span>{date_str}</span>'
                art_html += (
                    f'<div class="art-card">'
                    f'<a class="art-card-title" href="{url}" target="_blank">{display_title}</a>'
                    f'<div class="art-card-meta">{meta}</div>'
                    f'</div>'
                )
            if not art_html:
                art_html = '<div class="art-unavail">News articles unavailable</div>'

            card += (
                f'<div style="margin-top:14px">'
                f'<div class="ref-grid">'
                f'<div><div class="ref-col-label">𝕏 Sources</div>{x_html}</div>'
                f'<div><div class="ref-col-label">News Articles</div>{art_html}</div>'
                f'</div></div>'
            )

            # YF prices
            yf = str(row.get("yf_prices", "")).strip()
            if yf and yf not in ("", "nan"):
                prices = [p.strip() for p in yf.split("\n") if p.strip()]
                pills = "".join(f'<span class="chip chip-green">{p}</span>' for p in prices)
                card += f'<div class="row-label" style="margin-top:10px">Live prices used</div><div>{pills}</div>'

            card += '</div>'
            st.markdown(card, unsafe_allow_html=True)

# ── ENGAGEMENT METRICS ────────────────────────────────────────────────────────
elif page == "engagement":
    import altair as alt

    st.markdown('<p class="page-title">Engagement Metrics</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">@FiDecoded · 𝕏 Twitter · refreshed every pipeline run</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    followers      = _get_followers(df)
    follower_str   = f"{followers:,}" if followers is not None else "—"
    total_likes    = int(df["our_likes"].sum())    if not df.empty else 0
    total_replies  = int(df["our_replies"].sum())  if not df.empty else 0
    total_retweets = int(df["our_retweets"].sum()) if not df.empty else 0
    total_views    = int(df["our_views"].sum())    if not df.empty else 0
    total_quotes   = int(df["our_quotes"].sum())   if not df.empty else 0
    total_engage   = total_likes + total_replies + total_retweets + total_quotes
    eng_rate       = f"{(total_engage / total_views * 100):.2f}%" if total_views > 0 else "—"

    # ── Stat cards ────────────────────────────────────────────────────────────
    eg1, eg2, eg3, eg4, eg5 = st.columns(5)
    total_posts_eg = len(df) if not df.empty else 0
    for col, val, label, color in [
        (eg1, follower_str,           "Followers",       "#1d9bf0"),
        (eg2, f"{total_posts_eg:,}",  "Total Posts",     "#f0f0f0"),
        (eg3, f"{total_likes:,}",     "Total Likes",     "#f0f0f0"),
        (eg4, f"{total_replies:,}",   "Replies",         "#f0f0f0"),
        (eg5, eng_rate,               "Engagement Rate", "#4ade80"),
    ]:
        with col:
            st.markdown(
                f'<div class="eg-card">'
                f'<div class="eg-card-val" style="color:{color}">{val}</div>'
                f'<div class="eg-card-label">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Top Threads by Views ──────────────────────────────────────────────────
    st.markdown(
        '<p class="page-sub" style="font-size:0.8rem;color:#555;margin-bottom:10px;'
        'letter-spacing:.07em;text-transform:uppercase">🔥 Top Threads by Views</p>',
        unsafe_allow_html=True,
    )
    if not df.empty and df["our_views"].max() > 0:
        top_df = df[df["our_views"] > 0].nlargest(8, "our_views").copy()
        top_df["preview"] = top_df["tweet_text"].apply(
            lambda t: str(t).split(" || ")[0][:90] + "…" if len(str(t).split(" || ")[0]) > 90 else str(t).split(" || ")[0]
        )
        top_df["threads"] = top_df["thread_count"].apply(lambda n: f"🧵 {n}" if n > 1 else "—")
        top_df["date"]    = top_df["posted_at"].dt.strftime("%d %b")

        top_tbl = top_df[["date", "preview", "threads", "our_views", "our_likes", "our_replies"]].copy()
        top_tbl.columns = ["Date", "Tweet", "Thread", "Views", "Likes", "Replies"]
        st.dataframe(
            top_tbl,
            use_container_width=True,
            hide_index=True,
            height=min(50 + len(top_tbl) * 38, 360),
            column_config={"Views": st.column_config.ProgressColumn(
                "Views", min_value=0, max_value=int(top_tbl["Views"].max() or 1), format="%d"
            )},
        )
    else:
        st.markdown(
            '<div style="text-align:center;padding:36px;color:#2a2a2a;font-size:0.9rem;'
            'border:1px dashed #1e1e1e;border-radius:10px">'
            'View counts will populate after the next pipeline run</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Charts ────────────────────────────────────────────────────────────────
    has_metrics = not df.empty and df["our_views"].sum() > 0
    if has_metrics:
        chart_df = df[["posted_at", "our_views", "our_likes", "our_replies", "our_retweets"]].dropna(subset=["posted_at"]).copy()
        chart_df = chart_df[chart_df["our_views"] > 0].sort_values("posted_at")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<p class="page-sub" style="margin-bottom:8px">Views per post</p>', unsafe_allow_html=True)
            if not chart_df.empty:
                st.altair_chart(
                    alt.Chart(chart_df)
                    .mark_bar(color="#1d9bf0", cornerRadiusTopLeft=3, cornerRadiusTopRight=3)
                    .encode(
                        x=alt.X("posted_at:T", title=""),
                        y=alt.Y("our_views:Q", title="Views"),
                        tooltip=[
                            alt.Tooltip("posted_at:T", title="Date"),
                            alt.Tooltip("our_views:Q", title="Views"),
                        ],
                    )
                    .properties(height=220),
                    use_container_width=True,
                )

        with c2:
            st.markdown('<p class="page-sub" style="margin-bottom:8px">Likes & Replies per post</p>', unsafe_allow_html=True)
            if not chart_df.empty:
                lrr = chart_df.melt(
                    "posted_at",
                    ["our_likes", "our_replies"],
                    "metric", "value",
                )
                lrr["metric"] = lrr["metric"].map({
                    "our_likes": "Likes",
                    "our_replies": "Replies",
                })
                st.altair_chart(
                    alt.Chart(lrr)
                    .mark_bar()
                    .encode(
                        x=alt.X("posted_at:T", title=""),
                        y=alt.Y("value:Q", title="Count"),
                        color=alt.Color("metric:N", scale=alt.Scale(
                            domain=["Likes", "Replies"],
                            range=["#1d9bf0", "#6b7280"],
                        )),
                        tooltip=[
                            alt.Tooltip("posted_at:T", title="Date"),
                            alt.Tooltip("metric:N",    title="Metric"),
                            alt.Tooltip("value:Q",     title="Count"),
                        ],
                    )
                    .properties(height=220),
                    use_container_width=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Per-tweet breakdown table ─────────────────────────────────────────────
    st.markdown(
        '<p class="page-sub" style="font-size:0.8rem;color:#555;margin-bottom:8px;'
        'letter-spacing:.07em;text-transform:uppercase">All Posts Breakdown</p>',
        unsafe_allow_html=True,
    )
    if not df.empty:
        tbl = df[["posted_at", "tweet_text", "thread_count", "our_views", "our_likes", "our_replies"]].copy()
        tbl["tweet_text"] = tbl["tweet_text"].apply(
            lambda t: str(t).split(" || ")[0][:80] + "…" if len(str(t).split(" || ")[0]) > 80 else str(t).split(" || ")[0]
        )
        tbl["posted_at"] = tbl["posted_at"].dt.strftime("%d %b %Y %H:%M")
        tbl["thread_count"] = tbl["thread_count"].apply(lambda n: f"🧵 {n}" if n > 1 else "—")
        tbl.columns = ["Posted", "Tweet", "Thread", "Views", "Likes", "Replies"]
        st.dataframe(tbl, use_container_width=True, hide_index=True, height=400)

# ── PIPELINE LOG ──────────────────────────────────────────────────────────────
elif page == "pipeline":
    st.markdown('<p class="page-title">Pipeline Log</p>', unsafe_allow_html=True)
    st.markdown('<p class="page-sub">Last 7 days · one entry per day, newest first</p>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    _log_history = []
    if VM_API_URL and VM_API_KEY:
        try:
            import requests as _req
            _r = _req.get(f"{VM_API_URL}/log", headers={"X-API-Key": VM_API_KEY}, timeout=10)
            if _r.status_code == 200:
                _raw = _r.json()
                _log_history = _raw if isinstance(_raw, list) else []
        except Exception as _le:
            st.warning(f"Could not fetch log from VM: {_le}")

    if not _log_history:
        st.markdown(
            '<div style="background:#111;border:1px solid #1e1e1e;border-radius:8px;'
            'padding:32px;text-align:center;color:#444;font-size:0.9rem">'
            'No pipeline logs yet — run the pipeline first.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        def _day_label(d):
            try:
                _dt = datetime.strptime(d, "%Y-%m-%d")
                _delta = (datetime.now().date() - _dt.date()).days
                if _delta == 0: return f"Today  ·  {_dt.strftime('%d %b %Y')}"
                if _delta == 1: return f"Yesterday  ·  {_dt.strftime('%d %b %Y')}"
                return _dt.strftime("%d %b %Y")
            except Exception:
                return d

        # One expandable card per day — today open by default
        for _ci, _log_data in enumerate(_log_history):
            _status     = _log_data.get("status", "ok")
            _run_date   = _log_data.get("date", "—")
            _run_time   = _log_data.get("time", "—")
            _elapsed    = _log_data.get("elapsed_sec", 0)
            _events     = _log_data.get("events", [])
            _full_steps = _log_data.get("full_steps", [])

            _elapsed_fmt  = f"{_elapsed // 60}m {_elapsed % 60}s" if _elapsed else "—"
            _status_color = "#4caf50" if _status == "ok" else "#ef5350"
            _status_icon  = "✓" if _status == "ok" else "✗"
            _status_label = "SUCCESS" if _status == "ok" else "ERROR"
            _card_label   = (
                f"{_status_icon} {_day_label(_run_date)}"
                f"   —   {_status_label}   ·   {_run_time}   ·   {_elapsed_fmt}"
            )

            with st.expander(_card_label, expanded=(_ci == 0)):
                # Events timeline
                _ev_html = ""
                for ev in _events:
                    _is_err = "ERROR" in ev
                    _dot_col = "#ef5350" if _is_err else "#4caf50"
                    _txt_col = "#ef5350" if _is_err else "#ccc"
                    _ev_html += (
                        f'<div style="display:flex;align-items:flex-start;gap:10px;'
                        f'padding:7px 0;border-bottom:1px solid #111">'
                        f'<div style="width:7px;height:7px;border-radius:50%;background:{_dot_col};'
                        f'margin-top:5px;flex-shrink:0"></div>'
                        f'<div style="font-size:0.82rem;color:{_txt_col};font-family:monospace">{ev}</div>'
                        f'</div>'
                    )
                st.markdown(
                    f'<div style="background:#0d0d0d;border:1px solid #1a1a1a;border-radius:8px;'
                    f'padding:14px 18px;margin-bottom:12px">{_ev_html}</div>',
                    unsafe_allow_html=True,
                )

                # Full step trace (always available, auto-expanded on error)
                if _full_steps:
                    _trace_label = "Full step trace" + (" — error debug" if _status == "error" else "")
                    with st.expander(_trace_label, expanded=(_status == "error")):
                        st.code("\n".join(_full_steps), language=None)
