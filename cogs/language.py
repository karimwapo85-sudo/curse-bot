import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_db_connection(self):
        return sqlite3.connect("database.db")

    @app_commands.command(name="language", description="Change the bot's language for this server / Cambia el idioma del bot.")
    @app_commands.describe(lang="Choose 'en' for English or 'es' for Español")
    @app_commands.choices(lang=[
        app_commands.Choice(name="English 🇺🇸", value="en"),
        app_commands.Choice(name="Español 🇪🇸", value="es")
    ])
    @app_commands.checks.has_permissions(administrator=True)
    async def change_language(self, interaction: discord.Interaction, lang: app_commands.Choice[str]):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # Guarda o actualiza el idioma del servidor en la base de datos
        cursor.execute("""
            INSERT INTO guilds (guild_id, language)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET language = excluded.language
        """, (interaction.guild.id, lang.value))
        
        conn.commit()
        conn.close()

        # Respuesta en el idioma correcto según la elección del usuario
        if lang.value == "es":
            await interaction.response.send_message("¡Idioma cambiado a Español correctamente! 🇪🇸", ephemeral=True)
        else:
            await interaction.response.send_message("Language set to English successfully! 🇺🇸", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Language(bot))