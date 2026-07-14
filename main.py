import os
import sqlite3
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    
    # Server configuration table (Welcome settings & Anti-raid status)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS guilds (
        guild_id INTEGER PRIMARY KEY,
        welcome_channel_id INTEGER DEFAULT NULL,
        welcome_message TEXT DEFAULT 'Welcome {user} to our server!',
        antiraid_active INTEGER DEFAULT 0
    )
    """)
    conn.commit()
    conn.close()
    print("🗄️ SQLite Database initialized successfully.")

init_db()

# Gateway Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

class CurseBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="c!", intents=intents)

    async def setup_hook(self):
        # Load all modules inside the /cogs folder
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                try:
                    await self.load_extension(f'cogs.{filename[:-3]}')
                    print(f"✔️ Loaded module: {filename[:-3]}")
                except Exception as e:
                    print(f"❌ Error loading {filename}: {e}")
        
        # Global Slash Command sync
        print("🔄 Syncing commands globally with Discord...")
        try:
            await self.tree.sync()
            print("⚡ All Slash Commands synced globally and ready for use!")
        except Exception as e:
            print(f"⚠️ Sync error: {e}")

bot = CurseBot()

@bot.event
async def on_ready():
    print("=========================================")
    print(f"🤖 {bot.user.name} is online and ready!")
    print("=========================================")
    await bot.change_presence(activity=discord.Activity(
        type=discord.ActivityType.listening, 
        name="/help"
    ))

# Start the bot
token = os.environ.get("DISCORD_TOKEN")
if token:
    bot.run(token)
else:
    print("❌ ERROR: DISCORD_TOKEN not found in .env file.")