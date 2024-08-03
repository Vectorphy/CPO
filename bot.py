import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from database import Database

load_dotenv()
TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
intents.voice_states = True

class CPO(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=intents)
        self.db = Database()

    async def setup_hook(self):
        await self.db.connect()
        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and not filename.startswith("_"):
                try:
                    await self.load_extension(f"cogs.{filename[:-3]}")
                    print(f"Loaded extension: {filename[:-3]}")
                except Exception as e:
                    print(f"Failed to load extension {filename[:-3]}: {e}")
        await self.tree.sync()
        print("CPO setup completed.")

    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        print(f"Guilds: {len(self.guilds)}")
        print(f"Users: {len(set(self.get_all_members()))}")

    async def close(self):
        await self.db.close()
        await super().close()

cpo = CPO()

@cpo.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Use `!help` for a list of commands.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"Missing required argument: {error.param}")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"Bad argument: {str(error)}")
    else:
        print(f"An error occurred: {error}")
        await ctx.send("An error occurred while processing the command.")

@cpo.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"This command is on cooldown. Try again in {error.retry_after:.2f} seconds.", ephemeral=True)
    elif isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message("You don't have the required permissions to use this command.", ephemeral=True)
    else:
        print(f"An error occurred in app command: {error}")
        await interaction.response.send_message("An error occurred while processing the command.", ephemeral=True)

if __name__ == "__main__":
    cpo.run(TOKEN)