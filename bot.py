import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import Database

# Load environment variables
load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Set up intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.db = Database()

    async def setup_hook(self):
        await self.db.connect()
        await self.load_extension('cogs.manager')
        await self.load_extension('cogs.study_groups')
        await self.load_extension('cogs.pomodoro')
        await self.load_extension('cogs.voice_channels')
        await self.tree.sync()
        print("Bot setup completed.")

    async def close(self):
        await self.db.close()
        await super().close()

bot = Bot()

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

if __name__ == "__main__":
    bot.run(TOKEN)