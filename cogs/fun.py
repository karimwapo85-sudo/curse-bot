import discord
import random
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="avatar", description="Get the avatar of a user.")
    @app_commands.describe(user="The user whose avatar you want to see (leave blank for yours)")
    async def avatar(self, interaction: discord.Interaction, user: discord.Member = None):
        member = user or interaction.user
        embed = discord.Embed(
            title=f"🖼️ {member.name}'s Avatar",
            color=discord.Color.random()
        )
        embed.set_image(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8ball a question.")
    @app_commands.describe(question="The question you want to ask")
    async def eight_ball(self, interaction: discord.Interaction, question: str):
        replies = [
            "In my opinion, yes. 🟢",
            "It is decidedly so. 🟢",
            "Without a doubt. 🟢",
            "Yes definitely. 🟢",
            "Ask again later. 🟡",
            "Better not tell you now... 🟡",
            "Don't count on it. 🔴",
            "My reply is no. 🔴",
            "My sources say no. 🔴",
            "Very doubtful. 🔴"
        ]
        
        embed = discord.Embed(
            title="🔮 The Magic 8-Ball",
            color=discord.Color.dark_purple()
        )
        embed.add_field(name="Question:", value=question, inline=False)
        embed.add_field(name="Answer:", value=random.choice(replies), inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))