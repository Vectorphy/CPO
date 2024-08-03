import discord
from discord import app_commands
from discord.ext import commands

class SomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the database through the bot instance

class VoiceChannels(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.temp_channels = {}

    @app_commands.command(name="create_vc", description="Create a temporary voice channel for the study group")
    async def create_vc(self, interaction: discord.Interaction, name: str = None):
        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group:
            await interaction.response.send_message("No study group exists in this server.", ephemeral=True)
            return

        members = await self.bot.db.get_group_members(group[0])
        if interaction.user.id not in members:
            await interaction.response.send_message("You're not in the study group.", ephemeral=True)
            return

        if group[0] in self.temp_channels:
            await interaction.response.send_message("A temporary voice channel already exists for this group.", ephemeral=True)
            return

        channel_name = name or f"{group[1]} VC"
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(connect=False),
            interaction.guild.me: discord.PermissionOverwrite(connect=True, manage_channels=True)
        }

        role = discord.utils.get(interaction.guild.roles, name=f"Study Group: {group[1]}")
        if role:
            overwrites[role] = discord.PermissionOverwrite(connect=True)

        channel = await interaction.guild.create_voice_channel(channel_name, overwrites=overwrites)
        self.temp_channels[group[0]] = channel.id

        await interaction.response.send_message(f"Temporary voice channel {channel.mention} created for the study group.")

    @app_commands.command(name="delete_vc", description="Delete the temporary voice channel for the study group")
    async def delete_vc(self, interaction: discord.Interaction):
        group = await self.bot.db.get_study_group(interaction.guild_id)
        if not group or group[0] not in self.temp_channels:
            await interaction.response.send_message("No temporary voice channel exists for this group.", ephemeral=True)
            return

        channel_id = self.temp_channels[group[0]]
        channel = interaction.guild.get_channel(channel_id)
        if channel:
            await channel.delete()
            del self.temp_channels[group[0]]
            await interaction.response.send_message("Temporary voice channel deleted.")
        else:
            await interaction.response.send_message("The voice channel no longer exists.")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if before.channel and before.channel.id in self.temp_channels.values() and not before.channel.members:
            group_id = next(gid for gid, cid in self.temp_channels.items() if cid == before.channel.id)
            await before.channel.delete()
            del self.temp_channels[group_id]

async def setup(bot):
    await bot.add_cog(VoiceChannels(bot))