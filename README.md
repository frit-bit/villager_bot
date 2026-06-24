# Villager Bot

A multipurpose Discord bot built with `discord.py`, featuring an economy system, fun commands, AI chat, and moderation utilities.

[Official Discord Server Link](https://discord.gg/JArnC4Y2Ug)

---

## Features

- 🪙 **Economy System** — Coin wallets stored per-user per-server via SQLite
- 🏦 **Global Bank** — Bank balances follow users across servers
- 💼 **Jobs** — Work for coins with a 5-minute cooldown
- 🎲 **Gambling** — Dice roll betting with randomized outcomes
- 🕵️ **Crime Controls** — Steal coins when crime is enabled by server staff
- 🤖 **AI Chat** — Ask Villager Bot questions with `/chat`
- 🎱 **Fun Commands** — 8ball, coinflip, RNG, fight, slap, and more
- 🛠️ **Admin Tools** — Add/remove coins, make the bot speak, toggle crime, sync commands
- 📋 **Server Info** — Quick server stats embed

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
| `/speak <message> [channel]` | Make the bot say something *(moderator-only)* |
| `/help` | Show the command list inside Discord |

### Prefix Commands
These use the `v?` prefix instead of slash commands.

| Command | Description |
|---|---|
| `v?toggle_crime` | Enable or disable `/steal` in the current server *(requires Kick Members permission)* |
| `v?dm <user> <message>` | DM a user as the bot *(owner-only)* |
| `v?sync` | Manually sync slash commands *(owner-only)* |

---

## Database

The bot uses a local SQLite database to store economy data:

- `economy` stores each user's wallet and job per server
- `global_bank` stores each user's cross-server bank balance
- `guild_settings` stores server-level settings, including whether crime is enabled

---

## Notes

- DMs sent to the bot are logged. Logs are cleared every ~6 months, earlier if the bot is restarted.
- The dice roll is intentionally weighted (win chance is ~33%)
- Coin wallets never drop below 1, so you can keep using the economy commands
- First time using `/work` requires specifying a job; after that it's locked in
- `/steal` can take at most 25% of a user's wallet and can be disabled with `v?toggle_crime`
- Slash commands are synced automatically when the bot starts
