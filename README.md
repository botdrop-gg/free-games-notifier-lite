# Free Games Notifier Lite: Epic free games → Discord webhook

A tiny, free, MIT-licensed **Discord bot / webhook notifier for Epic Games Store free games**. One Python file, **zero dependencies** (standard library only), no API keys. Runs on your PC, a cron job, or **free on GitHub Actions**.

```
🎁 TerraScape is free on Epic until Oct 15: <https://store.epicgames.com/en-US/p/terrascape-2b12b1>
```

## Quick start
```bash
python notifier.py                                   # print current free games
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/... python notifier.py
```
It remembers what it already posted in `posted.json`, so it only announces new giveaways.

**Run it free on GitHub Actions:** fork this repo → Settings → Secrets → Actions → add `DISCORD_WEBHOOK_URL`. The included workflow checks every 6 hours.

Tests: `pip install pytest && pytest -q`

## Want more?
This is the free "lite" version. **[BotDrop](https://getbotdrop.com/)** sells tested, Docker-ready, self-hosted Discord and Steam bot source code you own and can rebrand:
- **[Free Games Radar](https://getbotdrop.com/free-games-radar/)** ($6): Epic + Steam + GOG, upcoming games, Docker and deploy configs.
- **[Gaming Community Kit for Discord](https://getbotdrop.com/discord-gaming-community-kit/)** ($25): one bot with moderation, free games, Steam deals, patch notes, player counts and what-to-play.
- **[BotDrop Bundle](https://getbotdrop.com/#bundle)**: all 10 templates for $29 (the 9 sold separately add up to $107).

## License
MIT. Do whatever you like with it.
