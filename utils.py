import re
import discord
from discord.ext import commands

def parse_duration(duration_str):
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

def is_manager():
    async def predicate(ctx):
        manager_cog = ctx.bot.get_cog('Manager')
        if manager_cog:
            permission_level = await manager_cog.get_permission_level(ctx.guild.id, ctx.author.id)
            return permission_level >= manager_cog.PermissionLevel.GUILD_MANAGER
        return False
    return commands.check(predicate)

def is_group_creator():
    async def predicate(ctx):
        manager_cog = ctx.bot.get_cog('Manager')
        if manager_cog:
            return await manager_cog.is_group_creator(ctx.guild.id, ctx.author.id)
        return False
    return commands.check(predicate)