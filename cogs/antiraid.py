import discord
import sqlite3
import datetime
from discord import app_commands
from discord.ext import commands

class AntiRaid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.channel_creations = {}

    def get_db_connection(self):
        return sqlite3.connect("database.db")

    @app_commands.command(name="antiraid_toggle", description="Enable or disable the anti-raid security system.")
    @app_commands.checks.has_permissions(administrator=True)
    async def antiraid_toggle(self, interaction: discord.Interaction):
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT antiraid_active FROM guilds WHERE guild_id = ?", (interaction.guild.id,))
        result = cursor.fetchone()
        
        current_state = result[0] if result else 0
        new_state = 1 if current_state == 0 else 0
        
        cursor.execute("""
            INSERT INTO guilds (guild_id, antiraid_active)
            VALUES (?, ?)
            ON CONFLICT(guild_id) DO UPDATE SET antiraid_active = excluded.antiraid_active
        """, (interaction.guild.id, new_state))
        
        conn.commit()
        conn.close()

        status_text = "🟢 **ENABLED**" if new_state == 1 else "🔴 **DISABLED**"
        embed = discord.Embed(
            title="🛡️ Anti-Raid System Status",
            description=f"The anti-raid security is now: {status_text}.",
            color=discord.Color.blue() if new_state == 1 else discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        guild = channel.guild
        conn = self.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT antiraid_active FROM guilds WHERE guild_id = ?", (guild.id,))
        result = cursor.fetchone()
        conn.close()

        if not result or result[0] == 0:
            return

        now = datetime.datetime.now(datetime.timezone.utc)
        if guild.id not in self.channel_creations:
            self.channel_creations[guild.id] = []
        
        self.channel_creations[guild.id].append(now)
        self.channel_creations[guild.id] = [t for t in self.channel_creations[guild.id] if (now - t).total_seconds() < 10]
        
        if len(self.channel_creations[guild.id]) > 4:
            async for entry in guild.audit_logs(action=discord.AuditLogAction.channel_create, limit=1):
                attacker = entry.user
                if attacker.id != self.bot.user.id:
                    alert_channel = discord.utils.get(guild.text_channels, name="general")
                    if alert_channel:
                        embed = discord.Embed(
                            title="🚨 ANTI-RAID TRIGGERED",
                            description=f"Mass channel creation detected! Initiated by {attacker.mention}.\n**Recommended action:** Remove their administrative roles immediately.",
                            color=discord.Color.red()
                        )
                        await alert_channel.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AntiRaid(bot))