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
This is the free "lite" version. **[BotDrop](https://botdrop-gg.github.io/)** sells tested, Docker-ready, self-hosted Discord and Steam bot source code you own and can rebrand:
- **[Free Games Radar](https://botdrop-gg.github.io/#products)**: Epic + Steam + GOG, upcoming games, Docker and deploy configs.
- **[Discord Gaming Community Kit](https://botdrop-gg.github.io/discord-gaming-community-kit/)**: one bot with moderation, free games, Steam deals, patch notes, player counts and what-to-play.
- **[The BotDrop Bundle](https://botdrop-gg.github.io/#bundle)**: all templates, launch price $29 (regular $49).

## License
MIT. Do whatever you like with it.
