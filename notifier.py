#!/usr/bin/env python3
"""Free Games Notifier Lite: posts Epic Games Store free games to a Discord webhook.
Usage: DISCORD_WEBHOOK_URL=... python notifier.py   (omit the webhook to just print)"""
import json, os, sys, urllib.request
from datetime import datetime, timezone

API = "https://store-site-backend-static.ak.epicgames.com/freeGamesPromotions?locale=en-US&country=US"
STATE = os.getenv("STATE_FILE", "posted.json")

def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "free-games-notifier-lite"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)

def free_now(data, now=None):
    """Return [{'id','title','url','until'}] for games that are 100% off right now."""
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
                    games.append({"id": g["id"], "title": g["title"], "url": url, "until": end.strftime("%b %d")})
    return games

def message(games):
    lines = [f"🎁 **{g['title']}** is free on Epic until {g['until']}: <{g['url']}>" for g in games]
    return "\n".join(lines)

def main():
    games = free_now(get_json(API))
    seen = set(json.load(open(STATE))) if os.path.exists(STATE) else set()
    new = [g for g in games if g["id"] not in seen]
    if not new:
        print("No new free games."); return
    text = message(new); print(text)
    hook = os.getenv("DISCORD_WEBHOOK_URL")
    if hook:
        req = urllib.request.Request(hook, data=json.dumps({"content": text}).encode(),
                                     headers={"Content-Type": "application/json", "User-Agent": "free-games-notifier-lite"})
        urllib.request.urlopen(req, timeout=20)
    json.dump(sorted(seen | {g["id"] for g in games}), open(STATE, "w"))

if __name__ == "__main__":
    sys.exit(main())
