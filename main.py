import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

# 1. Cargar variables de entorno (.env)
load_dotenv()

# 2. Inicializar la Base de Datos SQLite de forma limpia
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Creamos la tabla con todas las columnas necesarias organizadas
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

# 4. Clase principal del Bot
class CurseBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="c!", intents=intents)

    async def setup_hook(self):
        # Cargar todos los módulos automáticos de la carpeta /cogs
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✔️ Loaded module: {filename[:-3]}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        # Sincronización global automática de comandos de barra (/)
        print("🔄 Syncing commands globally with Discord...")
        try:
            await self.tree.sync()
            print("⚡ All Slash Commands synced globally and ready!")
        except Exception as e:
            print(f"⚠️ Sync error: {e}")

bot = CurseBot()

# 5. Evento cuando el bot se conecta correctamente
@bot.event
async def on_ready():
    print("=========================================")
    print(f"🤖 {bot.user.name} is online and ready!")
    print("=========================================")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="/help"
    ))

# 6. Ejecutar el Bot de forma segura
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR: DISCORD_TOKEN not found in your .env file.")