import os
import random
import datetime
from collections import defaultdict, deque

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

TOKEN = os.getenv("DISCORD_TOKEN") or os.getenv("TOKEN")
APPLICATION_ID = int(os.getenv("client_id")) if os.getenv("client_id") else None
PREFIX = os.getenv("DISCORD_PREFIX", "!")
GUILD_ID = os.getenv("GUILD_ID")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=PREFIX, intents=intents, application_id=APPLICATION_ID, help_command=None)


async def send_embed(ctx, title, description, color=discord.Color.blurple(), footer=None, delete_after=None, thumbnail=None, image=None, fields=None):
    embed = discord.Embed(title=title, description=description, color=color, timestamp=datetime.datetime.now(datetime.timezone.utc))
    if thumbnail:
        embed.set_thumbnail(url=thumbnail)
    else:
        embed.set_thumbnail(url=bot.user.display_avatar.url)
    if image:
        embed.set_image(url=image)
    if fields:
        for field_name, field_value, inline in fields:
            embed.add_field(name=field_name, value=field_value, inline=inline)
    if footer:
        embed.set_footer(text=footer, icon_url=bot.user.display_avatar.url)
    else:
        embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed, delete_after=delete_after)


# --- simple persistent config ---
# Welcome messages were removed for a simpler command set.

anti_raid_enabled = False
anti_spam_enabled = False
raid_join_times = deque()
spam_message_times = defaultdict(deque)
raid_threshold = 8
raid_window = 20
spam_threshold = 6
spam_window = 8


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user} ({bot.user.id})")
    print("Guilds:", [guild.id for guild in bot.guilds])
    try:
        synced_global = await bot.tree.sync()
        print(f"Slash commands synced globally ({len(synced_global)})")
    except Exception as exc:
        print(f"Error syncing slash commands globally: {exc}")


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await send_embed(ctx, "❌ Access denied", "You do not have permission to run this command.", color=discord.Color.red())
    elif isinstance(error, commands.MissingRequiredArgument):
        await send_embed(ctx, "⚠️ Missing argument", str(error), color=discord.Color.orange())
    elif isinstance(error, commands.BadArgument):
        await send_embed(ctx, "⚠️ Invalid input", "The provided argument is invalid.", color=discord.Color.orange())
    else:
        print(f"Error: {error}")


@bot.event
async def on_member_join(member):
    global anti_raid_enabled
    if not anti_raid_enabled or member.bot:
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    raid_join_times.append(now)
    while raid_join_times and (now - raid_join_times[0]).total_seconds() > raid_window:
        raid_join_times.popleft()

    if len(raid_join_times) >= raid_threshold:
        anti_raid_enabled = False
        try:
            if member.guild.system_channel:
                await member.guild.system_channel.send(
                    embed=discord.Embed(
                        title="🚨 Possible raid detected",
                        description="Protection is enabled and recent members were reviewed.",
                        color=discord.Color.red(),
                    )
                )
        except Exception:
            pass

        for target in member.guild.members:
            if target.bot:
                continue
            if target.joined_at is None:
                continue
            joined_delta = (now - target.joined_at).total_seconds()
            if 0 <= joined_delta <= raid_window:
                try:
                    await target.timeout(datetime.timedelta(minutes=10), reason="Anti-raid")
                except Exception:
                    pass



@bot.event
async def on_message(message):
    global anti_spam_enabled
    if message.author.bot or not message.guild or not anti_spam_enabled:
        await bot.process_commands(message)
        return

    now = datetime.datetime.now(datetime.timezone.utc)
    bucket = spam_message_times[message.author.id]
    bucket.append(now)
    while bucket and (now - bucket[0]).total_seconds() > spam_window:
        bucket.popleft()

    if len(bucket) >= spam_threshold:
        bucket.clear()
        try:
            await message.author.timeout(datetime.timedelta(minutes=5), reason="Anti-spam")
            await message.channel.send(
                embed=discord.Embed(
                    title="⛔ Spam detected",
                    description=f"{message.author.mention} was timed out for spam.",
                    color=discord.Color.red(),
                )
            )
        except Exception:
            pass

    await bot.process_commands(message)


