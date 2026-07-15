import discord
import asyncio
from discord import app_commands
from discord.ext import commands

# --- PANEL DE CONTROL DENTRO DEL TICKET (ESTILO TICKET KING) ---
class TicketControlView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Close 🔒", style=discord.ButtonStyle.red, custom_id="tk_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("⚙️ This ticket will be permanently deleted in 5 seconds...", ephemeral=False)
        await asyncio.sleep(5)
        await interaction.channel.delete()

    @discord.ui.button(label="Claim 🙋‍♂️", style=discord.ButtonStyle.green, custom_id="tk_claim")
    async def claim_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # El miembro del Staff que pulsa el botón reclama el caso
        staff_member = interaction.user
        
        # Deshabilitar el botón de reclamo una vez usado
        for child in self.children:
            if child.custom_id == "tk_claim":
                child.disabled = True
                child.label = f"Claimed by {staff_member.name}"
                child.style = discord.ButtonStyle.grey

        # Actualizar permisos para que solo el creador y este staff hablen
        await interaction.channel.edit(topic=f"Ticket claimed by {staff_member.mention}")
        
        embed = discord.Embed(
            title="🎯 Ticket Claimed",
            description=f"This support ticket is now being handled by {staff_member.mention}.",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(view=self)
        await interaction.channel.send(embed=embed)


# --- BOTÓN DINÁMICO DE CREACIÓN DE TICKETS ---
class DynamicTicketButton(discord.ui.Button):
    def __init__(self, label: str, style: discord.ButtonStyle, custom_id: str, category_name: str):
        super().__init__(label=label, style=style, custom_id=custom_id)
        self.category_name = category_name

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        member = interaction.user
        
        # Formato de canal limpio
        clean_channel_name = f"ticket-{self.category_name.lower()}-{member.name.lower()}".replace(" ", "-")
        existing_channel = discord.utils.get(guild.text_channels, name=clean_channel_name)
        
        if existing_channel:
            await interaction.response.send_message(f"⚠️ You already have an open ticket for this category: {existing_channel.mention}", ephemeral=True)
            return

        # Permisos del canal
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            member: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        category = interaction.channel.category
        channel = await guild.create_text_channel(
            name=clean_channel_name,
            category=category,
            overwrites=overwrites
        )

        # Embed de bienvenida al ticket abierto estilo Ticket King (Limpio y sin textos gigantes)
        embed = discord.Embed(
            title=f"🎫 SUPPORT TICKET — {self.category_name.upper()}",
            color=discord.Color.blue()
        )
        embed.add_field(
            name="Welcome", 
            value=f"Hello {member.mention}, thank you for opening a ticket.", 
            inline=False
        )
        embed.add_field(
            name="Inquiry", 
            value="Please describe your issue below. Our support team will assist you shortly.", 
            inline=False
        )
        embed.add_field(
            name="Actions", 
            value="Use the buttons below to close or claim this ticket.", 
            inline=False
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text="CurseBot Ticket System")

        await channel.send(content=f"{member.mention} | Support Staff", embed=embed, view=TicketControlView())
        await interaction.response.send_message(f"✅ Your ticket has been created at {channel.mention}", ephemeral=True)


# --- COMANDO PRINCIPAL DE CONFIGURACIÓN ---
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        # Mantiene activos los botones de control incluso tras reiniciar el bot
        self.bot.add_view(TicketControlView())

    @app_commands.command(name="setup_tickets", description="Create an advanced support panel (Ticket King style).")
    @app_commands.describe(
        panel_title="The title shown on the ticket panel embed",
        panel_description="The main text description on the panel",
        option1_name="First button label (e.g. Support)",
        option2_name="Second button label (Optional, e.g. Reports)",
        option3_name="Third button label (Optional, e.g. Partnerships)"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def setup_tickets(
        self, 
        interaction: discord.Interaction, 
        panel_title: str, 
        panel_description: str, 
        option1_name: str, 
        option2_name: str = None, 
        option3_name: str = None
    ):
        # Creamos el panel de tickets usando un Embed con estructura modular de campos
        embed = discord.Embed(
            title=f"📥 {panel_title.upper()}",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Information", 
            value=panel_description, 
            inline=False
        )
        embed.add_field(
            name="How to open?", 
            value="Click on one of the buttons below corresponding to your inquiry to open a private ticket.", 
            inline=False
        )
        embed.set_footer(text="Powered by CurseBot")

        # Vista de botones
        view = discord.ui.View(timeout=None)
        
        # Botón 1 (Obligatorio)
        view.add_item(DynamicTicketButton(
            label=option1_name, 
            style=discord.ButtonStyle.blurple, 
            custom_id="panel_btn_1", 
            category_name=option1_name
        ))
        
        # Botón 2 (Opcional)
        if option2_name:
            view.add_item(DynamicTicketButton(
                label=option2_name, 
                style=discord.ButtonStyle.green, 
                custom_id="panel_btn_2", 
                category_name=option2_name
            ))
            
        # Botón 3 (Opcional)
        if option3_name:
            view.add_item(DynamicTicketButton(
                label=option3_name, 
                style=discord.ButtonStyle.grey, 
                custom_id="panel_btn_3", 
                category_name=option3_name
            ))

        await interaction.response.send_message("✅ Support panel successfully deployed.", ephemeral=True)
        await interaction.channel.send(embed=embed, view=view)

async def setup(bot):
    await bot.add_cog(Tickets(bot))