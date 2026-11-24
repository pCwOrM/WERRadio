#!/usr/bin/env python3
import glob
import json
import os
import random
import sys
import urllib.request

API_URL = "https://ozan-api.werr.io/v1/public/songs?sort=latest&limit=100"
TMP_DIR = "/tmp/werrozan-radio/tracks"
QUEUE_FILE = "/tmp/werrozan-radio/shuffle_queue.json"
CACHE_LIST = "/tmp/werrozan-radio/catalog_cache.json"
WEB_CATALOG = "/var/www/rad.werr.io/catalog.json"

def fetch_songs():
    try:
        req = urllib.request.Request(API_URL, headers={"User-Agent": "WerrOzan-Radio/1.0"})
        data = json.loads(urllib.request.urlopen(req, timeout=12).read().decode("utf-8"))
        items = [s for s in (data.get("items") or []) if s.get("audio_url")]
        if items:
            with open(CACHE_LIST, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False)
            try:
                lite = [{"title": s.get("title"), "author_name": s.get("author_name"), "cover_url": s.get("cover_url")} for s in items]
                tmp_c = WEB_CATALOG + ".tmp"
                with open(tmp_c, "w", encoding="utf-8") as cf:
                    json.dump({"items": lite}, cf, ensure_ascii=False)
                os.replace(tmp_c, WEB_CATALOG)
            except Exception:
                pass
            return items
    except Exception:
        pass
    if os.path.exists(CACHE_LIST):
        with open(CACHE_LIST, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def cleanup_old_tracks(keep_path=None):
    files = sorted(glob.glob(os.path.join(TMP_DIR, "*")), key=os.path.getmtime, reverse=True)
    kept = 0
    for p in files:
        if keep_path and os.path.abspath(p) == os.path.abspath(keep_path):
            continue
        if kept < 1:
            kept += 1
            continue
        try:
            os.remove(p)
        except Exception:
            pass

def main():
    os.makedirs(TMP_DIR, exist_ok=True)
    items = fetch_songs()
    if not items:
        return 1

    by_id = {s["id"]: s for s in items if s.get("id")}
    all_ids = list(by_id.keys())
    queue_state = {"queue": [], "last_id": None}
    if os.path.exists(QUEUE_FILE):
        try:
            queue_state = json.load(open(QUEUE_FILE, "r", encoding="utf-8"))
        except Exception:
            pass

    q = [sid for sid in (queue_state.get("queue") or []) if sid in by_id]
    last_id = queue_state.get("last_id")
    if not q:
        q = list(all_ids)
        random.shuffle(q)
        if len(q) > 1 and q[0] == last_id:
            q.append(q.pop(0))

    sid = q.pop(0)
    pick = by_id[sid]
    queue_state = {"queue": q, "last_id": sid}
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue_state, f)

    url = pick["audio_url"]
    if url.startswith("/"):
        url = "https://ozan-api.werr.io" + url

    out_path = os.path.join(TMP_DIR, f"{sid}.flac")
    cleanup_old_tracks(keep_path=out_path)

    if not os.path.exists(out_path) or os.path.getsize(out_path) < 1024:
        req = urllib.request.Request(url, headers={"User-Agent": "WerrOzan-Radio/1.0"})
        tmp_dl = out_path + ".part"
        with urllib.request.urlopen(req, timeout=45) as r, open(tmp_dl, "wb") as f:
            while True:
                chunk = r.read(65536)
                if not chunk:
                    break
                f.write(chunk)
        os.replace(tmp_dl, out_path)

    title = (pick.get("title") or "WerrOzan Eser").replace('"', "'").replace("\n", " ")
    artist = (pick.get("author_name") or "WerrOzan").replace('"', "'").replace("\n", " ")
    print(f'annotate:title="{title}",artist="{artist}":file://{out_path}', end="")
    return 0

if __name__ == "__main__":
    sys.exit(main())
