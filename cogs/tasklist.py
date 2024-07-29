# cogs/tasklist.py

import discord
from discord.ext import commands
from database import add_task, complete_task, get_user_tasks
from utils import handle_errors

class TaskList(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def task(self, ctx):
        """Manage your task list"""
        await ctx.send_help(ctx.command)

    @task.command(name="add")
    @handle_errors
    async def add_task(self, ctx, *, task_description: str):
        """Add a new task to your list"""
        task_id = add_task(ctx.author.id, task_description)
        await ctx.send(f"Task added successfully. Task ID: {task_id}")

    @task.command(name="complete")
    @handle_errors
    async def complete_task(self, ctx, task_id: int):
        """Mark a task as complete"""
        success = complete_task(ctx.author.id, task_id)
        if success:
            await ctx.send(f"Task {task_id} marked as complete.")
        else:
            await ctx.send(f"Task {task_id} not found or already completed.")

    @task.command(name="list")
    @handle_errors
    async def list_tasks(self, ctx):
        """List your current tasks"""
        tasks = get_user_tasks(ctx.author.id)
        if tasks:
            embed = discord.Embed(title=f"{ctx.author.display_name}'s Tasks", color=discord.Color.blue())
            for task in tasks:
                status = "Completed" if task['completed'] else "In Progress"
                embed.add_field(name=f"Task {task['id']}", value=f"{task['task']} - {status}", inline=False)
            await ctx.send(embed=embed)
        else:
            await ctx.send("You have no tasks.")

async def setup(bot):
    await bot.add_cog(TaskList(bot))