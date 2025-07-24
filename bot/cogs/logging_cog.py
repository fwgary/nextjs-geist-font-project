import discord
from discord.ext import commands
from datetime import datetime
import logging
import sys
import os
from utils.file_utils import FileLogger
from utils.embed_utils import EmbedBuilder
from utils.permissions import whitelist_required, Permissions

class LoggingCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.file_logger = FileLogger()
        self.setup_console_logging()
    
    def setup_console_logging(self):
        """Setup console logging with file output"""
        # Create custom logger
        self.logger = logging.getLogger('security_bot')
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    async def log_to_channel(self, embed: discord.Embed):
        """Send log embed to designated log channel"""
        if not self.bot.config.LOG_CHANNEL_ID:
            return
        
        try:
            channel = self.bot.get_channel(int(self.bot.config.LOG_CHANNEL_ID))
            if channel:
                await channel.send(embed=embed)
        except Exception as e:
            self.logger.error(f"Failed to send log to channel: {e}")
    
    async def log_console(self, message: str, level: str = "INFO"):
        """Log message to console and file"""
        timestamp = datetime.now()
        
        # Log to console
        if level.upper() == "ERROR":
            self.logger.error(message)
        elif level.upper() == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
        
        # Log to file
        await self.file_logger.write_log('console', f"[{level.upper()}] {message}", timestamp)
    
    async def log_command(self, ctx: commands.Context, success: bool = True, error: str = None):
        """Log command execution"""
        timestamp = datetime.now()
        
        # Prepare command info
        command_name = ctx.command.name if ctx.command else "unknown"
        args = " ".join(ctx.args[2:]) if len(ctx.args) > 2 else ""
        
        # Log to database
        await self.bot.db.log_command(
            str(ctx.guild.id) if ctx.guild else "DM",
            str(ctx.channel.id),
            str(ctx.author.id),
            command_name,
            args,
            success,
            error
        )
        
        # Log to file
        log_data = {
            "guild_id": str(ctx.guild.id) if ctx.guild else "DM",
            "channel_id": str(ctx.channel.id),
            "user_id": str(ctx.author.id),
            "username": str(ctx.author),
            "command": command_name,
            "args": args,
            "success": success,
            "error": error
        }
        await self.file_logger.write_json_log('commands', log_data, timestamp)
        
        # Send embed to log channel
        embed = EmbedBuilder.create_command_log_embed(
            ctx.author, command_name, args, success, error
        )
        await self.log_to_channel(embed)
    
    async def log_deleted_message(self, message: discord.Message):
        """Log deleted message"""
        timestamp = datetime.now()
        
        # Store in database
        attachments = [att.url for att in message.attachments] if message.attachments else []
        await self.bot.db.store_deleted_message(
            str(message.id),
            str(message.channel.id),
            str(message.guild.id) if message.guild else "DM",
            str(message.author.id),
            message.content,
            attachments
        )
        
        # Log to file
        log_data = {
            "message_id": str(message.id),
            "channel_id": str(message.channel.id),
            "guild_id": str(message.guild.id) if message.guild else "DM",
            "author_id": str(message.author.id),
            "author_name": str(message.author),
            "content": message.content,
            "attachments": attachments
        }
        await self.file_logger.write_json_log('deleted', log_data, timestamp)
        
        # Send embed to log channel
        embed = EmbedBuilder.create_deleted_message_embed(message)
        await self.log_to_channel(embed)
    
    @commands.hybrid_command(name="logs", description="View recent logs")
    @whitelist_required([Permissions.VIEW_LOGS])
    async def view_logs(self, ctx: commands.Context, log_type: str = "commands", limit: int = 10):
        """View recent logs"""
        if log_type not in ['console', 'commands', 'deleted']:
            await ctx.send("❌ Invalid log type. Use: console, commands, or deleted")
            return
        
        if limit > 50:
            limit = 50
        
        try:
            logs = await self.file_logger.read_logs(log_type, limit=limit)
            
            if not logs:
                await ctx.send(f"No {log_type} logs found for today.")
                return
            
            # Format logs for display
            log_content = "```\n" + "".join(logs[-limit:]) + "```"
            
            # Split if too long
            if len(log_content) > 2000:
                log_content = log_content[:1997] + "```"
            
            embed = discord.Embed(
                title=f"Recent {log_type.title()} Logs",
                description=log_content,
                color=discord.Color.blue(),
                timestamp=datetime.now()
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            await ctx.send(f"❌ Error retrieving logs: {str(e)}")
    
    @commands.hybrid_command(name="clearlog", description="Clear log files")
    @whitelist_required([Permissions.CLEAR_LOGS])
    async def clear_logs(self, ctx: commands.Context, log_type: str, confirm: str = None):
        """Clear log files (requires confirmation)"""
        if log_type not in ['console', 'commands', 'deleted', 'all']:
            await ctx.send("❌ Invalid log type. Use: console, commands, deleted, or all")
            return
        
        if confirm != "CONFIRM":
            await ctx.send(
                f"⚠️ This will permanently delete {log_type} logs for today.\n"
                f"To confirm, use: `{ctx.prefix}clearlog {log_type} CONFIRM`"
            )
            return
        
        try:
            if log_type == "all":
                types_to_clear = ['console', 'commands', 'deleted']
            else:
                types_to_clear = [log_type]
            
            for log_t in types_to_clear:
                log_path = self.file_logger.get_log_path(log_t)
                if os.path.exists(log_path):
                    os.remove(log_path)
            
            embed = EmbedBuilder.create_success_embed(
                "Logs Cleared",
                f"Successfully cleared {log_type} logs for today.",
                ctx.author
            )
            await ctx.send(embed=embed)
            
            # Log this action
            await self.log_console(f"Logs cleared by {ctx.author} ({ctx.author.id}): {log_type}")
            
        except Exception as e:
            await ctx.send(f"❌ Error clearing logs: {str(e)}")
    
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        """Handle message deletion events"""
        # Ignore bot messages and DMs
        if message.author.bot or not message.guild:
            return
        
        await self.log_deleted_message(message)
    
    @commands.Cog.listener()
    async def on_command_completion(self, ctx: commands.Context):
        """Handle successful command completion"""
        await self.log_command(ctx, success=True)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: Exception):
        """Handle command errors"""
        error_message = str(error)
        await self.log_command(ctx, success=False, error=error_message)
        
        # Log to console as well
        await self.log_console(f"Command error in {ctx.guild.name if ctx.guild else 'DM'}: {error_message}", "ERROR")

async def setup(bot):
    await bot.add_cog(LoggingCog(bot))
