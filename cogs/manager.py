import discord
from discord import app_commands
from discord.ext import commands

class SomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the database through the bot instance

class PermissionLevel:
    BOT_DEVELOPER = 3
    GUILD_MANAGER = 2
    GROUP_CREATOR = 1
    REGULAR_USER = 0

class Manager(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def get_permission_level(self, guild_id, user_id):
        manager = await self.bot.db.get_manager(user_id, guild_id)
        if manager:
            return manager[3]  # permission_level
        return PermissionLevel.REGULAR_USER

    @app_commands.command(name="add_bot_developer", description="Add a bot developer (Bot Developer only)")
    @app_commands.describe(user="The user to add as a bot developer")
    async def add_bot_developer(self, interaction: discord.Interaction, user: discord.User):
        if await self.get_permission_level(interaction.guild_id, interaction.user.id) != PermissionLevel.BOT_DEVELOPER:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await self.bot.db.add_manager(user.id, None, PermissionLevel.BOT_DEVELOPER)
        await interaction.response.send_message(f"{user.name} has been added as a bot developer.", ephemeral=True)

    @app_commands.command(name="add_guild_manager", description="Add a guild manager (Bot Developer only)")
    @app_commands.describe(user="The user to add as a guild manager")
    async def add_guild_manager(self, interaction: discord.Interaction, user: discord.User):
        if await self.get_permission_level(interaction.guild_id, interaction.user.id) != PermissionLevel.BOT_DEVELOPER:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await self.bot.db.add_manager(user.id, interaction.guild_id, PermissionLevel.GUILD_MANAGER)
        await interaction.response.send_message(f"{user.name} has been added as a guild manager for this server.", ephemeral=True)

    @app_commands.command(name="remove_guild_manager", description="Remove a guild manager (Bot Developer only)")
    @app_commands.describe(user="The user to remove as a guild manager")
    async def remove_guild_manager(self, interaction: discord.Interaction, user: discord.User):
        if await self.get_permission_level(interaction.guild_id, interaction.user.id) != PermissionLevel.BOT_DEVELOPER:
            await interaction.response.send_message("You don't have permission to use this command.", ephemeral=True)
            return

        await self.bot.db.remove_manager(user.id, interaction.guild_id)
        await interaction.response.send_message(f"{user.name} has been removed as a guild manager for this server.", ephemeral=True)

    @app_commands.command(name="list_managers", description="List all managers for this server")
    async def list_managers(self, interaction: discord.Interaction):
        managers = await self.bot.db.get_all_managers(interaction.guild_id)
        
        embed = discord.Embed(title="Managers", color=discord.Color.blue())
        for manager in managers:
            user = await self.bot.fetch_user(manager[1])  # user_id
            level = "Bot Developer" if manager[2] is None else "Guild Manager"
            embed.add_field(name=f"{user.name}#{user.discriminator}", value=level, inline=False)

        await interaction.response.send_message(embed=embed)

    async def is_group_creator(self, guild_id, user_id):
        group = await self.bot.db.get_study_group(guild_id)
        return group and group[2] == user_id  # Assuming creator_id is at index 2

async def setup(bot):
    await bot.add_cog(Manager(bot))