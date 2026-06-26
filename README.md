# TT Festival timetable

A static, auto-refreshing visualiser of the **TT Festival** (Assen) programme,
grouped by **day**, **stage** and **time**.

🔗 **Live page:** https://graafg.github.io/tt-timetable/

- Opens on **today** and scrolls to the **current hour** (red "now" line).
- Grid (clash-finder) and list views, per-day tabs, artist/stage filter, detail popups.
- Times shown in **Europe/Amsterdam** (CEST) regardless of your device timezone.
- Data **auto-refreshes hourly** via GitHub Actions — see the footer for the last fetch time.

## How it works

`timetable.json` is built from the festival app's own backend
(`app.appmiral.com/api/v7`, the white-label **Appmiral** platform) and committed to
this repo. `index.html` is a single self-contained page that fetches that JSON — no
build step, no framework, no server.

```
build_timetable.py   # fetches stages + performances + artists, writes timetable.json
index.html           # the visualiser (fetches timetable.json)
timetable.json       # generated data (refreshed hourly by the Action)
.github/workflows/refresh.yml
```

## Refreshing the data

The API requires an `x-protect` header (an app-embedded key). It is **not** stored in
this repo — it's supplied as the GitHub Actions secret **`APPMIRAL_X_PROTECT`**, which
the workflow passes to the script as the `X_PROTECT` env var.

Run locally:

```bash
export X_PROTECT=<the x-protect value>
python build_timetable.py
```

The `refresh.yml` workflow runs hourly (and on demand via *Run workflow*), rebuilds
`timetable.json`, and commits it only if it changed.

## Source / disclaimer

Data comes from the public TT Festival app backend and is used here only to display the
public event programme. All event information belongs to the festival organisers.
