import os
import discord
import asyncio
import random
import aiosqlite
from discord.ext import commands
from discord import app_commands, Member, User
from datetime import datetime, timedelta
from discord.ext import tasks
from dotenv import load_dotenv

work_cooldowns = []

load_dotenv(override=True)

# set token env variable
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
if not TOKEN:
    raise ValueError("DISCORD_BOT_TOKEN environment variable is not set.")
print(TOKEN)

DB_PATH = "bot_data.db"

async def init_db():
    print("Initializing Database...")
    async with aiosqlite.connect(DB_PATH) as db:
        # economy table
        await db.execute('''
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER,
                guild_id INTEGER,
                balance INTEGER,
                job TEXT DEFAULT NULL,
                PRIMARY KEY (user_id, guild_id)
                )
                ''')
        print("Database Initialized Successfully.")


async def add_coins(user_id: int, guild_id: int, balance: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.executemany(
            "INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)",
            [(user_id, guild_id, balance)]
        )
        await db.commit()  

# Clear Message Logs every month
@tasks.loop(hours=720)
async def clear_mlogs():
    try:
        with open("message_logs.txt", "w", encoding="utf-8") as f:
            f.write(f"[Logs cleared on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]\n")
            print("[Message Logs Cleared]")
    except Exception as e:
        print(f"[Error Clearing Logs: {e}]")



class Villager(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        self.is_syncing = False
        super().__init__(
            command_prefix='!',
            intents=intents,
            dm_help=True,
            owner_id=947551947735576627
        )


    async def setup_hook(self):
        try:
            print("Starting setup_hook...")
            await init_db()
            print("🔄 Syncing commands...")
            self.is_syncing = True  # Set flag when sync starts
            # wait asyncio.sleep(1)
            # self.tree.default_permissions = None
            synced = await self.tree.sync()
            print(f"✅ Successfully synced {len(synced)} command(s)")
            self.is_syncing = False  # Set flag when sync completes
            print("Setup Complete!")
        except Exception as e:
            # print()
            print(f"❌ Failed to sync commands: {e}")
            self.is_syncing = False  # Make sure to set flag even if sync fails
    



    async def on_ready(self):
        channel = self.get_channel(1366904232317550683)
        print(f'✅ {self.user} is ready and online!')
        await self.change_presence(activity=discord.Game(name="Minecraft"))

        if not clear_mlogs.is_running():
            clear_mlogs.start()

        for guild in self.guilds:
            print(
                f"Connected to guild: {guild.name} (ID: {guild.id}, Member Count: {guild.member_count})"
            )
        print(f"Total visible guilds: {len(self.guilds)}")


bot = Villager()


@bot.tree.command(name="checkbalance", description="Check your coin balance")
@app_commands.describe(user="The user whose balance you want to check.")
async def checkbalance(interaction: discord.Interaction, user: Member):
        await interaction.response.defer(thinking=True)

        user_id = user.id
        guild_id = interaction.guild.id

        async with aiosqlite.connect(DB_PATH) as db:
            # Check is user exists in database
            cursor = await db.execute(
            "SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
            )
            result = await cursor.fetchone()

            if result is None:
                await db.execute(
                "INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)",
                (user_id, guild_id, 10)
                )
                await db.commit()
                balance = 10
                message = f"Balance: {balance} coins"
            elif result[0] == 0:
                await db.execute(
                "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                (1, user_id, guild_id)
                )
                await db.commit()
                balance = 1
                message = f"Balance: {balance} coins"
            else:
                balance = result[0]
                message = f"Balance: {balance} coins"
            embed = discord.Embed(
                title=f"Balance Check for {user}",
                description=message,
                color=discord.Color.gold()
                )
            embed.set_thumbnail(url=user.display_avatar.url)

            await interaction.followup.send(embed=embed)


@bot.tree.command(name="addcoins", description="Add coins to a user")
@app_commands.describe(user="The user who you want to give coins to", amount="How many coins you want to add")
async def addcoins(interaction: discord.Interaction, user: Member, amount: int):
    is_authorized = (interaction.user.guild_permissions.kick_members
                     or await bot.is_owner(interaction.user))
    if not is_authorized:
        await interaction.response.send_message(
            f"Nice try, {interaction.user.mention}, but you don't have permission to use this command.",
            ephemeral=True)
        return
    

    await interaction.response.defer(thinking=True)

    user_id = user.id
    guild_id = interaction.guild.id



    async with aiosqlite.connect(DB_PATH) as db:

        if amount<1:
            await interaction.followup.send("You must specify a positive integer!", ephemeral=True)
            return

        cursor = await db.execute(
            "SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        result = await cursor.fetchone()

        if result is None:
            # User not in DB, insert with starting balance
            new_balance = amount
            await db.execute(
                "INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)",
                (user_id, guild_id, new_balance)
            )
        else:
            # User exists, add to their balance
            new_balance = result[0] + amount
            await db.execute(
                "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                (new_balance, user_id, guild_id)
            )
        await db.commit()

        embed_title = f"Gift to {user}"
        msg = f"{interaction.user.mention} has added {amount} coins to {user.mention}'s balance!\nThey now have {new_balance} coins."
        embed = discord.Embed(
            title=embed_title,
            description=msg,
            color=discord.Color.blue()
        )
        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.followup.send(embed=embed)


@bot.tree.command(name="diceroll", description="Roll a 6-sided dice for money!")
@app_commands.describe(amount="How many coins you want to bet", number="Which side you want to bet on")
async def diceroll(interaction: discord.Interaction, amount: int, number: int):
    if number not in [1,2,3,4,5,6]:
        await interaction.response.send_message("You must select a number from 1-6!", ephemeral=True)
        return
    if amount <=0:
        await interaction.response.send_message("You must bet a positive amount of coins!", ephemeral=True)
        return

    await interaction.response.defer(thinking=True)

    user = interaction.user
    user_id = user.id
    guild_id = interaction.guild.id
    bet = amount

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT balance FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        balance_row = await cursor.fetchone()
        if balance_row is None:
            # User not in DB, give starting balance
            await db.execute(
                "INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)",
                (user_id, guild_id, 10)
            )
            await db.commit()
            balance = 10
        else:
            balance = balance_row[0]

        result = random.choice([1,1,2])
        if bet > balance:
            errormsg = f"You cannot bet more than what you have! Bet at most {balance}."
            await interaction.followup.send(errormsg)
            return
        else:
            if result == 1:
                lossArray = [n for n in range (1,7) if n!= number]
                lossNumber = random.choice(lossArray)
                returnBalance = balance - bet
                if returnBalance <= 0:
                    await db.execute(
                        "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                        (1, user_id, guild_id)
                    )
                    await db.commit()
                    returnBalance = 1
                else:
                    await db.execute(
                        "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                        (returnBalance, user_id, guild_id)
                    )
                    await db.commit()
                balance = returnBalance
                embed_title = "You Lost!"
                msg = f"The die landed on {lossNumber}\n\nLoss of {bet} coins\nNew Balance: {returnBalance} coins"
                embed_color = discord.Color.red()
            elif result == 2:
                winNum = number
                returnBalance = balance + bet
                await db.execute(
                    "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
                    (returnBalance, user_id, guild_id)
                )
                await db.commit()
                embed_title = "You won!"
                msg = f"The die landed on {winNum}\n\nEarnings: {bet} coins\nNew Balance: {returnBalance} coins"
                embed_color = discord.Color.green()
        embed = discord.Embed(
            title=embed_title,
            description=msg,
            color=embed_color
        )
        embed.set_thumbnail(url=user.display_avatar.url)
        await interaction.followup.send(embed=embed)

WORK_COOLDOWN = 300  # seconds

@bot.tree.command(name="work", description="Work for some money!")
@app_commands.describe(job="Your job (leave blank if you already have one)")
async def work(interaction: discord.Interaction, job: str = None):
    user = interaction.user
    user_id = user.id
    guild_id = interaction.guild.id
    key = (user_id, guild_id)

    # check cooldown
    if key in work_cooldowns:
        elapsed = (datetime.now() - work_cooldowns[key]).total_seconds()
        remaining = WORK_COOLDOWN - elapsed
        if remaining > 0:
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            await interaction.response.send_message(
                f"You cannot work for {mins} minutes and {secs} seconds",
                ephemeral=True
            )
            return

    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT job, balance FROM economy WHERE user_id = ? AND guild_id = ?",
            (user_id, guild_id)
        )
        row = await cursor.fetchone()

        if row is None:
            await db.execute(
                "INSERT INTO economy (user_id, guild_id, balance) VALUES (?, ?, ?)",
                (user_id, guild_id, 10)
            )
            await db.commit()
            current_job, balance, new_balance = None, 10, 15
        else:
            current_job, balance = row[0], row[1]
            new_balance = balance + 5

        if current_job is None:
            if job is None:
                await interaction.response.send_message("Select a job before using this command!", ephemeral=True)
                return
            else:
                await db.execute(
                    "UPDATE economy SET job = ?, balance = ? WHERE user_id = ? AND guild_id = ?",
                    (job, balance + 5, user_id, guild_id)
                )
                await db.commit()
                msg = f"You got hired as a {job} person and earned 5 coins on your first day."
        elif job is not None:
            await interaction.response.send_message(f"You already have a job as a {current_job}!", ephemeral=True)
            return
        else:
            msg = f"You worked as a {current_job} and earned 5 coins."

        await interaction.response.defer(thinking=True)
        await db.execute(
            "UPDATE economy SET balance = ? WHERE user_id = ? AND guild_id = ?",
            (new_balance, user_id, guild_id)
        )
        await db.commit()

    # set cooldown
    work_cooldowns[key] = datetime.now()

    embed = discord.Embed(title="Work", description=msg, color=discord.Color.yellow())
    embed.set_thumbnail(url=user.display_avatar.url)
    await interaction.followup.send(embed=embed)


@bot.tree.command(name="hello", description="Say hello to the villager!")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hrmmm! Hello {interaction.user.mention}!")


@bot.tree.command(name="ping", description="Check bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🏓  **Latency:** {round(bot.latency * 1000)} ms  🏓")
    

@bot.tree.command(name="rng", description="Generate a random number from your range.")
@app_commands.describe(start="The first number in the range", end="The last number in the range")
async def rng(interaction: discord.Interaction, start: int, end: int):
    rngArray = [n for n in range (start, end)]
    result = random.choice(rngArray)

    embed = discord.Embed(
        title="RNG",
        description=f"The bot has picked {result}.",
        color=discord.Color.teal()
    )
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1357513493816934520/1437622427281657856/image.png?ex=6913e9b8&is=69129838&hm=f8903f7ebcc9cf6b913c9dd09ac25e84bce281614f7bd12515b8b85972391337&")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="serverinfo",
                  description="Get information about the server",
                  )
async def serverinfo(interaction: discord.Interaction):
    server = interaction.guild
    embed = discord.Embed(title=f"Info about {server.name}:",
                          color=discord.Color.green())
    embed.add_field(name="Server Owner",
                    value=server.owner.mention,
                    inline=False)
    embed.add_field(name="Member Count",
                    value=server.member_count,
                    inline=True)
    embed.add_field(name="Created At",
                    value=server.created_at.strftime("%B %d, %Y"),
                    inline=True)
    embed.set_thumbnail(url=server.icon.url if server.icon else None)
    await interaction.response.send_message(embed=embed)


'''@bot.tree.command(name="report",
                  description="Report a small issue to the creator/dev(s)",
                  )
@app_commands.describe(issue="The issue you want to report.")
async def report(interaction: discord.Interaction, issue: str):
    dev = await bot.fetch_user(947551947735576627)
    app_info = await bot.application_info()
    owner = app_info.owner
    await interaction.response.send_message(
        f"✅ Your bug has been reported to {owner.name}.", ephemeral=True)
    await dev.send(
        f"{interaction.user} reported a bug in the bot!\nThey said: '" + issue +
        "'.")'''


@bot.tree.command(name="speak", description="Make the bot say anything")
@app_commands.describe(
    message="The message the bot will say.",
    channel="(Optional) The channel to send the message in.")
async def speak(interaction: discord.Interaction,
                message: str,
                channel: discord.TextChannel = None):
    # Check if user has permissions or is the bot owner
    is_authorized = (interaction.user.guild_permissions.kick_members
                     or await bot.is_owner(interaction.user))

    if not is_authorized:
        await interaction.response.send_message(
            f"Nice try, {interaction.user.mention}, but you don't have permission to use this command.",
            ephemeral=True)
        return

    if channel:
        await interaction.response.defer(ephemeral=True)
        await channel.send(message)
        await interaction.followup.send(f"✅ Sent message ({message}) in {channel.mention}",
                                        ephemeral=True)
    else:
        await interaction.response.send_message(f"✅ Sent message ({message})",
                                                ephemeral=True)
        await interaction.channel.send(message)


@bot.tree.command(
    name="fight",
    description="Fight people using ANY custom move (just for fun)",
    )
@app_commands.describe(user="The user you want to attack",
                       attack="The attack you want to do")
async def fight(interaction: discord.Interaction, user: User, attack: str):
    if user.id == interaction.client.user.id:
        await interaction.response.send_message("😡 Hrmm! *punches you*")
    else:
        await interaction.response.send_message(
            f"{user.mention}! {interaction.user.mention} has done '{attack}' to you!"
        )


@bot.tree.command(name="coinflip", description="Flip a coin")
async def coinflip(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"The coin landed on {random.choice(['heads', 'tails'])}.")


@bot.tree.command(name="8ball", description="Ask the 8ball a question")
@app_commands.describe(question="The question you want to ask the 8ball")
async def eightball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.", "It is decidedly so.", "Without a doubt.",
        "Yes - definitely.", "You may rely on it.", "As I see it, yes.",
        "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.",
        "Better not tell you now.", "Cannot predict now.",
        "Concentrate and ask again.", "Don't count on it.", "My reply is no.",
        "My sources say no.", "Outlook not so good.", "Very doubtful.", "Absolutely not, you idiot.",
        "Obviously.", "I don't want to answer this question.", "No.", "h̵̡̨̛̺̲͍̞͇̳̹̪̽̐̃̇̀́̽̋̀͐̈͌̋̚̕͜͜͝͝a̷̹̺̪͎̬͉̟̹͖̦͚̖̓̏̕ͅh̵̡̳̗̲̲͍̺̙͎͈͚̱͈̽̐͒̀̈́͑̊̕̕̚ͅä̷̢̧̛̛̻̺̫̻̭̙͔͇̯̖̮̩̱̻̲͈̎̋̍͛͊̈̈̀́̋͗̌̒͘ḩ̴̞̞͓̘̖̱͚̼̣͍̤̯̻̣͖̭͈̊̌͑̉̆͗̾͒ą̵̦̹̬̼̘̭͕͈͍̠̹̰̪̻̳̮͚̓̋̽̚̚h̵̯̰̤̤̝̜͔̥̝̙̳̰͈̭̤̗̹̓͊̒̆̒ͅͅa̸̟̮̒̀̀̃̈́̿͑͆͠ẖ̸̠̝̣̋̇́̂̋͗̈́͋̒͆̕͜ͅͅḁ̴̭̗̗͖̩̳͚͎̈́̑͛̉̾̀͒͊̃̒́̏̒͐͂̓͜h̵̹̠̝̽ä̸̢̡̨̡̛͈̹̝͈̭̺̤͇̳̹̼̦̝́̇̒̋̓̀͌̈́̿͂͒̊̾̑͆͘͟͝ḩ̷̞͖̿̽͘a̷̦͉̦̼̞̱͗̆́̈̓̈̿̀̕͘͠h̶̨̨̡̨̛̝̞̭̣̖̗͖͕̰̠̻͍̝͚͗̄̄͐̏̌̌͆̅̀̓̉̈́̕a̸̡̙̲̥̙̪̖̲̘̣͍͖̬̱̐́̂̐͑̀̈́͒͌̓͂̍̄̚̕͝h̷̰̯͉̻̝͓̥̙̞̆͌̔̾̐̐͆́͂̒̀ą̷͍͎̮͙͈̥̬̜͉̫͋͛̒̈́̆̾̂̚͠ḧ̵̡̢̨͈͇͍̹̣͚̮͕̫̮́̎̊̈́͊͒́̈́͛͛̆͐͊̉̑̚͠͝͠ā̷̢͈̯̮͇̫̯͉̯̤̼͔̼̲̞̰̍́͐̄̐̆̐͑̍͆̅͋͊̀͑̕̕h̴͉̜̤̞͔̗͛̑̄́̾͆͋͒̿̎̈́ȁ̴̦͍͉͙͈̬͕̯̼̻̙̱̬̰̎̀̉̂̄̓̓h̸̡̫͍̳̘̠̖̥̞̜̯̠̲͌́̂̇͝ḁ̷͉͊̌̇̏̑̇̾̂̓̔̄̂͂̋̚̕"
    ]
    embed = discord.Embed(title="🎱 8ball 🎱", color=discord.Color.blue())
    embed.add_field(name="Question",
                    value=f"{interaction.user.mention} asked: '{question}'",
                    inline=False)
    embed.add_field(name="Answer",
                    value=f"The 8ball says: '{random.choice(responses)}'",
                    inline=False)
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="choice", description="Make the bot pick one out of a list of choices! (Max 5)")
@app_commands.describe(choice1="Choice 1",
                       choice2="Choice 2",
                       choice3="Choice 3",
                       choice4="Choice 4",
                       choice5="Choice 5")