@bot.hybrid_command(name="help", description="Shows the available commands")
async def bot_help(ctx):
    embed = discord.Embed(title="🤖 CurseBot Commands", color=discord.Color.blurple(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="🔧 Moderation", value="```/clear, /kick, /ban, /unban, /timeout, /untimeout, /warn, /giverole, /removerole```", inline=False)
    embed.add_field(name="🛡️ Protection", value="```/anti-raid, /setraidthreshold, /anti-spam, /setspamthreshold, /sync```", inline=False)
    embed.add_field(name="🛠️ Utility", value="```/ping, /serverinfo, /userinfo, /say, /avatar, /invite, /about, /roleinfo```", inline=False)
    embed.add_field(name="🎲 Fun", value="```/coinflip, /roll, /8ball```", inline=False)
    embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="ping", description="Measures the bot latency")
async def ping(ctx):
    await send_embed(ctx, "🏓 Pong", f"Latency: {round(bot.latency * 1000)}ms", color=discord.Color.blurple())


@bot.hybrid_command(name="serverinfo", description="Shows server information")
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title=f"📊 {guild.name}", color=discord.Color.green(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
    embed.add_field(name="👑 Owner", value=guild.owner.mention if guild.owner else "Unknown", inline=True)
    embed.add_field(name="👥 Members", value=str(guild.member_count), inline=True)
    embed.add_field(name="📅 Created", value=guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)
    embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="userinfo", description="Shows information about a user")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 {member}", color=discord.Color.orange(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_thumbnail(url=member.display_avatar.url)
    embed.add_field(name="🆔 ID", value=str(member.id), inline=True)
    embed.add_field(name="📅 Joined", value=member.joined_at.strftime("%d/%m/%Y") if member.joined_at else "Unknown", inline=True)
    embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)
    embed.add_field(name="🔗 Status", value=str(member.status).title(), inline=True)
    embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="say", description="Make the bot say something")
async def say(ctx, *, message: str):
    await send_embed(ctx, "💬 Message sent", message, color=discord.Color.green())


@bot.hybrid_command(name="coinflip", description="Flip a coin")
async def coinflip(ctx):
    result = "🪙 Heads" if random.choice([True, False]) else "🪙 Tails"
    await send_embed(ctx, "🎲 Coin flip", result, color=discord.Color.gold())


@bot.hybrid_command(name="roll", description="Generate a random number")
async def roll(ctx, max_value: int = 6):
    if max_value < 1:
        await send_embed(ctx, "⚠️ Invalid range", "The number must be greater than 0", color=discord.Color.orange())
        return
    await send_embed(ctx, "🎲 Random roll", f"Result: {random.randint(1, max_value)}", color=discord.Color.green())


@bot.hybrid_command(name="8ball", description="Answer a question")
async def eight_ball(ctx, *, question: str):
    responses = [
        "Yes",
        "No",
        "Definitely",
        "Maybe",
        "Ask again",
        "Looks promising",
    ]
    await send_embed(ctx, "🎱 Magic 8 Ball", f"{random.choice(responses)}", color=discord.Color.purple())


