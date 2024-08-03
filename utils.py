import re
import discord

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

def is_manager(ctx):
    guild_id = ctx.guild.id
    if guild_id not in ctx.bot.manager_roles:
        ctx.bot.manager_roles[guild_id] = []
    if guild_id not in ctx.bot.manager_members:
        ctx.bot.manager_members[guild_id] = []
    
    user_roles = ctx.author.roles
    return (ctx.author.guild_permissions.administrator or 
            any(role.id in ctx.bot.manager_roles[guild_id] for role in user_roles) or 
            ctx.author.id in ctx.bot.manager_members[guild_id])