async def choice(interaction: discord.Interaction,
                 choice1:str,
                 choice2:str,
                 choice3:str=None,
                 choice4:str=None,
                 choice5:str=None):
    choices = [c for c in [choice1, choice2, choice3, choice4, choice5] if c]
    await interaction.response.send_message(f"The bot has picked: {random.choice(choices)}")
    

@bot.tree.command(name="slap",
                  description="Slap someone!",
                  )
@app_commands.describe(user="The user who you want to slap.")
@app_commands.choices(tool=[
    app_commands.Choice(name="Hand", value="Hand"),
    app_commands.Choice(name="Fish", value="Fish"),
    app_commands.Choice(name="Sock", value="Sock")])
async def slap(interaction: discord.Interaction, user: Member, tool: app_commands.Choice[str]):
    if tool.value == "Hand":
        message = f"{user.mention}! {interaction.user.mention} slapped you! Are you going to retaliate?"
    elif tool.value in ["Fish", "Sock"]:
        message = f"{user.mention}! {interaction.user.mention} slapped you with a {tool.value}! Will you retaliate?"
    await interaction.response.send_message(message)


@bot.command()
@commands.is_owner()
async def dm(ctx, user: discord.User, *, message: str):
    try:
        await user.send(message)
    except discord.Forbidden:
        await ctx.send("❌ Cannot DM this user (DMs closed or blocked).")
    except Exception as e:
        await ctx.send(f"❌ Error sending DM: {e}")
        print("DM error:", e)
    else:
        await ctx.send("✅ Sent DM")

       
@bot.command()
@commands.is_owner()
async def sync(ctx):
   try:
        if not await bot.is_owner(ctx.author):
            await ctx.send("❌ You must be the bot's owner to use this command!")
            return

        print("🔄 Manual sync initiated")
        sync_msg = await ctx.send("🔄 Manual sync initiated, please wait...")
        synced_commands = await bot.tree.sync()
   
        await sync_msg.edit(content=f"✅ Successfully synced {len(synced_commands)} commands.")
        print(f"✅ Successfully synced {len(synced_commands)} commands.")

   except Exception as e:
        print(f"❌ Failed to sync commands: {e}") 
        await ctx.send(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(
            "Nice try, but you don't have permission to use this command.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        await ctx.send("An error occurred.")
        raise error

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Only log DMs; skip logging if owner sent the DM
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id == bot.owner_id:
            # don't log owner's DMs
            await bot.process_commands(message)
            return
        log_entry = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] The user '{message.author}' ({message.author.id}) DM'ed the bot: '{message.content}'\n"
        with open("message_logs.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

    # always process commands for non-bot messages
    await bot.process_commands(message)

bot.run(TOKEN)
