import discord
from discord.ext import commands
import asyncio
import re
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random

# Load environment variables from .env file
load_dotenv()
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

# Initialize intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.presences = True

# Initialize bot
bot = commands.Bot(command_prefix=['/', '!'], intents=intents)

# Dictionaries to store data for each guild
checkin_channels = {}
active_sessions = {}
manager_roles = {}
manager_members = {}

# List of variation messages
progress_messages = [
    "How's your progress?",
    "What have you achieved so far?",
    "Any updates on your task?",
    "How are things going?",
    "How is your work progressing?",
    "What have you done since the last check-in?",
    "What's your status?",
    "How's it going?",
    "Any progress to report?",
    "What have you completed?"
]

class CheckinSession:
    def __init__(self, guild_id, channel, creator, duration, mentions):
        self.guild_id = guild_id
        self.channel = channel
        self.creator = creator
        self.duration = duration
        self.mentions = mentions
        self.task = None
        self.start_time = datetime.now()

class ReminderView(discord.ui.View):
    def __init__(self, session):
        super().__init__()
        self.session = session

    @discord.ui.button(label='Join', style=discord.ButtonStyle.success)
    async def join(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user not in self.session.mentions:
            self.session.mentions.append(interaction.user)
            await interaction.response.send_message('You have now joined the check-in session.', ephemeral=True)
        else:
            await interaction.response.send_message('You have already joined the check-in session.', ephemeral=True)

    @discord.ui.button(label='Leave', style=discord.ButtonStyle.danger)
    async def leave(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user in self.session.mentions:
            self.session.mentions.remove(interaction.user)
            await interaction.response.send_message('You have left the check-in session.', ephemeral=True)
        else:
            await interaction.response.send_message('You are not part of the check-in session.', ephemeral=True)

    @discord.ui.button(label='End', style=discord.ButtonStyle.primary)
    async def end(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user == self.session.creator:
            self.session.task.cancel()
            await interaction.response.send_message('The check-in session has now ended.')
        else:
            await interaction.response.send_message('Only the creator can end the session.', ephemeral=True)

async def parse_duration(duration_str):
    match = re.match(r'(\d+)\s*(s|secs?|seconds?|m|mins?|minutes?|h|hrs?|hours?|d|days?)', duration_str, re.IGNORECASE)
    if not match:
        return None
    value, unit = match.groups()
    value = int(value)
    unit = unit.lower()
    if 's' in unit:
        return value
    elif 'm' in unit:
        return value * 60
    elif 'h' in unit:
        return value * 3600
    elif 'd' in unit:
        return value * 86400
    return None

def parse_mentions(ctx, mentions):
    mention_list = mentions.split()
    members = []

    for mention in mention_list:
        mention = mention.strip()
        if mention.startswith('<@&'):  # Role mention
            role_id = int(mention.strip('<@&>'))
            role = ctx.guild.get_role(role_id)
            if role:
                members.extend(role.members)
        elif mention.startswith('<@!') or mention.startswith('<@'):  # User mention
            user_id = int(mention.strip('<@!>').strip('<@>'))
            member = ctx.guild.get_member(user_id)
            if member:
                members.append(member)
    
    return list(set(members))  # Remove duplicates

async def send_reminders(session):
    last_reminder_time = datetime.now()
    while True:
        try:
            await asyncio.sleep(session.duration)
            current_time = datetime.now()
            time_difference = current_time - last_reminder_time
            minutes_ago = int(time_difference.total_seconds() // 60)
            time_message = f"{minutes_ago} minutes ago"
            random_progress_message = random.choice(progress_messages)
            message = f'{" ".join(member.mention for member in session.mentions)}, {random_progress_message}\nLast reminder: {time_message}'
            await session.channel.send(message, view=ReminderView(session))
            last_reminder_time = current_time
        except asyncio.CancelledError:
            break
        except Exception as e:
            print(f'Error in send_reminders task: {e}')

def is_manager(ctx):
    guild_id = ctx.guild.id
    if guild_id not in manager_roles:
        manager_roles[guild_id] = []
    if guild_id not in manager_members:
        manager_members[guild_id] = []
    
    user_roles = ctx.author.roles
    return (ctx.author.guild_permissions.administrator or 
            any(role.id in manager_roles[guild_id] for role in user_roles) or 
            ctx.author.id in manager_members[guild_id])

@bot.event
async def on_ready():
    print(f'Bot is ready as {bot.user}')
    await bot.tree.sync()
    print('Commands synced with all guilds')

@bot.hybrid_command(name='checkin_channels')
@commands.check(is_manager)
async def checkin_channels_cmd(ctx, *, channels: str):
    guild_id = ctx.guild.id
    checkin_channels[guild_id] = [ctx.guild.get_channel(int(channel.strip('<#>'))) for channel in channels.split()]
    await ctx.send(f'Check-in channels updated: {", ".join(channel.mention for channel in checkin_channels[guild_id])}')

@bot.hybrid_command(name='checkin')
async def checkin_cmd(ctx, duration: str, *, mentions: str):
    guild_id = ctx.guild.id
    if guild_id not in checkin_channels or not checkin_channels[guild_id]:
        await ctx.send('No check-in channels are defined for this server. Please contact your admins to set up the bot.')
        return

    duration_seconds = await parse_duration(duration)
    if duration_seconds is None or duration_seconds < 30:
        await ctx.send('Invalid duration. Minimum duration is 30 seconds.')
        return

    members = parse_mentions(ctx, mentions)

    if ctx.author not in members:
        members.append(ctx.author)

    session = CheckinSession(guild_id=guild_id, channel=ctx.channel, creator=ctx.author, duration=duration_seconds, mentions=members)

    if guild_id not in active_sessions:
        active_sessions[guild_id] = []
    active_sessions[guild_id].append(session)

    session.task = asyncio.create_task(send_reminders(session))

    member_str = " ".join(member.mention for member in members)
    await ctx.send(f'{member_str}\nCheck-in session started for {duration}!', view=ReminderView(session))

@bot.hybrid_command(name='add_managers')
@commands.check(is_manager)
async def add_managers_cmd(ctx, *, mentions: str):
    guild_id = ctx.guild.id
    if guild_id not in manager_roles:
        manager_roles[guild_id] = []
    if guild_id not in manager_members:
        manager_members[guild_id] = []

    members = parse_mentions(ctx, mentions)

    for member in members:
        if isinstance(member, discord.Role):
            if member.id not in manager_roles[guild_id]:
                manager_roles[guild_id].append(member.id)
        else:
            if member.id not in manager_members[guild_id]:
                manager_members[guild_id].append(member.id)

    await ctx.send('Managers have been updated.')

@bot.hybrid_command(name='view_managers')
@commands.check(is_manager)
async def view_managers_cmd(ctx):
    guild_id = ctx.guild.id
    if guild_id not in manager_roles:
        manager_roles[guild_id] = []
    if guild_id not in manager_members:
        manager_members[guild_id] = []

    embed = discord.Embed(title="Managers", description="Roles and members who can use setting commands", color=discord.Color.blue())
    
    roles = [ctx.guild.get_role(role_id) for role_id in manager_roles[guild_id]]
    members = [ctx.guild.get_member(user_id) for user_id in manager_members[guild_id]]

    embed.add_field(name="Roles", value=", ".join(role.name for role in roles if role) or "None", inline=False)
    embed.add_field(name="Members", value=", ".join(member.display_name for member in members if member) or "None", inline=False)

    await ctx.send(embed=embed)

bot.run(DISCORD_BOT_TOKEN)