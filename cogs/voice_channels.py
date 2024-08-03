# cogs/voice_channels.py

import discord
from discord import app_commands
from discord.ext import commands
from utils import is_manager, is_group_creator

class VoiceChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="create_vc", description="Create a voice channel for the study group")
    @app_commands.describe(name="Name of the voice channel (optional)")
    @is_group_creator()
    async def create_vc(self, interaction: discord.Interaction, name: str = None):
        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group:
            await interaction.response.send_message("No study group exists in this server.", ephemeral=True)
            return

        if group[8]:  # Assuming voice_channel_id is at index 8
            await interaction.response.send_message("A voice channel already exists for this group.", ephemeral=True)
            return

        channel_name = name or f"{group[1]} VC"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=False),
            interaction.guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True)
        }

        _, session_role_id = await self.bot.db.get_group_roles(group[0])
        session_role = interaction.guild.get_role(session_role_id)
        if session_role:
            overwrites[session_role] = discord.PermissionOverwrite(connect=True)

        channel = await interaction.guild.create_voice_channel(channel_name, overwrites=overwrites)
        await self.bot.db.update_voice_channel(group[0], channel.id)

        await interaction.response.send_message(f"Voice channel {channel.mention} created for the study group.")

    @app_commands.command(name="delete_vc", description="Delete the voice channel for the study group")
    @is_group_creator()
    async def delete_vc(self, interaction: discord.Interaction):
        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group or not group[8]:  # Assuming voice_channel_id is at index 8
            await interaction.response.send_message("No voice channel exists for this group.", ephemeral=True)
            return

        channel = interaction.guild.get_channel(group[8])
        if channel:
            await channel.delete()
            await self.bot.db.update_voice_channel(group[0], None)
            await interaction.response.send_message("Voice channel deleted.")
        else:
            await interaction.response.send_message("The voice channel no longer exists.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel and not after.channel:
            group = await self.bot.db.get_study_group(before.channel.guild.id)
            if group and group[8] == before.channel.id:
                if not before.channel.members:
                    await before.channel.delete()
                    await self.bot.db.update_voice_channel(group[0], None)

async def setup(bot):
    await bot.add_cog(VoiceChannels(bot))