from datetime import datetime, timezone
from notifier import free_now, message
NOW = datetime(2026, 10, 15, tzinfo=timezone.utc)
def offer(s, e, pct): return [{"promotionalOffers": [{"startDate": s, "endDate": e, "discountSetting": {"discountPercentage": pct}}]}]
DATA = {"data": {"Catalog": {"searchStore": {"elements": [
    {"id": "1", "title": "Free Game", "productSlug": "free-game", "promotions": {"promotionalOffers": offer("2026-10-10T00:00:00.000Z", "2026-10-17T00:00:00.000Z", 0)}},
    {"id": "2", "title": "Half Off", "productSlug": "half", "promotions": {"promotionalOffers": offer("2026-10-10T00:00:00.000Z", "2026-10-17T00:00:00.000Z", 50)}},
    {"id": "3", "title": "Old", "promotions": {"promotionalOffers": offer("2026-09-01T00:00:00.000Z", "2026-09-08T00:00:00.000Z", 0)}},
    {"id": "4", "title": "No Promo", "promotions": None}]}}}}
def test_only_current_free_games():
    g = free_now(DATA, NOW)
    assert [x["title"] for x in g] == ["Free Game"] and g[0]["url"].endswith("/p/free-game")
def test_message():
    assert "Free Game" in message(free_now(DATA, NOW))
def test_webhook_error_keeps_state(tmp_path, monkeypatch, capsys):
    import urllib.error, notifier
    state = tmp_path / "posted.json"
    monkeypatch.setattr(notifier, "STATE", str(state))
    monkeypatch.setattr(notifier, "get_json", lambda url: DATA)
    monkeypatch.setattr(notifier, "free_now", lambda data: free_now(data, NOW))
    monkeypatch.setenv("DISCORD_WEBHOOK_URL", "https://example.invalid/hook")
    def boom(*a, **k): raise urllib.error.HTTPError("u", 404, "Not Found", {}, None)
    monkeypatch.setattr(notifier.urllib.request, "urlopen", boom)
    assert notifier.main() == 1 and not state.exists()
    assert "HTTP 404" in capsys.readouterr().err
