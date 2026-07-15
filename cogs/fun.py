import discord
import random
import sqlite3
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_lang(self, guild_id):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("SELECT language FROM guilds WHERE guild_id = ?", (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else "en"

    @app_commands.command(name="8ball", description="Ask the magic 8ball a question.")
    async def magic_8ball(self, interaction: discord.Interaction, question: str):
        lang = self.get_lang(interaction.guild.id)
        
        if lang == "es":
            responses = ["En mi opinión, sí. 🟢", "Sin duda. 🟢", "Prueba otra vez más tarde. 🟡", "Mi respuesta es no. 🔴", "Muy dudoso. 🔴"]
            title, q_field, a_field = "🔮 La Bola Mágica 8", "Pregunta:", "Respuesta:"
        else:
            responses = ["It is certain. 🟢", "Without a doubt. 🟢", "Reply hazy, try again. 🟡", "My reply is no. 🔴", "Very doubtful. 🔴"]
            title, q_field, a_field = "🔮 The Magic 8-Ball", "Question:", "Answer:"

        embed = discord.Embed(title=title, color=discord.Color.purple())
        embed.add_field(name=q_field, value=question, inline=False)
        embed.add_field(name=a_field, value=random.choice(responses), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get the avatar of a user.")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        lang = self.get_lang(interaction.guild.id)
        member = member or interaction.user
        
        title = f"🖼️ Avatar de {member.name}" if lang == "es" else f"🖼️ {member.name}'s Avatar"
        
        embed = discord.Embed(title=title, color=discord.Color.blue())
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))