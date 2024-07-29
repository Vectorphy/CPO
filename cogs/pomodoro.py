# cogs/pomodoro.py

import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
from utils import parse_duration, is_manager_or_admin, handle_errors, DurationConverter
from database import update_pomodoro_stats, create_pomodoro_group, add_group_member, remove_group_member, get_group_members, get_group_by_name

class PomodoroSession:
    def __init__(self, user_ids, voice_channel, work_duration=25*60, short_break=5*60, long_break=15*60):
        self.user_ids = set(user_ids)
        self.voice_channel = voice_channel
        self.work_duration = work_duration
        self.short_break = short_break
        self.long_break = long_break
        self.cycle = 0
        self.timer = None
        self.status = "Not Started"

    async def start(self):
        self.status = "Running"
        while self.status == "Running":
            await self.work_session()
            if self.status != "Running":
                break
            await self.break_session()

    async def work_session(self):
        await self.start_timer(self.work_duration, "Work")

    async def break_session(self):
        self.cycle += 1
        if self.cycle % 4 == 0:
            await self.start_timer(self.long_break, "Long Break")
        else:
            await self.start_timer(self.short_break, "Short Break")

    async def start_timer(self, duration, session_type):
        end_time = datetime.now() + timedelta(seconds=duration)
        while datetime.now() < end_time and self.status == "Running":
            remaining = end_time - datetime.now()
            await self.voice_channel.edit(name=f"{session_type}: {remaining.seconds // 60:02d}:{remaining.seconds % 60:02d}")
            await asyncio.sleep(1)

        if self.status == "Running":
            mentions = " ".join(f"<@{user_id}>" for user_id in self.user_ids)
            await self.voice_channel.send(f"{mentions} {session_type} session has ended!")

    def stop(self):
        self.status = "Stopped"

class Pomodoro(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.active_sessions = {}

    @commands.group(invoke_without_command=True)
    async def pomodoro(self, ctx):
        """Manage Pomodoro sessions"""
        await ctx.send_help(ctx.command)

    @pomodoro.command(name="start")
    @handle_errors
    async def start_pomodoro(self, ctx, work: DurationConverter = 25*60, short_break: DurationConverter = 5*60, long_break: DurationConverter = 15*60):
        """Start a Pomodoro session"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel to start a Pomodoro session.")
            return

        if ctx.author.id in self.active_sessions:
            await ctx.send("You're already in an active Pomodoro session.")
            return

        session = PomodoroSession([ctx.author.id], ctx.author.voice.channel, work, short_break, long_break)
        self.active_sessions[ctx.author.id] = session
        await ctx.send(f"Pomodoro session started! Work: {work//60}min, Short break: {short_break//60}min, Long break: {long_break//60}min")
        await session.start()

        # Update user stats
        update_pomodoro_stats(ctx.author.id)

    @pomodoro.command(name="stop")
    @handle_errors
    async def stop_pomodoro(self, ctx):
        """Stop your active Pomodoro session"""
        if ctx.author.id in self.active_sessions:
            session = self.active_sessions[ctx.author.id]
            session.stop()
            del self.active_sessions[ctx.author.id]
            await ctx.send("Your Pomodoro session has been stopped.")
        else:
            await ctx.send("You don't have an active Pomodoro session.")

    @pomodoro.group(name="group", invoke_without_command=True)
    async def pomodoro_group(self, ctx):
        """Manage Pomodoro groups"""
        await ctx.send_help(ctx.command)

    @pomodoro_group.command(name="create")
    @handle_errors
    async def create_group(self, ctx, group_name: str):
        """Create a new Pomodoro group"""
        group = get_group_by_name(group_name)
        if group:
            await ctx.send("A group with this name already exists.")
        else:
            create_pomodoro_group(group_name, ctx.author.id)
            await ctx.send(f"Group '{group_name}' created successfully.")

    @pomodoro_group.command(name="add")
    @handle_errors
    async def add_to_group(self, ctx, group_name: str, member: discord.Member):
        """Add a member to a Pomodoro group"""
        group = get_group_by_name(group_name)
        if not group:
            await ctx.send("This group doesn't exist.")
        elif group['creator_id'] != ctx.author.id:
            await ctx.send("Only the group creator can add members.")
        else:
            add_group_member(group['group_id'], member.id)
            await ctx.send(f"{member.display_name} has been added to the group '{group_name}'.")

    @pomodoro_group.command(name="remove")
    @handle_errors
    async def remove_from_group(self, ctx, group_name: str, member: discord.Member):
        """Remove a member from a Pomodoro group"""
        group = get_group_by_name(group_name)
        if not group:
            await ctx.send("This group doesn't exist.")
        elif group['creator_id'] != ctx.author.id:
            await ctx.send("Only the group creator can remove members.")
        else:
            remove_group_member(group['group_id'], member.id)
            await ctx.send(f"{member.display_name} has been removed from the group '{group_name}'.")

    @pomodoro_group.command(name="start")
    @handle_errors
    async def start_group_pomodoro(self, ctx, group_name: str, work: DurationConverter = 25*60, short_break: DurationConverter = 5*60, long_break: DurationConverter = 15*60):
        """Start a Pomodoro session for a group"""
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("You need to be in a voice channel to start a group Pomodoro session.")
            return

        group = get_group_by_name(group_name)
        if not group:
            await ctx.send("This group doesn't exist.")
            return

        members = get_group_members(group['group_id'])
        if ctx.author.id not in members:
            await ctx.send("You're not a member of this group.")
            return

        session = PomodoroSession(members, ctx.author.voice.channel, work, short_break, long_break)
        for member_id in members:
            self.active_sessions[member_id] = session

        await ctx.send(f"Group Pomodoro session started for '{group_name}'! Work: {work//60}min, Short break: {short_break//60}min, Long break: {long_break//60}min")
        await session.start()

        # Update user stats for all participants
        for member_id in members:
            update_pomodoro_stats(member_id)

async def setup(bot):
    await bot.add_cog(Pomodoro(bot))