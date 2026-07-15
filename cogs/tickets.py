import discord
import sqlite3
import asyncio
from discord import app_commands
from discord.ext import commands

def get_server_lang(guild_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT language FROM guilds WHERE guild_id = ?", (guild_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else "en"

class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="🔒 Close / Cerrar", style=discord.ButtonStyle.red, custom_id="tk_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_server_lang(interaction.guild.id)
        msg = "⚙️ Este ticket se eliminará permanentemente en 5 segundos..." if lang == "es" else "⚙️ This ticket will be permanently deleted in 5 seconds..."
        await interaction.response.send_message(msg, ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="🙋‍♂️ Claim / Reclamar", style=discord.ButtonStyle.green, custom_id="tk_claim")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        lang = get_server_lang(interaction.guild.id)
        staff_member = interaction.user
        
        for child in self.children:
            if child.custom_id == "tk_claim":
                child.disabled = True
                child.label = f"Claimed by {staff_member.name}" if lang == "en" else f"Reclamado por {staff_member.name}"
                child.style = discord.ButtonStyle.grey

        await interaction.channel.edit(topic=f"Ticket claimed by {staff_member.mention}")
        
        title = "🎯 Ticket Reclamado" if lang == "es" else "🎯 Ticket Claimed"
        desc = f"Este ticket de soporte ahora es manejado por {staff_member.mention}." if lang == "es" else f"This support ticket is now being handled by {staff_member.mention}."
        
        embed = discord.Embed(title=title, description=desc, color=discord.Color.green())
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(embed=embed)

class DynamicTicketButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, custom_id: str, category_name: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.category_name = category_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        lang = get_server_lang(guild.id)
        
        clean_channel_name = f"ticket-{self.category_name.lower()}-{member.name.lower()}".replace(" ", "-")
        existing_channel = discord.utils.get(guild.text_channels, name=clean_channel_name)
        
        if existing_channel:
            msg = f"⚠️ Ya tienes un ticket abierto aquí: {existing_channel.mention}" if lang == "es" else f"⚠️ You already have an open ticket here: {existing_channel.mention}"
            await interaction.response.send_message(msg, ephemeral=True)
            return

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        channel = await guild.create_text_channel(name=clean_channel_name, category=interaction.channel.category, overwrites=overwrites)

        embed = discord.Embed(title=f"🎫 TICKET — {self.category_name.upper()}", color=discord.Color.blue())
        
        if lang == "es":
            embed.add_field(name="Bienvenido", value=f"Hola {member.mention}, gracias por abrir un ticket.", inline=False)
            embed.add_field(name="Consulta", value="Por favor, detalla tu problema abajo. El staff te atenderá pronto.", inline=False)
        else:
            embed.add_field(name="Welcome", value=f"Hello {member.mention}, thank you for opening a ticket.", inline=False)
            embed.add_field(name="Inquiry", value="Please describe your issue below. Our support team will assist you shortly.", inline=False)
            
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(content=f"{member.mention}", embed=embed, view=TicketControlView())
        
        ok_msg = f"✅ Tu ticket ha sido creado en {channel.mention}" if lang == "es" else f"✅ Your ticket has been created at {channel.mention}"
        await interaction.response.send_message(ok_msg, ephemeral=True)

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(TicketControlView())

    @app_commands.command(name="setup_tickets", description="Create a support panel.")
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(self, interaction: discord.Interaction, panel_title: str, panel_description: str, option1_name: str):
        embed = discord.Embed(title=f"📥 {panel_title.upper()}", color=discord.Color.purple())
        embed.add_field(name="Info", value=panel_description, inline=False)
        
        view = discord.ui.View(timeout=None)
        view.add_item(DynamicTicketButton(label=option1_name, style=discord.ButtonStyle.blurple, custom_id="panel_btn_1", category_name=option1_name))

        await interaction.response.send_message("✅ Panel deployed.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Tickets(bot))