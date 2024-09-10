import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

# Laden der Umgebungsvariablen
load_dotenv()

# Logging konfigurieren
logging.basicConfig(level=logging.INFO)

# Überprüfen und Laden der Umgebungsvariablen
TEST_BOT = os.getenv("TEST_BOT")
GENERAL_CHANNEL_ID = os.getenv("GENERAL_CHANNEL_ID_TEST")
TEST_SERVER = int(os.getenv("TEST_SERVER"))
APPLICATION_ID = os.getenv("APPLICATION_ID_TEST")

if TEST_BOT is None:
    raise ValueError("Die Umgebungsvariable TEST_BOT ist nicht gesetzt.")
if GENERAL_CHANNEL_ID is None:
    raise ValueError("Die Umgebungsvariable GENERAL_CHANNEL_ID_TEST ist nicht gesetzt.")
if APPLICATION_ID is None:
    raise ValueError("Die Umgebungsvariable APPLICATION_ID ist nicht gesetzt.")
if TEST_SERVER is None:
    raise ValueError("Die Umgebungsvariable TEST_SERVER ist nicht gesetzt.")

GENERAL_CHANNEL_ID = int(GENERAL_CHANNEL_ID)
TEST_SERVER = int(TEST_SERVER)

# Festlegen der Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Aktivieren des members Intents

# Erstellen einer Bot-Instanz mit Kommandos
bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    application_id=APPLICATION_ID
)


@bot.event
async def on_ready():
    print(f"{bot.user} is online!")

    await bot.change_presence(activity=discord.Game(name="CoD"))

    # Sync commands globally for debugging
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} global command(s)")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(msg):
    if msg.author == bot.user:
        return
    await bot.process_commands(msg)  # Ermöglicht die Verarbeitung von Bot-Kommandos


async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and filename != "__init__.py":
            print(f"loaded Cog: {filename[:-3]}")
            await bot.load_extension(f"cogs.{filename[:-3]}")


# Laden der cogs
if __name__ == "__main__":
    async def main():
        await load_extensions()
        await bot.start(TEST_BOT)

    import asyncio
    asyncio.run(main())