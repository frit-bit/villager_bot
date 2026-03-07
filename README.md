# Villager Bot

A multipurpose Discord bot built with `discord.py`, featuring an economy system, fun commands, and moderation utilities.

[Official Discord Server Link](https://discord.gg/JArnC4Y2Ug)

---

## Features

- 🪙 **Economy System** — Coin balances stored per-user per-server via SQLite
- 🎲 **Gambling** — Dice roll betting with randomized outcomes
- 🎱 **Fun Commands** — 8ball, coinflip, RNG, fight, slap, and more
- 🛠️ **Admin Tools** — Add coins, make the bot speak, sync slash commands
- 📋 **Server Info** — Quick server stats embed

---

## Commands

### Economy
| Command | Description |
|---|---|
| `/checkbalance <user>` | Check a user's coin balance |
| `/addcoins <user> <amount>` | Add coins to a user *(requires Kick Members permission)* |
| `/diceroll <amount> <number>` | Bet coins on a dice roll (1–6) |

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

---

## Database

The bot uses a local SQLite database to store economy data.

---

## Notes

- DMs sent to the bot are logged. Logs are cleared every ~30 days.
- The dice roll is intentionally weighted (win chance is ~33%)
- Coin balances never drop below 1, so you can keep using the economy commands



# NEW FEATURES COMING SOON!