@bot.hybrid_command(name="avatar", description="Shows a user's avatar")
async def avatar(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"👤 Avatar of {member}", color=discord.Color.purple(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.set_image(url=member.display_avatar.url)
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="invite", description="Shows the bot invite link")
async def invite(ctx):
    invite_url = f"https://discord.com/oauth2/authorize?client_id={APPLICATION_ID}&permissions=8&scope=bot%20applications.commands"
    await send_embed(ctx, "🔗 Invite CurseBot", f"[Click here to invite me to your server]({invite_url})", color=discord.Color.blurple())


@bot.hybrid_command(name="about", description="Bot information")
async def about(ctx):
    await send_embed(ctx, "🤖 About CurseBot", "English moderation bot. Use /help for available commands.", color=discord.Color.teal())


@bot.hybrid_command(name="roleinfo", description="Shows information about a role")
async def roleinfo(ctx, role: discord.Role):
    embed = discord.Embed(title=f"🏷️ {role.name}", color=role.color if role.color != discord.Color.default() else discord.Color.blurple(), timestamp=datetime.datetime.now(datetime.timezone.utc))
    embed.add_field(name="🆔 ID", value=str(role.id), inline=True)
    embed.add_field(name="👥 Members", value=str(len(role.members)), inline=True)
    embed.add_field(name="🎨 Color", value=str(role.color), inline=True)
    embed.add_field(name="📍 Position", value=str(role.position), inline=True)
    embed.add_field(name="⭐ Mentionable", value="Yes" if role.mentionable else "No", inline=True)
    embed.set_footer(text=f"CurseBot • {ctx.author.name}", icon_url=bot.user.display_avatar.url)
    await ctx.send(embed=embed)


@bot.hybrid_command(name="clear", description="Delete messages from the channel")
@commands.has_permissions(manage_messages=True)
@app_commands.checks.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    if amount < 1 or amount > 100:
        await send_embed(ctx, "⚠️ Invalid amount", "Use a number between 1 and 100", color=discord.Color.orange())
        return
    await ctx.channel.purge(limit=amount + 1)
    await send_embed(ctx, "🧹 Messages cleared", f"Deleted {amount} messages.", color=discord.Color.green(), delete_after=5)


@bot.hybrid_command(name="kick", description="Kick a member")
@commands.has_permissions(kick_members=True)
@app_commands.checks.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = "No reason"):
    await member.kick(reason=reason)
    await send_embed(ctx, "👢 Member kicked", f"{member.mention} was kicked.\nReason: {reason}", color=discord.Color.red())


@bot.hybrid_command(name="ban", description="Ban a member")
@commands.has_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = "No reason"):
    await member.ban(reason=reason)
    await send_embed(ctx, "🔨 Member banned", f"{member.mention} was banned.\nReason: {reason}", color=discord.Color.red())


@bot.hybrid_command(name="unban", description="Unban a user")
@commands.has_permissions(ban_members=True)
@app_commands.checks.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    await ctx.guild.unban(user)
    await send_embed(ctx, "✅ Member unbanned", f"{user.mention} was unbanned.", color=discord.Color.green())


@bot.hybrid_command(name="timeout", description="Timeout a user for a few minutes")
@commands.has_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def timeout(ctx, member: discord.Member, minutes: int = 10, *, reason: str = "No reason"):
    if minutes < 1 or minutes > 10080:
        await send_embed(ctx, "⚠️ Invalid timeout", "Minutes must be between 1 and 10080", color=discord.Color.orange())
        return
    await member.timeout(datetime.timedelta(minutes=minutes), reason=reason)
    await send_embed(ctx, "⏱️ Member timed out", f"{member.mention} was timed out for {minutes} minutes.\nReason: {reason}", color=discord.Color.orange())


@bot.hybrid_command(name="untimeout", description="Remove timeout from a user")
@commands.has_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def untimeout(ctx, member: discord.Member):
    await member.remove_timeout()
    await send_embed(ctx, "✅ Timeout removed", f"Timeout removed from {member.mention}", color=discord.Color.green())


@bot.hybrid_command(name="warn", description="Warn a user")
@commands.has_permissions(moderate_members=True)
@app_commands.checks.has_permissions(moderate_members=True)
async def warn(ctx, member: discord.Member, *, reason: str = "No reason"):
    await send_embed(ctx, "⚠️ Warning issued", f"{member.mention} was warned.\nReason: {reason}", color=discord.Color.orange())


@bot.hybrid_command(name="giverole", description="Give a role to a user")
@commands.has_permissions(manage_roles=True)
@app_commands.checks.has_permissions(manage_roles=True)
async def giverole(ctx, member: discord.Member, role: discord.Role):
    if role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:
        await send_embed(ctx, "⚠️ Role restriction", "You cannot assign a role higher than your own.", color=discord.Color.orange())
        return
    await member.add_roles(role)
    await send_embed(ctx, "✅ Role assigned", f"Gave {role.mention} to {member.mention}", color=discord.Color.green())


