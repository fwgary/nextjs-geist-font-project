import discord
from discord.ext import commands
from datetime import datetime
from typing import Optional
from utils.permissions import whitelist_required, admin_or_whitelist, Permissions
from utils.embed_utils import EmbedBuilder

class ModerationCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.hybrid_command(name="snipe", description="Retrieve the last deleted message in this channel")
    @whitelist_required([Permissions.SNIPE])
    async def snipe(self, ctx: commands.Context):
        """Snipe the last deleted message in the current channel"""
        try:
            deleted_msg = await self.bot.db.get_last_deleted_message(str(ctx.channel.id))
            
            if not deleted_msg:
                await ctx.send("🔍 No recently deleted messages found in this channel.")
                return
            
            author_id, content, attachments, deleted_at = deleted_msg
            
            # Parse deleted_at timestamp
            if isinstance(deleted_at, str):
                deleted_at = datetime.fromisoformat(deleted_at.replace('Z', '+00:00'))
            
            embed = EmbedBuilder.create_snipe_embed(author_id, content, attachments, deleted_at)
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving deleted message: {str(e)}")
    
    @commands.hybrid_command(name="drag", description="Move a user between voice channels")
    @whitelist_required([Permissions.DRAG])
    async def drag(self, ctx: commands.Context, user: discord.Member, channel: discord.VoiceChannel):
        """Drag a user to a different voice channel"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Check if user is in a voice channel
        if not user.voice or not user.voice.channel:
            await ctx.send(f"❌ {user.mention} is not in a voice channel.")
            return
        
        # Check bot permissions
        if not channel.permissions_for(ctx.guild.me).move_members:
            await ctx.send("❌ I don't have permission to move members in that channel.")
            return
        
        # Check if user can be moved
        if not channel.permissions_for(ctx.guild.me).connect:
            await ctx.send("❌ I don't have permission to connect to that channel.")
            return
        
        old_channel = user.voice.channel
        
        try:
            await user.move_to(channel)
            
            embed = EmbedBuilder.create_moderation_embed(
                "User Dragged",
                user,
                ctx.author,
                f"Moved from {old_channel.name} to {channel.name}",
                {
                    "From Channel": old_channel.name,
                    "To Channel": channel.name
                }
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to move that user.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to move user: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.hybrid_command(name="nsfw", description="Mark a text channel as NSFW")
    @whitelist_required([Permissions.NSFW])
    async def nsfw(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Mark a text channel as NSFW"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        target_channel = channel or ctx.channel
        
        # Check bot permissions
        if not target_channel.permissions_for(ctx.guild.me).manage_channels:
            await ctx.send("❌ I don't have permission to manage that channel.")
            return
        
        # Check if already NSFW
        if target_channel.nsfw:
            await ctx.send(f"❌ {target_channel.mention} is already marked as NSFW.")
            return
        
        try:
            await target_channel.edit(nsfw=True, reason=f"NSFW enabled by {ctx.author}")
            
            embed = EmbedBuilder.create_moderation_embed(
                "Channel Marked NSFW",
                ctx.author,  # Using author as target since no specific target user
                ctx.author,
                f"Channel {target_channel.mention} has been marked as NSFW",
                {
                    "Channel": target_channel.mention,
                    "Action": "Marked as NSFW"
                }
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to mark channel as NSFW: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.hybrid_command(name="unnsfw", description="Remove NSFW marking from a text channel")
    @whitelist_required([Permissions.NSFW])
    async def unnsfw(self, ctx: commands.Context, channel: discord.TextChannel = None):
        """Remove NSFW marking from a text channel"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        target_channel = channel or ctx.channel
        
        # Check bot permissions
        if not target_channel.permissions_for(ctx.guild.me).manage_channels:
            await ctx.send("❌ I don't have permission to manage that channel.")
            return
        
        # Check if not NSFW
        if not target_channel.nsfw:
            await ctx.send(f"❌ {target_channel.mention} is not marked as NSFW.")
            return
        
        try:
            await target_channel.edit(nsfw=False, reason=f"NSFW disabled by {ctx.author}")
            
            embed = EmbedBuilder.create_moderation_embed(
                "NSFW Removed",
                ctx.author,
                ctx.author,
                f"NSFW marking removed from {target_channel.mention}",
                {
                    "Channel": target_channel.mention,
                    "Action": "NSFW marking removed"
                }
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to edit that channel.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to remove NSFW marking: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.hybrid_group(name="role", description="Role management commands")
    @whitelist_required([Permissions.MANAGE_ROLES])
    async def role(self, ctx: commands.Context):
        """Role management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Role Management Commands",
                description="Available role management commands:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands",
                value=(
                    "`role add @user @role` - Add role to user\n"
                    "`role remove @user @role` - Remove role from user\n"
                    "`role create <name> [color]` - Create new role\n"
                    "`role delete @role` - Delete role\n"
                    "`role info @role` - Get role information"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
    
    @role.command(name="add", description="Add role to user")
    async def role_add(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Add a role to a user"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Check if user already has the role
        if role in user.roles:
            await ctx.send(f"❌ {user.mention} already has the {role.mention} role.")
            return
        
        # Check bot permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("❌ I don't have permission to manage roles.")
            return
        
        # Check role hierarchy
        if role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot assign roles higher than or equal to my highest role.")
            return
        
        try:
            await user.add_roles(role, reason=f"Role added by {ctx.author}")
            
            embed = EmbedBuilder.create_moderation_embed(
                "Role Added",
                user,
                ctx.author,
                f"Added {role.mention} role",
                {
                    "Role": role.mention,
                    "User": user.mention
                }
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to assign that role.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to add role: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @role.command(name="remove", description="Remove role from user")
    async def role_remove(self, ctx: commands.Context, user: discord.Member, role: discord.Role):
        """Remove a role from a user"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Check if user has the role
        if role not in user.roles:
            await ctx.send(f"❌ {user.mention} doesn't have the {role.mention} role.")
            return
        
        # Check bot permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("❌ I don't have permission to manage roles.")
            return
        
        # Check role hierarchy
        if role >= ctx.guild.me.top_role:
            await ctx.send("❌ I cannot remove roles higher than or equal to my highest role.")
            return
        
        try:
            await user.remove_roles(role, reason=f"Role removed by {ctx.author}")
            
            embed = EmbedBuilder.create_moderation_embed(
                "Role Removed",
                user,
                ctx.author,
                f"Removed {role.mention} role",
                {
                    "Role": role.mention,
                    "User": user.mention
                }
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to remove that role.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to remove role: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @role.command(name="create", description="Create a new role")
    async def role_create(self, ctx: commands.Context, name: str, color: str = None):
        """Create a new role"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        # Check bot permissions
        if not ctx.guild.me.guild_permissions.manage_roles:
            await ctx.send("❌ I don't have permission to manage roles.")
            return
        
        # Parse color
        role_color = discord.Color.default()
        if color:
            try:
                if color.startswith('#'):
                    role_color = discord.Color(int(color[1:], 16))
                else:
                    role_color = discord.Color(int(color, 16))
            except ValueError:
                await ctx.send("❌ Invalid color format. Use hex format like #FF0000 or FF0000")
                return
        
        try:
            new_role = await ctx.guild.create_role(
                name=name,
                color=role_color,
                reason=f"Role created by {ctx.author}"
            )
            
            embed = EmbedBuilder.create_success_embed(
                "Role Created",
                f"Successfully created role {new_role.mention}",
                ctx.author
            )
            embed.add_field(name="Role Name", value=name, inline=True)
            embed.add_field(name="Color", value=str(role_color), inline=True)
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create roles.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to create role: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @commands.hybrid_group(name="channel", description="Channel management commands")
    @whitelist_required([Permissions.MANAGE_CHANNELS])
    async def channel(self, ctx: commands.Context):
        """Channel management commands"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(
                title="Channel Management Commands",
                description="Available channel management commands:",
                color=discord.Color.blue()
            )
            embed.add_field(
                name="Commands",
                value=(
                    "`channel create text <name>` - Create text channel\n"
                    "`channel create voice <name>` - Create voice channel\n"
                    "`channel delete <channel>` - Delete channel\n"
                    "`channel lock <channel>` - Lock channel\n"
                    "`channel unlock <channel>` - Unlock channel"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
    
    @channel.group(name="create", description="Create channels")
    async def channel_create(self, ctx: commands.Context):
        """Create channel commands"""
        pass
    
    @channel_create.command(name="text", description="Create text channel")
    async def create_text_channel(self, ctx: commands.Context, *, name: str):
        """Create a text channel"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("❌ I don't have permission to manage channels.")
            return
        
        try:
            new_channel = await ctx.guild.create_text_channel(
                name=name,
                reason=f"Text channel created by {ctx.author}"
            )
            
            embed = EmbedBuilder.create_success_embed(
                "Text Channel Created",
                f"Successfully created {new_channel.mention}",
                ctx.author
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create channels.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to create channel: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")
    
    @channel_create.command(name="voice", description="Create voice channel")
    async def create_voice_channel(self, ctx: commands.Context, *, name: str):
        """Create a voice channel"""
        if not ctx.guild:
            await ctx.send("❌ This command can only be used in a server.")
            return
        
        if not ctx.guild.me.guild_permissions.manage_channels:
            await ctx.send("❌ I don't have permission to manage channels.")
            return
        
        try:
            new_channel = await ctx.guild.create_voice_channel(
                name=name,
                reason=f"Voice channel created by {ctx.author}"
            )
            
            embed = EmbedBuilder.create_success_embed(
                "Voice Channel Created",
                f"Successfully created voice channel **{new_channel.name}**",
                ctx.author
            )
            
            await ctx.send(embed=embed)
            
        except discord.Forbidden:
            await ctx.send("❌ I don't have permission to create channels.")
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to create channel: {str(e)}")
        except Exception as e:
            await ctx.send(f"❌ An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(ModerationCog(bot))
