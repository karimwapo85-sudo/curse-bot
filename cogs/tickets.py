import discord
import asyncio
from discord import app_commands
from discord.ext import commands

class TicketPanelView(discord.ui.View):
    def __init__(self, button_text="Create Ticket 🎫"):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(
            label=button_text,
            style=discord.ButtonStyle.blurple,
            custom_id="create_ticket_btn"
        ))

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close Ticket 🔒", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("This ticket will be closed and deleted in 5 seconds...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketControlView())

    @app_commands.command(name="setup_tickets", description="Create a customizable support panel.")
    @app_commands.describe(
        title="The title shown on the panel",
        description="The description helper on the panel",
        button_text="The text inside the ticket button"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction, title: str, description: str, button_text: str = "Create Ticket 🎫"):
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.purple()
        )
        
        view = TicketPanelView(button_text=button_text)
        await interaction.response.send_message("Support panel deployed successfully.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.data and interaction.data.get("custom_id") == "create_ticket_btn":
            guild = interaction.guild
            member = interaction.user
            
            existing_channel = discord.utils.get(guild.text_channels, name=f"ticket-{member.name.lower()}")
            if existing_channel:
                await interaction.response.send_message(f"⚠️ You already have an open ticket here: {existing_channel.mention}", ephemeral=True)
                return

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }

            category = interaction.channel.category
            channel = await guild.create_text_channel(
                name=f"ticket-{member.name}",
                category=category,
                overwrites=overwrites,
                topic=f"Support ticket open by {member.name}"
            )

            embed = discord.Embed(
                title="🎫 Support Ticket",
                description=f"Hello {member.mention}, please describe your issue in detail.\nUse the button below to close this ticket.",
                color=discord.Color.blue()
            )
            await channel.send(embed=embed, view=TicketControlView())
            await interaction.response.send_message(f"✅ Your ticket has been created at {channel.mention}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))