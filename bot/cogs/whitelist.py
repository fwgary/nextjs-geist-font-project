import discord
from discord.ext import commands
from typing import Union
from utils.permissions import whitelist_required, admin_or_whitelist, owner_only, Permissions
from utils.embed_utils import EmbedBuilder

class WhitelistCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_group(name="whitelist", description="Manage whitelist settings")
    @admin_or_whitelist()
    async def whitelist(self, ctx: commands.Context):
        """Whitelist management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Whitelist Commands",
                description="Available whitelist management commands:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands",
                value=(
                    "`whitelist add user @user [permissions]` - Add user to whitelist\n"
                    "`whitelist add role @role [permissions]` - Add role to whitelist\n"
                    "`whitelist remove user @user` - Remove user from whitelist\n"
                    "`whitelist remove role @role` - Remove role from whitelist\n"
                    "`whitelist list` - View current whitelist\n"
                    "`whitelist permissions` - View available permissions"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
    
    @whitelist.group(name="add", description="Add to whitelist")
    @whitelist_required([Permissions.MANAGE_WHITELIST])
    async def whitelist_add(self, ctx: commands.Context):
        """Add user or role to whitelist"""
        pass
    
    @whitelist_add.command(name="user", description="Add user to whitelist")
    async def add_user(self, ctx: commands.Context, user: discord.Member, *, permissions: str = ""):
        """Add user to whitelist with specified permissions"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Parse permissions
        perm_list = []
        if permissions:
            perm_list = [p.strip() for p in permissions.split(',') if p.strip()]
            
            # Validate permissions
            valid_perms = Permissions.get_all_permissions() + [Permissions.ALL]
            invalid_perms = [p for p in perm_list if p not in valid_perms]
            
            if invalid_perms:
                await ctx.send(f"❌ Invalid permissions: {', '.join(invalid_perms)}")
                return
        
        try:
            await self.bot.permission_manager.add_user_to_whitelist(
                str(ctx.guild.id),
                str(user.id),
                perm_list,
                str(ctx.author.id)
            )
            
            embed = EmbedBuilder.create_success_embed(
                "User Added to Whitelist",
                f"{user.mention} has been added to the whitelist.",
                ctx.author
            )
            
            if perm_list:
                embed.add_field(name="Permissions", value=", ".join(perm_list), inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error adding user to whitelist: {str(e)}")
    
    @whitelist_add.command(name="role", description="Add role to whitelist")
    async def add_role(self, ctx: commands.Context, role: discord.Role, *, permissions: str = ""):
        """Add role to whitelist with specified permissions"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Parse permissions
        perm_list = []
        if permissions:
            perm_list = [p.strip() for p in permissions.split(',') if p.strip()]
            
            # Validate permissions
            valid_perms = Permissions.get_all_permissions() + [Permissions.ALL]
            invalid_perms = [p for p in perm_list if p not in valid_perms]
            
            if invalid_perms:
                await ctx.send(f"❌ Invalid permissions: {', '.join(invalid_perms)}")
                return
        
        try:
            await self.bot.permission_manager.add_role_to_whitelist(
                str(ctx.guild.id),
                str(role.id),
                perm_list,
                str(ctx.author.id)
            )
            
            embed = EmbedBuilder.create_success_embed(
                "Role Added to Whitelist",
                f"{role.mention} has been added to the whitelist.",
                ctx.author
            )
            
            if perm_list:
                embed.add_field(name="Permissions", value=", ".join(perm_list), inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error adding role to whitelist: {str(e)}")
    
    @whitelist.group(name="remove", description="Remove from whitelist")
    @whitelist_required([Permissions.MANAGE_WHITELIST])
    async def whitelist_remove(self, ctx: commands.Context):
        """Remove user or role from whitelist"""
        pass
    
    @whitelist_remove.command(name="user", description="Remove user from whitelist")
    async def remove_user(self, ctx: commands.Context, user: discord.Member):
        """Remove user from whitelist"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        try:
            await self.bot.permission_manager.remove_user_from_whitelist(
                str(ctx.guild.id),
                str(user.id)
            )
            
            embed = EmbedBuilder.create_success_embed(
                "User Removed from Whitelist",
                f"{user.mention} has been removed from the whitelist.",
                ctx.author
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error removing user from whitelist: {str(e)}")
    
    @whitelist_remove.command(name="role", description="Remove role from whitelist")
    async def remove_role(self, ctx: commands.Context, role: discord.Role):
        """Remove role from whitelist"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        try:
            await self.bot.permission_manager.remove_role_from_whitelist(
                str(ctx.guild.id),
                str(role.id)
            )
            
            embed = EmbedBuilder.create_success_embed(
                "Role Removed from Whitelist",
                f"{role.mention} has been removed from the whitelist.",
                ctx.author
            )
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error removing role from whitelist: {str(e)}")
    
    @whitelist.command(name="list", description="View whitelist entries")
    @whitelist_required([Permissions.VIEW_WHITELIST])
    async def list_whitelist(self, ctx: commands.Context):
        """List all whitelist entries for the current guild"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        try:
            entries = await self.bot.permission_manager.get_whitelist_entries(str(ctx.guild.id))
            
            if not entries:
                await ctx.send("📝 The whitelist is currently empty.")
                return
            
            embed = discord.Embed(
                title="Server Whitelist",
                color=discord.Color.blue(),
                timestamp=ctx.message.created_at
            )
            
            users = []
            roles = []
            
            for entry_type, discord_id, permissions in entries:
                perm_str = ", ".join(eval(permissions)) if permissions != '[]' else "No specific permissions"
                
                if entry_type == 'user':
                    user = ctx.guild.get_member(int(discord_id))
                    user_name = user.display_name if user else f"Unknown User ({discord_id})"
                    users.append(f"**{user_name}**: {perm_str}")
                elif entry_type == 'role':
                    role = ctx.guild.get_role(int(discord_id))
                    role_name = role.name if role else f"Unknown Role ({discord_id})"
                    roles.append(f"**{role_name}**: {perm_str}")
            
            if users:
                embed.add_field(name="Whitelisted Users", value="\n".join(users), inline=False)
            
            if roles:
                embed.add_field(name="Whitelisted Roles", value="\n".join(roles), inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving whitelist: {str(e)}")
    
    @whitelist.command(name="permissions", description="View available permissions")
    async def list_permissions(self, ctx: commands.Context):
        """List all available permissions"""
        embed = discord.Embed(
            title="Available Permissions",
            description="List of all permissions that can be assigned:",
            color=discord.Color.blue()
        )
        
        permissions = {
            "Moderation": [
                f"`{Permissions.SNIPE}` - Use snipe command",
                f"`{Permissions.DRAG}` - Drag users between voice channels",
                f"`{Permissions.NSFW}` - Mark channels as NSFW",
                f"`{Permissions.MANAGE_ROLES}` - Manage server roles",
                f"`{Permissions.MANAGE_CHANNELS}` - Manage server channels"
            ],
            "Whitelist Management": [
                f"`{Permissions.MANAGE_WHITELIST}` - Add/remove whitelist entries",
                f"`{Permissions.VIEW_WHITELIST}` - View whitelist entries"
            ],
            "Configuration": [
                f"`{Permissions.MANAGE_CONFIG}` - Modify bot configuration",
                f"`{Permissions.VIEW_CONFIG}` - View bot configuration"
            ],
            "Logging": [
                f"`{Permissions.VIEW_LOGS}` - View bot logs",
                f"`{Permissions.CLEAR_LOGS}` - Clear log files"
            ],
            "Special": [
                f"`{Permissions.ALL}` - All permissions (use with caution)"
            ]
        }
        
        for category, perms in permissions.items():
            embed.add_field(name=category, value="\n".join(perms), inline=False)
        
        embed.add_field(
            name="Usage",
            value="When adding users/roles to whitelist, separate multiple permissions with commas:\n"
                  "`!whitelist add user @user snipe,drag,nsfw`",
            inline=False
        )
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="checkperms", description="Check your permissions")
    async def check_permissions(self, ctx: commands.Context, user: discord.Member = None):
        """Check permissions for yourself or another user"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        target_user = user or ctx.author
        
        # Check if user can view others' permissions
        if user and user != ctx.author:
            can_check = await self.bot.permission_manager.check_whitelist(ctx, [Permissions.VIEW_WHITELIST])
            if not can_check:
                await ctx.send("❌ You don't have permission to check other users' permissions.")
                return
        
        try:
            user_id = str(target_user.id)
            role_ids = [str(role.id) for role in target_user.roles]
            guild_id = str(ctx.guild.id)
            
            is_whitelisted, permissions = await self.bot.db.is_whitelisted(user_id, role_ids, guild_id)
            
            embed = discord.Embed(
                title=f"Permissions for {target_user.display_name}",
                color=discord.Color.green() if is_whitelisted else discord.Color.red()
            )
            
            # Check admin status
            is_admin = target_user.guild_permissions.administrator or target_user == ctx.guild.owner
            
            if is_admin:
                embed.add_field(name="Status", value="✅ Administrator (All Permissions)", inline=False)
            elif is_whitelisted:
                embed.add_field(name="Status", value="✅ Whitelisted", inline=False)
                perm_str = ", ".join(permissions) if permissions else "No specific permissions"
                embed.add_field(name="Permissions", value=perm_str, inline=False)
            else:
                embed.add_field(name="Status", value="❌ Not Whitelisted", inline=False)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error checking permissions: {str(e)}")

async def setup(bot):
    await bot.add_cog(WhitelistCog(bot))
