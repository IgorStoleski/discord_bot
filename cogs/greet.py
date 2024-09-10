import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Laden der Umgebungsvariablen
load_dotenv()
GENERAL_CHANNEL_ID = int(os.getenv("GENERAL_CHANNEL_ID_TEST"))

class Greet(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #(name="greet", description="Begrüßt den Benutzer.")
    #async def greet(self, interaction: discord.Interaction):
    #    """Begrüßt den Benutzer, der den Befehl ausgeführt hat."""
    #    await interaction.response.send_message(f"Hey {interaction.user.mention}")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild = member.guild
        embed = discord.Embed(
            title="Willkommen",
            description=f"""
            Willkommen bei den {guild.name}, {member.mention}!
            Ändere deinen Name auf diesem Server in deinen Spielernamen.
            In der nächsten Nachricht wird Dir eine schnelle möglikeit erklärt!""",
            color=discord.Color.orange()
        )

        nickname = discord.Embed(
            title="Servernamen ändern",
            description=f"""
                    Hallo {member.mention}!
                    so kannst Du deinen Servernamen für {guild.name} anzupassen:
                    1) /nick 
                    2) new_nick
                    3) dann deinen Spielernamen eingeben
                    """,
            color=discord.Color.yellow()
        )

        channel = await self.bot.fetch_channel(GENERAL_CHANNEL_ID)
        await channel.send(embed=embed)
        await channel.send(embed=nickname)


async def setup(bot):
    await bot.add_cog(Greet(bot))