@bot.hybrid_command(name="removerole", description="Remove a role from a user")
@commands.has_permissions(manage_roles=True)
@app_commands.checks.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    if role >= ctx.author.top_role and ctx.guild.owner_id != ctx.author.id:
        await send_embed(ctx, "⚠️ Role restriction", "You cannot remove a role higher than your own.", color=discord.Color.orange())
        return
    await member.remove_roles(role)
    await send_embed(ctx, "✅ Role removed", f"Removed {role.mention} from {member.mention}", color=discord.Color.green())


@bot.hybrid_command(name="anti-raid", description="Enable or disable anti-raid protection")
@commands.has_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def anti_raid(ctx, state: str = None):
    global anti_raid_enabled
    if state is None:
        await send_embed(ctx, "🛡️ Anti-raid", f"Current status: {'enabled' if anti_raid_enabled else 'disabled'}", color=discord.Color.blurple())
        return

    if state.lower() in {"on", "enable", "true", "enabled", "activate", "activated"}:
        anti_raid_enabled = True
        await send_embed(ctx, "🛡️ Anti-raid enabled", "Protection is now active.", color=discord.Color.green())
    else:
        anti_raid_enabled = False
        await send_embed(ctx, "🛡️ Anti-raid disabled", "Protection is now off.", color=discord.Color.orange())


@bot.hybrid_command(name="setraidthreshold", description="Change the anti-raid detection threshold")
@commands.has_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def set_raid_threshold(ctx, threshold: int):
    global raid_threshold
    if threshold < 2:
        await send_embed(ctx, "⚠️ Invalid threshold", "The threshold must be 2 or higher", color=discord.Color.orange())
        return
    raid_threshold = threshold
    await send_embed(ctx, "✅ Threshold updated", f"Anti-raid threshold updated to {threshold}", color=discord.Color.green())


@bot.hybrid_command(name="anti-spam", description="Enable or disable anti-spam protection")
@commands.has_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def anti_spam(ctx, state: str = None):
    global anti_spam_enabled
    if state is None:
        await send_embed(ctx, "🛡️ Anti-spam", f"Current status: {'enabled' if anti_spam_enabled else 'disabled'}", color=discord.Color.blurple())
        return

    if state.lower() in {"on", "enable", "true", "enabled", "activate", "activated"}:
        anti_spam_enabled = True
        await send_embed(ctx, "🛡️ Anti-spam enabled", "Protection is now active.", color=discord.Color.green())
    else:
        anti_spam_enabled = False
        await send_embed(ctx, "🛡️ Anti-spam disabled", "Protection is now off.", color=discord.Color.orange())


@bot.hybrid_command(name="setspamthreshold", description="Change the anti-spam detection threshold")
@commands.has_permissions(administrator=True)
@app_commands.checks.has_permissions(administrator=True)
async def set_spam_threshold(ctx, threshold: int):
    global spam_threshold
    if threshold < 2:
        await send_embed(ctx, "⚠️ Invalid threshold", "The threshold must be 2 or higher", color=discord.Color.orange())
        return
    spam_threshold = threshold
    await send_embed(ctx, "✅ Threshold updated", f"Anti-spam threshold updated to {threshold}", color=discord.Color.green())


@bot.hybrid_command(name="sync", description="Manually sync slash commands")
@commands.has_permissions(administrator=True)
async def sync(ctx):
    if GUILD_ID:
        guild_obj = discord.Object(id=int(GUILD_ID))
        synced = await bot.tree.sync(guild=guild_obj)
        await send_embed(ctx, "🔄 Slash commands synced", f"Synced {len(synced)} command(s) for this server.", color=discord.Color.blurple())
    else:
        synced = await bot.tree.sync()
        await send_embed(ctx, "🔄 Slash commands synced", f"Synced {len(synced)} command(s) globally.", color=discord.Color.blurple())


if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Discord token not found. Check your .env file")
    bot.run(TOKEN)
