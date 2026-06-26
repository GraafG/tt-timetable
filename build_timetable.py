#!/usr/bin/env python3
"""Fetch the TT Festival programme from the Appmiral API and write timetable.json.

The read API requires the app's static `x-protect` header. Provide it via the
X_PROTECT environment variable (do not hard-code it). The value ships in the
Android app's resources (res/values/strings.xml -> x_Protect).
"""
import json, os, sys, urllib.request, datetime

FESTIVAL = "ttfestival"
EDITION = "ttfestival2026"
BASE = f"https://app.appmiral.com/api/v7/events/{FESTIVAL}/editions/{EDITION}"

X_PROTECT = os.environ.get("X_PROTECT", "").strip()
if not X_PROTECT:
    sys.exit("ERROR: X_PROTECT env var is not set (the Appmiral x-protect header value).")

HEADERS = {
    "x-app-version": "v2.0.1",
    "x-platform": "android",
    "x-app-id": "com.appmiral.ttfestival",
    "x-protect": X_PROTECT,
    "Accept": "application/json",
    "User-Agent": "okhttp/4.12.0",
}


def fetch(path):
    req = urllib.request.Request(f"{BASE}/{path}", headers=HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    return d["data"] if isinstance(d, dict) and "data" in d else d


def main():
    stages = fetch("stages")
    perfs = fetch("performances")
    artists = fetch("artists")

    art = {str(a["id"]): a for a in artists}
    stg = {str(s["id"]): s for s in stages}

    stage_list = sorted(
        ({"id": str(s["id"]), "name": s.get("name"), "color": s.get("color"),
          "priority": s.get("priority")} for s in stages),
        key=lambda s: (s["priority"] if s["priority"] is not None else 9999, s["name"] or ""),
    )

    events = []
    for p in perfs:
        if not p.get("start_time"):
            continue  # skip placeholder / always-on attraction rows without a time
        aid = str(p.get("artist_id"))
        a = art.get(aid)
        sid = str(p.get("stage_id")) if p.get("stage_id") is not None else None
        s = stg.get(sid)
        title = p.get("name") or (a.get("name") if a else None) or "(untitled)"
        events.append({
            "id": p["id"],
            "title": title,
            "stageId": sid,
            "stageName": p.get("stage_name") or (s.get("name") if s else (f"Stage {sid}" if sid else "—")),
            "stageColor": p.get("color") or (s.get("color") if s else None),
            "stagePriority": (s.get("priority") if s else 9999),
            "artistName": a.get("name") if a else None,
            "artistImage": a.get("image") if a else None,
            "bio": a.get("body") if a else None,
            "start": p.get("start_time"),
            "end": p.get("end_time"),
            "hideStart": 1 if p.get("hide_start_time") else 0,
            "hideEnd": 1 if p.get("hide_end_time") else 0,
            "soldOut": 1 if p.get("sold_out") else 0,
            "showInSchedule": 1 if p.get("show_in_schedule") else 0,
        })

    events.sort(key=lambda e: (e["start"] or "", e["stageName"] or ""))

    data = {
        "festival": "TT Festival",
        "edition": EDITION,
        "source": "Appmiral API app.appmiral.com/api/v7 (live)",
        "fetchedAt": datetime.datetime.now(datetime.timezone.utc).replace(microsecond=0).isoformat(),
        "timezone": "Europe/Amsterdam",
        "stages": stage_list,
        "events": events,
    }

    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "timetable.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"wrote {out}: {len(events)} events, {len(stage_list)} stages, fetched {data['fetchedAt']}")


if __name__ == "__main__":
    main()
