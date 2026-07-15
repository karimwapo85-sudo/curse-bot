import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_lang(self, guild_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "en"

    @app_commands.command(name="clear", description="Clear messages.")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        lang = self.get_lang(interaction.guild.id)
        await interaction.channel.purge(limit=amount)
        
        msg = f"🗑️ Se han eliminado {amount} mensajes." if lang == "es" else f"🗑️ Cleared {amount} messages."
        await interaction.response.send_message(msg, ephemeral=True)

    @app_commands.command(name="ban", description="Ban a member.")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason"):
        lang = self.get_lang(interaction.guild.id)
        await member.ban(reason=reason)
        
        msg = f"🔴 {member.mention} ha sido baneado. Razón: {reason}" if lang == "es" else f"🔴 {member.mention} has been banned. Reason: {reason}"
        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(Moderation(bot))