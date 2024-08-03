# cogs/pomodoro.py

import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from datetime import datetime, timedelta

class SomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = bot.db  # Access the database through the bot instance

class PomodoroSession:
    def __init__(self, group_id, focus, short_break, long_break):
        self.group_id = group_id
        self.focus = focus
        self.short_break = short_break
        self.long_break = long_break
        self.current_stage = "focus"
        self.cycles = 0
        self.is_paused = False
        self.timer = None

class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.sessions = {}

    @app_commands.command(name="start_pomodoro", description="Start a Pomodoro session for the study group")
    @app_commands.describe(
        focus="Focus duration in minutes",
        short_break="Short break duration in minutes",
        long_break="Long break duration in minutes"
    )
    async def start_pomodoro(self, interaction: discord.Interaction, focus: int = 25, short_break: int = 5, long_break: int = 15):
        group = await self.bot.db.get_user_group(interaction.user.id)
        if not group:
            await interaction.response.send_message("You're not in any study group.", ephemeral=True)
            return

        if group[0] in self.sessions:
            await interaction.response.send_message("A Pomodoro session is already in progress for this group.", ephemeral=True)
            return

        session = PomodoroSession(group[0], focus, short_break, long_break)
        self.sessions[group[0]] = session

        # Create or get the voice channel
        voice_channel_id = group[8]  # Assuming voice_channel_id is at index 8
        if not voice_channel_id:
            voice_channel = await interaction.guild.create_voice_channel(f"{group[1]} VC")
            await self.bot.db.update_voice_channel(group[0], voice_channel.id)
        else:
            voice_channel = interaction.guild.get_channel(voice_channel_id)

        # Move the user to the voice channel
        if interaction.user.voice:
            await interaction.user.move_to(voice_channel)
        else:
            await interaction.response.send_message(f"Please join the voice channel {voice_channel.mention} to start the Pomodoro session.", ephemeral=True)
            return

        await interaction.response.send_message(f"Pomodoro session started! Focus for {focus} minutes.")
        self.run_timer.start(interaction.guild_id, group[0])

    @app_commands.command(name="end_pomodoro", description="End the current Pomodoro session")
    async def end_pomodoro(self, interaction: discord.Interaction):
        group = await self.bot.db.get_user_group(interaction.user.id)
        if not group or group[0] not in self.sessions:
            await interaction.response.send_message("No active Pomodoro session for your group.", ephemeral=True)
            return

        self.run_timer.stop()
        del self.sessions[group[0]]
        await interaction.response.send_message("Pomodoro session ended.")

    @app_commands.command(name="pause_pomodoro", description="Pause the current Pomodoro session")
    async def pause_pomodoro(self, interaction: discord.Interaction):
        group = await self.bot.db.get_user_group(interaction.user.id)
        if not group or group[0] not in self.sessions:
            await interaction.response.send_message("No active Pomodoro session for your group.", ephemeral=True)
            return

        session = self.sessions[group[0]]
        if session.is_paused:
            await interaction.response.send_message("Session is already paused.", ephemeral=True)
            return

        session.is_paused = True
        await interaction.response.send_message("Pomodoro session paused.")

    @app_commands.command(name="resume_pomodoro", description="Resume the paused Pomodoro session")
    async def resume_pomodoro(self, interaction: discord.Interaction):
        group = await self.bot.db.get_user_group(interaction.user.id)
        if not group or group[0] not in self.sessions:
            await interaction.response.send_message("No active Pomodoro session for your group.", ephemeral=True)
            return

        session = self.sessions[group[0]]
        if not session.is_paused:
            await interaction.response.send_message("Session is not paused.", ephemeral=True)
            return

        session.is_paused = False
        await interaction.response.send_message("Pomodoro session resumed.")

    @tasks.loop(seconds=1)
    async def run_timer(self, guild_id, group_id):
        session = self.sessions[group_id]
        if session.is_paused:
            return

        if session.timer is None:
            session.timer = session.focus * 60

        session.timer -= 1

        if session.timer <= 0:
            if session.current_stage == "focus":
                session.cycles += 1
                if session.cycles % 4 == 0:
                    session.current_stage = "long_break"
                    session.timer = session.long_break * 60
                    await self.send_notification(guild_id, group_id, f"Focus session ended. Take a long break for {session.long_break} minutes!")
                else:
                    session.current_stage = "short_break"
                    session.timer = session.short_break * 60
                    await self.send_notification(guild_id, group_id, f"Focus session ended. Take a short break for {session.short_break} minutes!")
            else:
                session.current_stage = "focus"
                session.timer = session.focus * 60
                await self.send_notification(guild_id, group_id, f"Break ended. Focus for {session.focus} minutes!")

    async def send_notification(self, guild_id, group_id, message):
        guild = self.bot.get_guild(guild_id)
        if guild:
            group = await self.bot.db.get_study_group(guild_id)
            if group:
                _, session_role_id = await self.bot.db.get_group_roles(group[0])
                session_role = guild.get_role(session_role_id)
                if session_role:
                    voice_channel_id = group[8]  # Assuming voice_channel_id is at index 8
                    voice_channel = guild.get_channel(voice_channel_id)
                    if voice_channel:
                        await voice_channel.send(f"{session_role.mention} {message}")
                    else:
                        # Fallback to the first text channel if voice channel is not found
                        channel = guild.text_channels[0]
                        await channel.send(f"{session_role.mention} {message}")

async def setup(bot):
    await bot.add_cog(Pomodoro(bot))