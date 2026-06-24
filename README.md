# Villager Bot

A multipurpose Discord bot built with `discord.py`, featuring an economy system, global banking, jobs, gambling, AI chat, fun commands, and staff utilities.

[Official Discord Server Link](https://discord.gg/JArnC4Y2Ug)

---

## Features

- 🪙 **Economy System** — Coin wallets stored per-user per-server via SQLite
- 🏦 **Global Bank** — Bank balances follow users across servers
- 💼 **Jobs** — Work for coins with a 5-minute cooldown
- 🎲 **Gambling** — Dice roll betting with randomized outcomes
- 🕵️ **Crime Controls** — Steal coins when crime is enabled by the server owner
- 🤖 **AI Chat** — Ask Villager Bot with `/chat`, mention it, reply to it, or let it occasionally join server chat
- 🎱 **Fun Commands** — 8ball, coinflip, RNG, fight, slap, and more
- 🛠️ **Admin Tools** — Add/remove coins, make the bot speak, toggle crime, sync commands
- 📋 **Server Info** — Quick server stats embed

---

## Setup

```bash
pip install -r requirements.txt
python3 main.py
```

Create a `.env` file before running:

```env
DISCORD_BOT_TOKEN=your_discord_bot_token
GROQ_API_KEY=your_groq_api_key
```

The bot initializes SQLite tables and syncs slash commands when it starts.

---

## Commands
-# Run /help to see these details in Discord

### Economy
| Command | Description |
|---|---|
| `/balance [user]` | Check a user's wallet, bank balance, and local total |
| `/deposit [amount]` | Move wallet coins into the global bank. Leave blank to deposit all |
| `/withdraw [amount]` | Move bank coins back into this server's wallet. Leave blank to withdraw all |
| `/work [job]` | Work for 5 coins. First use requires choosing a job, then that job is locked in |
| `/resign` | Resign from your current job so you can choose a new one |
| `/diceroll <amount> <number>` | Bet coins on a dice roll (1–6) |
| `/steal <user> <amount>` | Steal up to 25% of another user's wallet when crime is enabled |
| `/addcoins <user> <amount>` | Add coins to a user *(requires Kick Members permission or bot owner)* |
| `/removecoins <user> <amount>` | Remove coins from a user *(requires Kick Members permission or bot owner)* |

### AI
| Command | Description |
|---|---|
| `/chat <prompt>` | Ask Villager Bot a question using Groq's free tier |
| Mention/reply chat | The bot can respond when mentioned, when replied to, or randomly in server chat |

### Fun
| Command | Description |
|---|---|
| `/8ball <question>` | Ask the magic 8ball |
| `/coinflip` | Flip a coin |
| `/rng <start> <end>` | Generate a random number in a range |
| `/choice <1-5 choices>` | Let the bot pick from your choices |
| `/fight <user> <attack>` | Attack someone with a custom move |
| `/slap <user> <tool>` | Slap someone with a Hand, Fish, or Sock |
| `/hello` | Say hello to the villager |

### Utility
| Command | Description |
|---|---|
| `/ping` | Check bot latency |
| `/serverinfo` | View server info |
| `/speak <message> [channel]` | Make the bot say something here or in another text channel *(requires Kick Members permission or bot owner)* |
| `/help` | Show the command list inside Discord |

### Prefix Commands
These use the `v?` prefix instead of slash commands.

| Command | Description |
|---|---|
| `v?toggle_crime` | Enable or disable `/steal` in the current server *(server owner only)* |
| `v?dm <user> <message>` | DM a user as the bot *(owner-only)* |
| `v?sync` | Manually sync slash commands *(owner-only)* |

---

## Database

The bot uses a local SQLite database to store economy data:

- `economy` stores each user's wallet and job per server
- `global_bank` stores each user's cross-server bank balance
- `guild_settings` stores server-level settings, including whether crime is enabled
- `message_logs.log` stores DM logs from non-owner users until the periodic cleanup runs

---

## Notes

- DMs sent to the bot are logged, except owner DMs. Logs are cleared every ~6 months, earlier if the bot is restarted.
- AI responses use Groq's `meta-llama/llama-4-scout-17b-16e-instruct` model.
- In server chat, the bot can respond when mentioned, when replied to, or by random chance.
- The dice roll is intentionally weighted (win chance is ~33%).
- Coin wallets never drop below 1, so you can keep using the economy commands
- First time using `/work` requires specifying a job; after that it's locked in
- `/steal` can take at most 25% of a user's wallet and can be disabled by the server owner with `v?toggle_crime`
- Slash commands are synced automatically when the bot starts
