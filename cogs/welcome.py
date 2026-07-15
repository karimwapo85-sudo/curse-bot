import discord
import sqlite3
from discord import app_commands
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_db_connection(self):
        return sqlite3.connect("database.db")

    @app_commands.command(name="config_welcome", description="Configure the welcome system channel.")
    @app_commands.describe(channel="The channel where welcome messages will be sent")
    @app_commands.checks.has_permissions(administrator=True)
    async def config_welcome(self, interaction: discord.Interaction, channel: discord.TextChannel):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO guilds (guild_id, welcome_channel_id)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET welcome_channel_id = excluded.welcome_channel_id
        """, (interaction.guild.id, channel.id))
        
        conn.commit()
        conn.close()
        
        await interaction.response.send_message(f"✅ Welcome channel successfully set to {channel.mention}", ephemeral=True)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT welcome_channel_id FROM guilds WHERE guild_id = ?", (member.guild.id,))
        result = cursor.fetchone()
        conn.close()

        if result and result[0]:
            channel_id = result[0]
            channel = member.guild.get_channel(channel_id)
            if channel:
                # El diseño ordenado, limpio y estructurado en inglés que querías
                embed = discord.Embed(
                    title="👋 WELCOME TO THE SERVER!",
                    description=f"Hello {member.mention}! We are absolutely thrilled to have you here in **{member.guild.name}**.\n\nPlease make sure to check out the rest of the channels and enjoy your stay!",
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="📌 What you can do here",
                    value="• Get support from our staff.\n• Stay updated with announcements.\n• Connect with other members.",
                    inline=False
                )
                
                embed.add_field(
                    name="📜 Before chatting",
                    value="• Read the rules carefully.\n• Keep conversations friendly and respectful.",
                    inline=False
                )
                
                embed.set_thumbnail(url=member.display_avatar.url)
                embed.set_footer(text=f"Member #{len(member.guild.members)} • Thank you for joining!")
                
                await channel.send(content=member.mention, embed=embed)

async def setup(bot):
    await bot.add_cog(Welcome(bot))