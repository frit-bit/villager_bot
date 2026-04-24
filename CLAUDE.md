# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Responses should always be as concise as possible. Conserve as many tokens as you can. Even one-word responses are fine. Only explain if asked to, no unnecessary explanation. keep it short and simple.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python3 main.py
```

Requires a `.env` file with `DISCORD_BOT_TOKEN=<token>`. The bot will initialize the SQLite database, sync Discord slash commands, and connect to Discord on startup.

There are no tests or linting tools configured.

## Architecture

The entire bot lives in a single file: `main.py`. There are no cogs, modules, or subdirectories.

**Core class**: `Villager(commands.Bot)` at line 57. Setup hook runs DB initialization and slash command sync. The bot instance is created once at line 104: `bot = Villager()`.

**Database**: SQLite (`bot_data.db`) accessed via `aiosqlite`. Two tables:
- `economy` — per-user, per-guild coin wallets + current job. Composite key `(user_id, guild_id)`.
- `global_bank` — cross-server balances keyed by `user_id` only.

**Work cooldowns** are stored in an in-memory dict (`work_cooldowns` at line 12), so they reset on bot restart.

## Command Pattern

All slash commands follow this structure:

```python
@bot.tree.command(name="command_name", description="Help text shown in Discord")
@app_commands.describe(param="Parameter description")  # omit if no params
async def command_name(interaction: discord.Interaction, param: type):
    await interaction.response.defer(thinking=True)  # use for DB ops or slow responses
    # ... logic ...
    await interaction.followup.send(...)  # use send_message() if no defer
```

For commands that modify the economy, always use `max(1, value)` to prevent wallets from dropping below 1 coin (existing pattern at line 395).

## Permission Levels

- **Owner-only**: `@commands.is_owner()` — used for `/dm` and `/sync`
- **Staff-only**: `interaction.user.guild_permissions.kick_members` check inline — used for `/addcoins`, `/removecoins`, `/speak`
- **Public**: everything else

## Key Behaviors (from README)

- Dice roll is intentionally weighted: 33% win, 66% loss (`random.choice([1,1,2])`)
- Jobs are assigned on first `/work` and locked per user per server; `/resign` clears the job
- All DMs sent to the bot are logged to `message_logs.log` (owner DMs excluded)
- `clear_mlogs` background task clears DM logs every 4380 hours (~6 months)
