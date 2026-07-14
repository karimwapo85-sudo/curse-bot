import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_db_connection(self):
        return sqlite3.connect("database.db")

    @app_commands.command(name="config_welcome", description="Configure the welcome system for your server.")
    @app_commands.describe(
        channel="The channel where welcome messages will be sent",
        message="Custom message. Use '{user}' to mention the joining user."
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def config_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel, message: str):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO guilds (guild_id, welcome_channel_id, welcome_message)
            VALUES (?, ?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET 
                welcome_channel_id = excluded.welcome_channel_id,
                welcome_message = excluded.welcome_message
        """, (interaction.guild.id, channel.id, message))
        
        conn.commit()
        conn.close()
        
        embed = discord.Embed(
            title="✅ Configuration Saved",
            description=f"Welcome channel set to {channel.mention}.\n**Preview:**\n{message.replace('{user}', interaction.user.mention)}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT welcome_channel_id, welcome_message FROM guilds WHERE guild_id = ?", (member.guild.id,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            channel_id, message_template = result
            channel = member.guild.get_channel(channel_id)
            if channel:
                formatted_message = message_template.replace("{user}", member.mention)
                
                embed = discord.Embed(
                    title="👋 A new member has arrived!",
                    description=formatted_message,
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member #{len(member.guild.members)}")
                await channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))