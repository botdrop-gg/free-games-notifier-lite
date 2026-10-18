# Free Games Notifier Lite

**Posts Epic Games Store free games to your Discord server. Free, one Python file, no dependencies.**

[![tests](https://github.com/botdrop-gg/free-games-notifier-lite/actions/workflows/tests.yml/badge.svg)](https://github.com/botdrop-gg/free-games-notifier-lite/actions/workflows/tests.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

What it posts in your channel:

```
🎁 **Bad Cheese** is free on Epic until Oct 22: <https://store.epicgames.com/en-US/p/bad-cheese-4256d9>
```

## Features

- **Epic free games, automatically.** Checks Epic's public free-games feed and posts each game that is 100% off right now, with a store link and the end date.
- **No repeats.** Remembers what it already posted in `posted.json`, so each giveaway is announced once.
- **No bot, no token, no API keys.** It sends to a Discord **webhook**, so there's nothing to invite and no bot to keep online.
- **Zero dependencies.** One file, Python standard library only (Python 3.9+).
- **Runs anywhere.** On GitHub Actions for free (workflow included), on your PC, with cron, or in Docker.
- **Tested.** Small pytest suite, run on every push.

## Quick start

### Option A: GitHub Actions (free, nothing to host)

1. Click **Fork** at the top of this page.
2. In your fork, go to **Settings → Secrets and variables → Actions → New repository secret**. Name it `DISCORD_WEBHOOK_URL` and paste your webhook URL ([how to get one](#create-a-discord-webhook)).
3. Open the **Actions** tab and click **I understand my workflows, go ahead and enable them** (GitHub turns scheduled workflows off in forks).
4. Open the **notify** workflow and click **Run workflow** to test it. After that it runs every 6 hours by itself.

### Option B: Python on your PC or server

```bash
git clone https://github.com/botdrop-gg/free-games-notifier-lite.git
cd free-games-notifier-lite

python notifier.py            # dry run: just prints the current free games
```

Then post to Discord:

```bash
# macOS / Linux
DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python3 notifier.py
```

```powershell
# Windows PowerShell
$env:DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."; python notifier.py
```

It checks once and exits. To keep it running, schedule it, for example every 6 hours with cron:

```cron
0 */6 * * * cd /path/to/free-games-notifier-lite && DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." python3 notifier.py
```

On Windows, use **Task Scheduler** to run `python notifier.py` in this folder.

### Option C: Docker (no Python install needed)

No image to build. Run it with the official Python image from this folder:

```bash
docker run --rm -v "$PWD:/app" -w /app \
  -e DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..." \
  python:3.13-alpine python notifier.py
```

`posted.json` is saved in this folder, so repeats are still skipped next run.

## Configuration

Settings are environment variables:

| Variable | Required | Default | What it does |
| --- | --- | --- | --- |
| `DISCORD_WEBHOOK_URL` | No | (none) | Where to post. Leave it empty to just print the games. |
| `STATE_FILE` | No | `posted.json` | Where to remember which games were already posted. |

Keep your webhook URL private: anyone who has it can post in that channel. On GitHub, store it only as a secret, never in a file.

## Create a Discord webhook

You need **Manage Webhooks** permission in the server.

1. In Discord, open your server and hover over the channel you want, such as `#free-games`. Click the gear icon (**Edit Channel**).
2. Go to **Integrations → Webhooks → New Webhook**.
3. Give it a name and avatar if you like, such as "Free Games".
4. Click **Copy Webhook URL**. That's your `DISCORD_WEBHOOK_URL`.

Discord's guide: [Intro to Webhooks](https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks).

<details>
<summary>Building a full bot later? Here's how to invite one</summary>

This Lite notifier doesn't need a bot. If you later build or buy a bot with slash commands, invite it from the [Discord Developer Portal](https://discord.com/developers/applications):

1. Click **New Application**, name it, and on the **Bot** page click **Reset Token** to get the bot token (keep it secret).
2. Click **Installation** in the left menu and tick **Guild Install**.
3. Under **Default Install Settings**, add the scopes **bot** and **applications.commands**, plus the permissions the bot needs (for example **Send Messages** and **Embed Links**). Click **Save Changes**.
4. Copy the **Discord Provided Link**, open it, and pick your server.

</details>

## FAQ

**Nothing was posted. Is it broken?**
It only posts games it hasn't posted before. Delete `posted.json` (or, on GitHub Actions, the cache under **Actions → Caches**) to post the current games again. Run without `DISCORD_WEBHOOK_URL` to see what it finds.

**It says "Discord rejected the webhook: HTTP 404".**
The webhook was deleted or the URL is mistyped. Create a new one and update the secret. The games aren't marked as posted, so they'll go out on the next run.

**Does it cover Steam or GOG?**
No, Lite covers Epic only. See [Want more?](#want-more) below.

**How often does Epic change its free games?**
Usually weekly. Checking every 6 hours is plenty.

**Does GitHub Actions cost anything?**
Scheduled workflows on a public repo are free. Each run takes about 10 seconds.

**Which region and prices does it use?**
Epic's US store feed. Free giveaways are usually the same worldwide.

**Can I change the message?**
Yes. Edit the `message()` function in `notifier.py`.

## Run the tests

```bash
pip install pytest
pytest -q
```

## Want more?

This is the free version. [BotDrop](https://getbotdrop.com/) makes self-hosted Discord bots for gaming servers that you own and run yourself:

- **[Free Games Radar](https://getbotdrop.com/free-games-radar/)** (free for your email): free games from Epic, Steam and GOG, including upcoming giveaways, with a one-click Windows launcher (beta).
- **[Gaming Community Kit](https://getbotdrop.com/discord-gaming-community-kit/)** ($25, pay once): one bot with auto-moderation, free games, Steam deals, patch notes and more.

## License

[MIT](LICENSE) © 2026 BotDrop. Use it, change it, share it.

Not affiliated with Epic Games or Discord.
