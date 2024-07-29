# utils.py

import re
from discord.ext import commands

def parse_duration(duration_str):
    """
    Parse a duration string into seconds.
    Accepts formats like '1h', '30m', '45s', '1d', etc.
    """
    units = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    match = re.match(r'(\d+)([smhd])', duration_str.lower())
    if not match:
        return None
    
    value, unit = match.groups()
    return int(value) * units[unit]

def format_duration(seconds):
    """
    Format a duration in seconds to a human-readable string.
    """
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}s")

    return " ".join(parts)

def is_manager(ctx):
    """
    Check if the user is a manager.
    This function should be updated to use your actual logic for identifying managers.
    """
    # Placeholder logic - replace with your actual implementation
    return ctx.author.guild_permissions.manage_guild

def is_admin(ctx):
    """
    Check if the user is an admin.
    """
    return ctx.author.guild_permissions.administrator

def is_manager_or_admin(ctx):
    """
    Check if the user is either a manager or an admin.
    """
    return is_manager(ctx) or is_admin(ctx)

class DurationConverter(commands.Converter):
    async def convert(self, ctx, argument):
        duration = parse_duration(argument)
        if duration is None:
            raise commands.BadArgument("Invalid duration format. Use something like '1h', '30m', or '45s'.")
        return duration

# Error handling decorator
def handle_errors(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            ctx = args[0] if isinstance(args[0], commands.Context) else args[1]
            await ctx.send(f"An error occurred: {str(e)}")
    return wrapper