import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Cargar variables de entorno (.env)
load_dotenv()

# 2. Inicializar la Base de Datos SQLite
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id INTEGER PRIMARY KEY,
        welcome_channel_id INTEGER DEFAULT NULL,
        antiraid_active INTEGER DEFAULT 0,
        language TEXT DEFAULT 'en'
    )
    """)
    conn.commit()
    conn.close()
    print("🗄️ SQLite Database initialized successfully.")

init_db()

# 3. Configuración de los accesos y permisos (Intents)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

# 4. Clase principal del Bot Público
class CurseBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="c!", intents=intents)

    async def setup_hook(self):
        # Cargar todos los módulos de la carpeta /cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✔️ Loaded module: {filename[:-3]}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        # 🌍 Sincronización GLOBAL para que funcione en todos los servidores públicos
        print("🔄 Syncing commands globally with Discord...")
        try:
            await self.tree.sync()
            print("⚡ Slash Commands synced GLOBALLY for all servers!")
        except Exception as e:
            print(f"⚠️ Global sync error: {e}")

bot = CurseBot()

# 5. Evento de conexión
@bot.event
async def on_ready():
    print("=========================================")
    print(f"🤖 {bot.user.name} is online and ready for public use!")
    print("=========================================")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="/help"
    ))

# 6. Ejecutar el Bot
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR: DISCORD_TOKEN not found.")