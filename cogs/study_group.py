import discord
from discord import app_commands
from discord.ext import commands
import asyncio
from .manager import PermissionLevel

class SomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the database through the bot instance

class StudyGroups(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_session_role(self, guild, session_name):
        role_name = f"In {session_name}"
        return await guild.create_role(name=role_name, mentionable=True)

    @app_commands.command(name="create_group", description="Create a new study group")
    @app_commands.describe(name="Name of the study group", max_size="Maximum number of members")
    async def create_group(self, interaction: discord.Interaction, name: str, max_size: int = 10):
        manager_cog = self.bot.get_cog('Manager')
        if manager_cog:
            permission_level = await manager_cog.get_permission_level(interaction.guild_id, interaction.user.id)
            if permission_level < PermissionLevel.GROUP_CREATOR:
                await interaction.response.send_message("You don't have permission to create a group.", ephemeral=True)
                return

        existing_group = await self.bot.db.get_study_group(interaction.guild_id)
        if existing_group:
            await interaction.response.send_message("A study group already exists in this server.", ephemeral=True)
            return

        end_time = asyncio.get_event_loop().time() + 43200  # 12 hours
        group_id = await self.bot.db.create_study_group(name, interaction.user.id, max_size, end_time, interaction.guild_id)
        await self.bot.db.add_group_member(group_id, interaction.user.id)

        # Create roles for the group
        admin_role = await interaction.guild.create_role(name=f"Study Group: {name}")
        session_role = await self.create_session_role(interaction.guild, name)
        
        await interaction.user.add_roles(admin_role, session_role)

        await self.bot.db.update_group_roles(group_id, admin_role.id, session_role.id)

        await interaction.response.send_message(
            f"Study group '{name}' created! Use /join_group to join.\n"
            f"You've been assigned the role {session_role.mention}. "
            f"You can use this role to check progress in the session."
        )

    @app_commands.command(name="join_group", description="Join the existing study group")
    async def join_group(self, interaction: discord.Interaction):
        user_group = await self.bot.db.get_user_group(interaction.user.id)
        if user_group:
            await interaction.response.send_message("You're already in a study group. Leave your current group first.", ephemeral=True)
            return

        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group:
            await interaction.response.send_message("No study group exists in this server.", ephemeral=True)
            return

        members = await self.bot.db.get_group_members(group[0])
        if len(members) >= group[3]:  # max_size
            await interaction.response.send_message("This group is full.", ephemeral=True)
            return

        await self.bot.db.add_group_member(group[0], interaction.user.id)

        _, session_role_id = await self.bot.db.get_group_roles(group[0])
        session_role = interaction.guild.get_role(session_role_id)

        if session_role:
            await interaction.user.add_roles(session_role)

        # Move user to voice channel if it exists
        voice_channel_id = group[8]  # Assuming voice_channel_id is at index 8
        if voice_channel_id:
            voice_channel = interaction.guild.get_channel(voice_channel_id)
            if voice_channel:
                await interaction.user.move_to(voice_channel)

        await interaction.response.send_message(
            f"You've joined the study group '{group[1]}'!\n"
            f"You've been assigned the role {session_role.mention}. "
            f"You can use this role to check progress in the session."
        )

    @app_commands.command(name="leave_group", description="Leave the current study group")
    async def leave_group(self, interaction: discord.Interaction):
        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group:
            await interaction.response.send_message("No study group exists in this server.", ephemeral=True)
            return

        members = await self.bot.db.get_group_members(group[0])
        if interaction.user.id not in members:
            await interaction.response.send_message("You're not in a study group.", ephemeral=True)
            return

        await self.bot.db.remove_group_member(group[0], interaction.user.id)
        
        admin_role_id, session_role_id = await self.bot.db.get_group_roles(group[0])
        session_role = interaction.guild.get_role(session_role_id)
        
        if session_role:
            await interaction.user.remove_roles(session_role)
        
        await interaction.response.send_message(f"You've left the study group '{group[1]}'.")

        updated_members = await self.bot.db.get_group_members(group[0])
        if not updated_members:
            await self.end_group(interaction.guild_id)

    @app_commands.command(name="end_group", description="End the current study group")
    async def end_group_command(self, interaction: discord.Interaction):
        manager_cog = self.bot.get_cog('Manager')
        if manager_cog:
            is_creator = await manager_cog.is_group_creator(interaction.guild_id, interaction.user.id)
            if not is_creator:
                await interaction.response.send_message("Only the group creator can end the group.", ephemeral=True)
                return

        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group:
            await interaction.response.send_message("No study group exists in this server.", ephemeral=True)
            return

        await self.end_group(interaction.guild_id)
        await interaction.response.send_message(f"The study group '{group[1]}' has been ended.")

    async def end_group(self, guild_id):
        group = await self.bot.db.get_study_group(guild_id)
        if group:
            admin_role_id, session_role_id = await self.bot.db.get_group_roles(group[0])
            guild = self.bot.get_guild(guild_id)
            
            admin_role = guild.get_role(admin_role_id)
            session_role = guild.get_role(session_role_id)
            
            if admin_role:
                await admin_role.delete()
            if session_role:
                await session_role.delete()
            
            await self.bot.db.delete_study_group(group[0])

async def setup(bot):
    await bot.add_cog(StudyGroups(bot))