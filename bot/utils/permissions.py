import discord
from discord.ext import commands
from typing import List, Union
from database import Database

class PermissionManager:
    def __init__(self, database: Database):
        self.db = database
    
    async def check_whitelist(self, ctx: commands.Context, required_permissions: List[str] = None) -> bool:
        """Check if user is whitelisted and has required permissions"""
        if not ctx.guild:
            return False
        
        user_id = str(ctx.author.id)
        role_ids = [str(role.id) for role in ctx.author.roles]
        guild_id = str(ctx.guild.id)
        
        # Check if user is server owner or has administrator permissions
        if ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner:
            return True
        
        # Check whitelist
        is_whitelisted, user_permissions = await self.db.is_whitelisted(user_id, role_ids, guild_id)
        
        if not is_whitelisted:
            return False
        
        # If no specific permissions required, whitelist is enough
        if not required_permissions:
            return True
        
        # Check if user has required permissions
        for perm in required_permissions:
            if perm not in user_permissions and '*' not in user_permissions:
                return False
        
        return True
    
    async def add_user_to_whitelist(self, guild_id: str, user_id: str, permissions: List[str], added_by: str):
        """Add user to whitelist"""
        await self.db.add_to_whitelist('user', user_id, guild_id, permissions, added_by)
    
    async def add_role_to_whitelist(self, guild_id: str, role_id: str, permissions: List[str], added_by: str):
        """Add role to whitelist"""
        await self.db.add_to_whitelist('role', role_id, guild_id, permissions, added_by)
    
    async def remove_user_from_whitelist(self, guild_id: str, user_id: str):
        """Remove user from whitelist"""
        await self.db.remove_from_whitelist('user', user_id, guild_id)
    
    async def remove_role_from_whitelist(self, guild_id: str, role_id: str):
        """Remove role from whitelist"""
        await self.db.remove_from_whitelist('role', role_id, guild_id)
    
    async def get_whitelist_entries(self, guild_id: str):
        """Get all whitelist entries for a guild"""
        return await self.db.get_whitelist(guild_id)

def whitelist_required(permissions: List[str] = None):
    """Decorator to check if user is whitelisted with required permissions"""
    async def predicate(ctx: commands.Context):
        if not hasattr(ctx.bot, 'permission_manager'):
            return False
        
        return await ctx.bot.permission_manager.check_whitelist(ctx, permissions)
    
    return commands.check(predicate)

def admin_or_whitelist():
    """Decorator for commands that require admin permissions or whitelist"""
    async def predicate(ctx: commands.Context):
        # Check if user has admin permissions
        if ctx.author.guild_permissions.administrator or ctx.author == ctx.guild.owner:
            return True
        
        # Check whitelist
        if hasattr(ctx.bot, 'permission_manager'):
            return await ctx.bot.permission_manager.check_whitelist(ctx)
        
        return False
    
    return commands.check(predicate)

def owner_only():
    """Decorator for owner-only commands"""
    async def predicate(ctx: commands.Context):
        return ctx.author == ctx.guild.owner
    
    return commands.check(predicate)

class PermissionLevel:
    """Permission level constants"""
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    WHITELIST = "whitelist"
    EVERYONE = "everyone"

class Permissions:
    """Permission constants"""
    # Moderation permissions
    SNIPE = "snipe"
    DRAG = "drag"
    NSFW = "nsfw"
    MANAGE_ROLES = "manage_roles"
    MANAGE_CHANNELS = "manage_channels"
    
    # Whitelist management
    MANAGE_WHITELIST = "manage_whitelist"
    VIEW_WHITELIST = "view_whitelist"
    
    # Configuration
    MANAGE_CONFIG = "manage_config"
    VIEW_CONFIG = "view_config"
    
    # Logging
    VIEW_LOGS = "view_logs"
    CLEAR_LOGS = "clear_logs"
    
    # Special permissions
    ALL = "*"  # All permissions
    
    @classmethod
    def get_all_permissions(cls):
        """Get list of all available permissions"""
        return [
            cls.SNIPE, cls.DRAG, cls.NSFW, cls.MANAGE_ROLES, cls.MANAGE_CHANNELS,
            cls.MANAGE_WHITELIST, cls.VIEW_WHITELIST, cls.MANAGE_CONFIG, cls.VIEW_CONFIG,
            cls.VIEW_LOGS, cls.CLEAR_LOGS
        ]
