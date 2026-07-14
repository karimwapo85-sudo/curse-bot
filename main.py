import os
import random
import datetime
import discord
from discord.ext import commands
from keep_alive import keep_alive

# 1. START INVISIBLE WEB SERVER (To prevent Render from shutting down the bot)
keep_alive()

# 2. CONFIGURE PERMISSIONS (Intents)
intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to read message content
intents.members = True          # Allows detecting when members join/leave

# 3. CREATE BOT INSTANCE (Prefix '!' for commands)
bot = commands.Bot(command_prefix="!", intents=intents, help_command=None)


# ==============================================================================
# MAIN EVENTS
# ==============================================================================

@bot.event
async def on_ready():
    """Runs when the bot successfully connects to Discord."""
    print("=========================================")
    print(f" Bot successfully connected!")
    print(f" Bot username: {bot.user.name}")
    print(f" Bot ID: {bot.user.id}")
    print("=========================================")
    
    # --------------------------------------------------------------------------
    # ESTADO DEL BOT (ACTIVITY / STATUS)
    # Aquí puedes cambiar el estado del bot. Actualmente dice: "Listening to !help"
    # --------------------------------------------------------------------------
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="!help"
    ))


@bot.event
async def on_member_join(member):
    """Runs automatically when a new user joins the server."""
    channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if not channel:
        channel = discord.utils.get(member.guild.text_channels, name="general")
        
    if channel:
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}! 🎉",
            description=f"Hey {member.mention}, we are super excited to have you here! Have a great time.",
            color=discord.Color.green(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
        embed.set_footer(text=f"Member #{len(member.guild.members)}")
        await channel.send(embed=embed)


@bot.event
async def on_member_remove(member):
    """Runs when a user leaves the server."""
    channel = discord.utils.get(member.guild.text_channels, name="goodbyes")
    if not channel:
        channel = discord.utils.get(member.guild.text_channels, name="general")
        
    if channel:
        await channel.send(f"😢 **{member.name}** has left the server. We will miss you!")


# ==============================================================================
# CUSTOM HELP SYSTEM
# ==============================================================================

@bot.command()
async def help(ctx):
    """Displays the list of available commands organized by category."""
    embed = discord.Embed(
        title="🤖 Help Panel - Curse Bot",
        description="Here is the complete list of commands you can use on this server.",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛡️ Moderation (Admins Only)",
        value="`!kick @user [reason]` - Kicks a member.\n"
              "`!ban @user [reason]` - Bans a member.\n"
              "`!clear [number]` - Clears chat messages.",
        inline=False
    )
    
    embed.add_field(
        name="⚙️ Utility",
        value="`!ping` - Shows the bot's latency.\n"
              "`!userinfo @user` - Information about a member.\n"
              "`!serverinfo` - Information about this server.\n"
              "`!avatar @user` - Shows someone's profile picture.",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Fun",
        value="`!dice` - Rolls a 6-sided die.\n"
              "`!coin` - Flips a coin (Heads or Tails).\n"
              "`!ask [question]` - Ask the Magic 8-Ball a question.",
        inline=False
    )
    
    embed.set_footer(text="Use the '!' prefix before each command.")
    await ctx.send(embed=embed)


# ==============================================================================
# MODERATION COMMANDS (Require special permissions)
# ==============================================================================

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    """Kicks a user from the server."""
    if reason is None:
        reason = "No reason was specified."
    await member.kick(reason=reason)
    await ctx.send(f"✅ **{member.name}** has been kicked. Reason: *{reason}*")


@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    """Bans a user from the server."""
    if reason is None:
        reason = "No reason was specified."
    await member.ban(reason=reason)
    await ctx.send(f"🚨 **{member.name}** has been permanently banned. Reason: *{reason}*")


@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Clears a specific amount of messages from the chat."""
    if amount < 1:
        await ctx.send("You must clear at least 1 message!")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"🧹 Successfully cleared **{len(deleted) - 1}** messages.", delete_after=5)


# ==============================================================================
# UTILITY COMMANDS
# ==============================================================================

@bot.command()
async def ping(ctx):
    """Displays the current bot latency."""
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 **Pong!** My latency is **{latency}ms**.")


@bot.command()
async def avatar(ctx, member: discord.Member = None):
    """Displays the avatar of the mentioned user, or the author if none is mentioned."""
    if member is None:
        member = ctx.author
        
    avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
    
    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.purple()
    )
    embed.set_image(url=avatar_url)
    await ctx.send(embed=embed)


@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    """Displays detailed information about a user."""
    if member is None:
        member = ctx.author
        
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]
    
    embed = discord.Embed(title=f"👤 Information for {member.name}", color=member.color)
    embed.set_thumbnail(url=member.avatar.url if member.avatar else member.default_avatar.url)
    embed.add_field(name="Nickname:", value=member.nick if member.nick else "None", inline=True)
    embed.add_field(name="User ID:", value=member.id, inline=True)
    embed.add_field(name="Is Bot?:", value="Yes" if member.bot else "No", inline=True)
    embed.add_field(name="Account Created:", value=member.created_at.strftime("%m/%d/%Y"), inline=True)
    embed.add_field(name="Joined Server:", value=member.joined_at.strftime("%m/%d/%Y"), inline=True)
    embed.add_field(name=f"Roles ({len(roles)}):", value=" ".join(roles) if roles else "No roles", inline=False)
    
    await ctx.send(embed=embed)


@bot.command()
async def serverinfo(ctx):
    """Displays information about the server where it's executed."""
    guild = ctx.guild
    embed = discord.Embed(
        title=f"🏰 Server Info - {guild.name}",
        color=discord.Color.gold()
    )
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
        
    embed.add_field(name="Owner:", value=f"<@{guild.owner_id}>", inline=True)
    embed.add_field(name="Server ID:", value=guild.id, inline=True)
    embed.add_field(name="Created On:", value=guild.created_at.strftime("%m/%d/%Y"), inline=True)
    embed.add_field(name="Total Members:", value=guild.member_count, inline=True)
    embed.add_field(name="Text Channels:", value=len(guild.text_channels), inline=True)
    embed.add_field(name="Voice Channels:", value=len(guild.voice_channels), inline=True)
    
    await ctx.send(embed=embed)


# ==============================================================================
# FUN COMMANDS
# ==============================================================================

@bot.command()
async def dice(ctx):
    """Rolls a 6-sided die."""
    result = random.randint(1, 6)
    await ctx.send(f"🎲 You rolled a: **{result}**")


@bot.command()
async def coin(ctx):
    """Flips a coin."""
    options = ["Heads 🪙", "Tails ❌"]
    result = random.choice(options)
    await ctx.send(f"🪙 Flapped a coin and got: **{result}**")


@bot.command()
async def ask(ctx, *, question: str):
    """Answers Yes/No questions like a Magic 8-Ball."""
    answers = [
        "Yes, definitely. 👍",
        "It is highly likely. 😎",
        "All signs point to yes. ✨",
        "Don't count on it. 👎",
        "My reply is a definite no. ❌",
        "Very doubtful. 🥶",
        "Ask again later... 🤫",
        "Better not tell you now. 🤔"
    ]
    chosen_answer = random.choice(answers)
    await ctx.send(f"🔮 **Question:** {question}\n💬 **8-Ball:** {chosen_answer}")


# ==============================================================================
# ERROR HANDLER (Prevents the bot from crashing on user input errors)
# ==============================================================================

@bot.event
async def on_command_error(ctx, error):
    """Runs automatically when a command fails."""
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You do not have the required permissions to use this command.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("⚠️ Missing required arguments for this command.")
    elif isinstance(error, commands.CommandNotFound):
        pass
    else:
        print(f"Error detected: {error}")


# ==============================================================================
# BOT RUN
# ==============================================================================

token = os.environ.get("DISCORD_TOKEN")

if token:
    bot.run(token)
else:
    print("----------------------------------------------------------------------")
    print("FATAL ERROR: 'DISCORD_TOKEN' variable not detected.")
    print("Make sure you added it correctly in your Render dashboard settings.")
    print("----------------------------------------------------------------------")