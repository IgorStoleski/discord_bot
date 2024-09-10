import sqlite3
import discord
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

CONTEST_CHANNEL = int(os.getenv("CONTEST_CHANNEL"))



# Funktion zum Laden des Leaderboards aus der SQLite-Datenbank
def load_leaderboard():
    print("Lade Leaderboard...")
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, points FROM leaderboard ORDER BY points DESC')
    leaderboard = cursor.fetchall()
    conn.close()
    print("Leaderboard geladen.")
    return leaderboard

# Funktion zum Hinzufügen oder Aktualisieren eines Eintrags im Leaderboard
def update_leaderboard(name, points):
    name = name.lower()  # Namen in Kleinbuchstaben konvertieren
    print(f"Aktualisiere Leaderboard für {name} mit {points} Punkten...")
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('SELECT points FROM leaderboard WHERE name = ?', (name,))
    result = cursor.fetchone()
    if result:
        new_points = result[0] + points
        cursor.execute('UPDATE leaderboard SET points = ? WHERE name = ?', (new_points, name))
    else:
        cursor.execute('INSERT INTO leaderboard (name, points) VALUES (?, ?)', (name, points))
    conn.commit()
    conn.close()
    print("Leaderboard aktualisiert.")

# Funktion zum Zurücksetzen der Datenbank
def reset_database():
    if os.path.exists('leaderboard.db'):
        os.remove('leaderboard.db')
        print("Datenbank wurde zurückgesetzt.")
    else:
        print("Datenbankdatei existiert nicht.")

# Alternative Funktion zum Zurücksetzen der Datenbank ohne Löschen der Datei
def reset_database_and_recreate():
    conn = sqlite3.connect('leaderboard.db')
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS leaderboard')
    cursor.execute('''
        CREATE TABLE leaderboard (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            points INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
    print("Datenbank wurde zurückgesetzt und Tabelle neu erstellt.")


# Benutzerdefinierte Überprüfung für Admin und Mod Berechtigungen
def is_admin_or_mod():
    async def predicate(interaction: discord.Interaction) -> bool:
        guild = interaction.guild
        if guild is None:
            print("Interaktion ist nicht auf einem Server.")
            return False

        # Überprüfen, ob der Benutzer Administrator ist
        if interaction.user.guild_permissions.administrator:
            print(f"Benutzer {interaction.user} ist Administrator.")
            return True

        # Überprüfen, ob der Benutzer die Rolle "Mod" hat
        mod_role = discord.utils.get(guild.roles, name="Mod")
        if mod_role in interaction.user.roles:
            print(f"Benutzer {interaction.user} hat die Mod-Rolle.")
            return True

        print(f"Benutzer {interaction.user} hat weder Administratorrechte noch die Mod-Rolle.")
        return False

    return app_commands.check(predicate)


# Benutzerdefinierte Überprüfung für Serverbesitzer oder Administrator
def is_owner_or_admin():
    async def predicate(interaction: discord.Interaction) -> bool:
        guild = interaction.guild
        if guild is None:
            print("Interaktion ist nicht auf einem Server.")
            return False

        # Überprüfen, ob der Benutzer der Besitzer des Servers ist
        if interaction.user.id == guild.owner_id:
            print(f"Benutzer {interaction.user} ist der Besitzer des Servers.")
            return True

        # Überprüfen, ob der Benutzer Administrator ist
        if interaction.user.guild_permissions.administrator:
            print(f"Benutzer {interaction.user} ist Administrator.")
            return True

        print(f"Benutzer {interaction.user} hat weder Administratorrechte noch ist er der Besitzer des Servers.")
        return False

    return app_commands.check(predicate)

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        print("Leaderboard Cog wurde initialisiert")

    @app_commands.command(name='leaderboard', description="Zeigt das Leaderboard an")
    @commands.cooldown(3, 30 * 60, commands.BucketType.user)
    async def leaderboard_command(self, interaction: discord.Interaction):
        leaderboard = load_leaderboard()
        message = "Platzierungen und Punktestand:\n"
        for idx, entry in enumerate(leaderboard):
            message += f"{idx + 1}. {entry[0].capitalize()} - {entry[1]} Punkte\n"
        await self.send_to_channel(CONTEST_CHANNEL, message)
        await interaction.response.send_message("Das Leaderboard wurde im contest Channel gepostet.",
                                                ephemeral=True)


    @staticmethod
    def convert_time(seconds):
        if seconds < 60:
            return f"{round(seconds)} Sekunden"

        minutes = seconds // 60
        if minutes < 60:
            return f"{round(minutes)} Minuten"

        hours = minutes // 60
        return f"{round(hours)} Stunden"

    @leaderboard_command.error
    async def leaderboard_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.CommandOnCooldown):
            retry_after = error.retry_after
            final_time = self.convert_time(retry_after)
            await interaction.response.send_message(
                f"Dieses Kommando ist im Moment deaktiviert. Bitte versuche es in {final_time} erneut.",
                ephemeral=True
            )
    @app_commands.command(name='addpoints', description="Fügt einem Benutzer Punkte hinzu")
    @is_admin_or_mod()
    async def addpoints_command(self, interaction: discord.Interaction, name: str, points: int):
        print(f"Füge {points} Punkte zu {name} hinzu...")
        update_leaderboard(name, points)
        await interaction.response.send_message(f"{points} Punkte wurden zu {name} hinzugefügt.")
        print("Punkte hinzugefügt.")

    @addpoints_command.error
    async def addpoints_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Du hast nicht die nötigen Berechtigungen, um dieses Kommando auszuführen.")
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Du hast weder Administratorrechte noch die Mod-Rolle, um dieses Kommando auszuführen.")
        else:
            print(f"Fehler: {error}")
            await interaction.response.send_message(f"Ein Fehler ist aufgetreten: {error}")


    @app_commands.command(name='resetdb', description="Setzt die Datenbank zurück")
    @is_owner_or_admin()
    async def resetdb_command(self, interaction: discord.Interaction):
        reset_database_and_recreate()
        await interaction.response.send_message("Datenbank wurde zurückgesetzt.")

    @resetdb_command.error
    async def resetdb_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message(
                "Du hast nicht die nötigen Berechtigungen, um dieses Kommando auszuführen.")
        elif isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Nur der Serverbesitzer oder ein Administrator kann dieses Kommando ausführen.")
        else:
            print(f"Fehler: {error}")
            await interaction.response.send_message(f"Ein Fehler ist aufgetreten: {error}")

        # Beispiel für das Senden einer Nachricht an einen bestimmten Channel

    async def send_to_channel(self, channel_id: int, message: str):
        channel = self.bot.get_channel(CONTEST_CHANNEL)
        if channel:
            await channel.send(message)
        else:
            print(f"Konnte Channel mit ID {channel_id} nicht finden")


async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
    print("Leaderboard Cog wurde geladen")