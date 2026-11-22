#!/usr/bin/env python3
"""Free Games Notifier Lite: posts Epic Games Store free games to a Discord webhook.
Usage: DISCORD_WEBHOOK_URL=... python notifier.py   (omit the webhook to just print)"""
import json, os, sys, time, urllib.error, urllib.request
from datetime import datetime, timezone

__version__ = "1.0.1"

API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US"
STATE = os.getenv("STATE_FILE", "posted.json")

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "free-games-notifier-lite"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def kind_of(g):
    """'f2p_bonus' when Epic's regular price is 0: the game is already free-to-play, so the
    "100% off" offer is an in-game bonus, not a paid game going free. 'addon' for DLC, else 'game'.
    A missing or odd price block counts as a normal giveaway (we can't tell).
    originalPrice is in the currency's smallest unit, so 0 means free in any currency."""
    orig = (((g.get("price") or {}).get("totalPrice")) or {}).get("originalPrice")
    if isinstance(orig, (int, float)) and not isinstance(orig, bool) and orig == 0:
        return "f2p_bonus"
    return "addon" if g.get("offerType") == "ADD_ON" else "game"

def free_now(data, now=None):
    """Return [{'id','title','url','until','kind'}] for offers that are 100% off right now."""
    now = now or datetime.now(timezone.utc)
    games = []
    for g in data["data"]["Catalog"]["searchStore"]["elements"]:
        for block in ((g.get("promotions") or {}).get("promotionalOffers") or []):
            for offer in block.get("promotionalOffers", []):
                start = datetime.fromisoformat(offer["startDate"].replace("Z", "+00:00"))
                end = datetime.fromisoformat(offer["endDate"].replace("Z", "+00:00"))
                if offer.get("discountSetting", {}).get("discountPercentage") == 0 and start <= now <= end:
                    slug = g.get("productSlug") or (g.get("catalogNs", {}).get("mappings") or [{}])[0].get("pageSlug")
                    url = f"https://store.epicgames.com/en-US/p/{slug}" if slug else "https://store.epicgames.com/free-games"
                    games.append({"id": g["id"], "title": g["title"], "url": url, "until": end.strftime("%b %d"), "kind": kind_of(g)})
    return games

def message(games):
    lines = []
    for g in games:
        kind = g.get("kind", "game")
        if kind == "f2p_bonus":
            lines.append(f"🎮 In-game bonus on Epic (game is free-to-play): **{g['title']}** until {g['until']}. Check the store page for details: <{g['url']}>")
        elif kind == "addon":
            lines.append(f"🧩 **{g['title']}** (add-on, needs the base game) is free on Epic until {g['until']}: <{g['url']}>")
        else:
            lines.append(f"🎁 **{g['title']}** is free on Epic until {g['until']}: <{g['url']}>")
    return "\n".join(lines)

def main():
    games = free_now(get_json(API))
    seen = set(json.load(open(STATE))) if os.path.exists(STATE) else set()
    new = [g for g in games if g["id"] not in seen]
    if not new:
        print("No new free games."); return
    text = message(new); print(text)
    hook = os.getenv("DISCORD_WEBHOOK_URL")
    if not hook:
        # Nothing was posted, so nothing is remembered: add a webhook later and these games still get posted.
        print("(DISCORD_WEBHOOK_URL not set: printed only, not marked as posted)"); return
    if not send(hook, text):
        return 1  # don't save state, so the games are retried next run
    json.dump(sorted(seen | {g["id"] for g in games}), open(STATE, "w"))

def retry_after(err):
    """Seconds to wait from a 429 answer (Retry-After header or JSON retry_after), kept between 0.5 and 60."""
    try:
        return min(max(float(err.headers.get("Retry-After")), 0.5), 60.0)
    except (TypeError, ValueError, AttributeError):
        pass
    try:
        return min(max(float(json.loads(err.read() or b"{}").get("retry_after")), 0.5), 60.0)
    except Exception:
        return 1.0

def send(hook, text, tries=4, sleep=None):
    """POST to the Discord webhook. True only on a 2xx answer; retries 429 rate limits; never prints the webhook URL."""
    req = urllib.request.Request(hook, data=json.dumps({"content": text}).encode(),
                                 headers={"Content-Type": "application/json", "User-Agent": "free-games-notifier-lite"})
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                if 200 <= r.status < 300:
                    return True
                print(f"Discord rejected the webhook: HTTP {r.status}", file=sys.stderr); return False
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < tries - 1:
                wait = retry_after(e); print(f"Discord rate limit (429), retrying in {wait:.1f}s", file=sys.stderr); (sleep or time.sleep)(wait); continue
            hint = " (webhook deleted or URL mistyped?)" if e.code in (401, 404) else " (rate limited too many times)" if e.code == 429 else ""
            print(f"Discord rejected the webhook: HTTP {e.code}{hint}", file=sys.stderr); return False
        except (urllib.error.URLError, OSError) as e:
            print(f"Could not reach Discord ({type(e).__name__}); will retry next run", file=sys.stderr); return False
    return False

if __name__ == "__main__":
    sys.exit(main())
