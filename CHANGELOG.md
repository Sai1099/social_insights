# Changelog — Social Insights Dashboard

All notable milestones and changes to `dashboard.py` are documented here.

---

## [v0.5] — 2026-05-19

### Fixed
- **TypeError on Home & Engagement pages** — `our_total_tweets` column was never cast to numeric in `load_data()`, causing `'>' not supported between instances of 'str' and 'int'` crash on every page load. Added to the numeric conversion loop alongside the other `our_*` columns.
- **pandas 2.2 melt warning** — Updated `chart_df.melt()` from positional args to named kwargs (`id_vars`, `value_vars`, `var_name`, `value_name`) to stay compatible with pandas 2.x.

---

## [v0.4] — 2026-05-15

### Added
- **Auto Reply Bot tab** — new `replybot` page showing all auto-replies posted by @FiDecoded; fetches from VM API or local `replied_tweets.csv` fallback.
- **Total Posts from live profile** — `_get_total_tweets()` reads `our_total_tweets` column written by the pipeline (live follower/tweet count fetched at run start), replacing the old `len(df)` approximation.
- **Followers live fallback** — `_get_followers()` now tries twikit as a secondary fallback when the column is absent or all-zero.

---

## [v0.3] — 2026-05-12

### Added
- **3-path CSV parser** — handles three generations of `posted_tweets.csv` column layouts in a single scan-based recovery (handle position scan + `our_*` positional formula + after-src fallback).
- **API streaming** — switched `/data` endpoint fetch to `stream=True` with 60 s timeout to avoid truncation on large CSVs.

### Fixed
- `our_views` recovery — preserve `dict(zip)` value when it is already a valid numeric, avoiding double-overwrite from the positional formula.

---

## [v0.2] — 2026-05-08

### Added
- **Engagement Metrics page** — views/likes/replies bar charts via Altair, top-threads table with `ProgressColumn`, full posts breakdown table.
- **Pipeline Log page** — expandable per-day cards fetched from VM API `/log`; full step trace collapsible on error.
- **Source + Article two-column reference block** — each post card shows the X handles scraped and the news articles fetched, with avatar initials, profile links, and article metadata.
- **YF live prices chips** — shows `yf_prices` as green monospace chips on each post card.
- **Model filter** — Posts page filter by `ai_model` used for that run.

### Fixed
- Handle validation regex — exclude category strings (`news_event`, `stock_specific`, etc.) that were matching as valid Twitter handles in older CSV rows.

---

## [v0.1] — 2026-04-28

### Added
- Initial dashboard with dark theme, sidebar navigation (Home, Posts, Engagement, Pipeline Log).
- `load_data()` reads `posted_tweets.csv` locally or from Oracle VM API (`VM_API_URL` / `VM_API_KEY` env vars).
- Home page stat cards: Followers, Total Posts, Total Views, Total Likes, Engagement Rate.
- Top Performing Post card on Home.
- Posts page with search, date filter, tweet bubbles, per-post engagement row.
- `@st.cache_data(ttl=30)` for CSV reload without full page refresh.
