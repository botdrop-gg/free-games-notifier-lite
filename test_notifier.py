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


# --- delivery: 2xx only, 429 retry, network errors caught, nothing remembered unless posted
import io, json, urllib.error, pytest
import notifier
def _setup(tmp_path, monkeypatch, hook="https://discord.com/api/webhooks/1/test-secret"):
    state = tmp_path / "posted.json"
    monkeypatch.setattr(notifier, "STATE", str(state)); monkeypatch.setattr(notifier, "get_json", lambda url: DATA)
    monkeypatch.setattr(notifier, "free_now", lambda data: free_now(data, NOW)); monkeypatch.setattr(notifier.time, "sleep", lambda s: None)
    if hook: monkeypatch.setenv("DISCORD_WEBHOOK_URL", hook)
    else: monkeypatch.delenv("DISCORD_WEBHOOK_URL", raising=False)
    return state
class _Ok:
    status = 204
    def __enter__(self): return self
    def __exit__(self, *a): return False
def _seq(monkeypatch, steps):
    calls = []
    def urlopen(req, timeout=None):
        calls.append(1); s = steps.pop(0)
        if s == "down": raise urllib.error.URLError("refused")
        if s == 204: return _Ok()
        raise urllib.error.HTTPError("u", s, "x", {"Retry-After": "2"} if s == 429 else {}, io.BytesIO(b"{}"))
    monkeypatch.setattr(notifier.urllib.request, "urlopen", urlopen); return calls
def test_success_saves_state(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch); calls = _seq(monkeypatch, [204])
    assert notifier.main() is None and json.loads(state.read_text()) == ["1"] and len(calls) == 1
def test_429_then_success(tmp_path, monkeypatch):
    state = _setup(tmp_path, monkeypatch); calls = _seq(monkeypatch, [429, 204])
    assert notifier.main() is None and state.exists() and len(calls) == 2
def test_429_gives_up(tmp_path, monkeypatch, capsys):
    state = _setup(tmp_path, monkeypatch); calls = _seq(monkeypatch, [429] * 4)
    assert notifier.main() == 1 and not state.exists() and len(calls) == 4 and "429" in capsys.readouterr().err
def test_network_error_caught(tmp_path, monkeypatch, capsys):
    state = _setup(tmp_path, monkeypatch); _seq(monkeypatch, ["down"])
    assert notifier.main() == 1 and not state.exists()
    err = capsys.readouterr().err; assert "Could not reach Discord" in err and "test-secret" not in err
def test_no_webhook_does_not_mark_seen(tmp_path, monkeypatch, capsys):
    state = _setup(tmp_path, monkeypatch, hook=None)
    assert notifier.main() is None and not state.exists() and "not marked as posted" in capsys.readouterr().out
def test_retry_after_parsing():
    e = urllib.error.HTTPError("u", 429, "x", {"Retry-After": "0.1"}, io.BytesIO(b"{}")); assert notifier.retry_after(e) == 0.5
    e = urllib.error.HTTPError("u", 429, "x", {}, io.BytesIO(b'{"retry_after": 3}')); assert notifier.retry_after(e) == 3.0
