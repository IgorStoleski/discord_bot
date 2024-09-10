import discord
import os
from dotenv import load_dotenv
from discord.ext import commands

load_dotenv()
LOST_BOT = os.getenv('LOST_BOT')
GENERAL_CHANNEL_ID = os.getenv('GENERAL_CHANNEL_ID')
LOST_SERVER = os.getenv("LOST_SERVER")
APPLICATION_ID = os.getenv("APPLICATION_ID")

if LOST_BOT is None:
    raise ValueError("Die Umgebungsvariable LOST_BOT ist nicht gesetzt.")
if GENERAL_CHANNEL_ID is None:
    raise ValueError("Die Umgebungsvariable GENERAL_CHANNEL_ID ist nicht gesetzt.")
if APPLICATION_ID is None:
    raise ValueError("Die Umgebungsvariable APPLICATION_ID ist nicht gesetzt.")

GENERAL_CHANNEL_ID = int(GENERAL_CHANNEL_ID)
LOST_SERVER = int(LOST_SERVER)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
	command_prefix="!",
	intents=intents,
	debug_guilds=[LOST_SERVER],
	application_id=APPLICATION_ID
)


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")
    await bot.change_presence(activity=discord.Game(name="Hill Climb Racing 2"))
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    await bot.process_commands(msg)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            print(f"loaded Cog: {filename[:-3]}")
            await bot.load_extension(f"cogs.{filename[:-3]}")

if __name__ == "__main__":
    async def main():
        await load_extensions()
        await bot.start(LOST_BOT)

    import asyncio
    asyncio.run(main())