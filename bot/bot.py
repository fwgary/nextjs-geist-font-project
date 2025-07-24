import discord
from discord.ext import commands
import asyncio
import os
import sys
from config import Config
from database import Database
from utils.permissions import PermissionManager

class SecurityBot(commands.Bot):
    def __init__(self):
        # Configure intents
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.guilds = True
        intents.voice_states = True
        
        # Initialize bot
        super().__init__(
            command_prefix=Config.BOT_PREFIX,
            intents=intents,
            case_insensitive=Config.CASE_INSENSITIVE,
            strip_after_prefix=Config.STRIP_AFTER_PREFIX,
            help_command=None  # We'll create a custom help command
        )
        
        # Store config
        self.config = Config
        
        # Initialize database
        self.db = Database(Config.DATABASE_PATH)
        
        # Initialize permission manager
        self.permission_manager = PermissionManager(self.db)
        
        # Track startup
        self.startup_time = None
    
    async def setup_hook(self):
        """Setup hook called when bot is starting up"""
        print("🔧 Setting up bot...")
        
        # Initialize database
        await self.db.initialize()
        print("✅ Database initialized")
        
        # Load cogs
        cogs_to_load = [
            'cogs.logging_cog',
            'cogs.whitelist',
            'cogs.moderation'
        ]
        
        for cog in cogs_to_load:
            try:
                await self.load_extension(cog)
                print(f"✅ Loaded {cog}")
            except Exception as e:
                print(f"❌ Failed to load {cog}: {e}")
        
        # Sync slash commands
        try:
            synced = await self.tree.sync()
            print(f"✅ Synced {len(synced)} slash commands")
        except Exception as e:
            print(f"❌ Failed to sync slash commands: {e}")
    
    async def on_ready(self):
        """Called when bot is ready"""
        self.startup_time = discord.utils.utcnow()
        
        print(f"\n🤖 {self.user} is now online!")
        print(f"📊 Connected to {len(self.guilds)} guilds")
        print(f"👥 Serving {len(set(self.get_all_members()))} users")
        print(f"🔧 Prefix: {Config.BOT_PREFIX}")
        print(f"🆔 Bot ID: {self.user.id}")
        print("=" * 50)
        
        # Set bot status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {Config.BOT_PREFIX}help"
        )
        await self.change_presence(activity=activity)
        
        # Log startup to console
        if hasattr(self, 'get_cog'):
            logging_cog = self.get_cog('LoggingCog')
            if logging_cog:
                await logging_cog.log_console(f"Bot started successfully. Connected to {len(self.guilds)} guilds.")
    
    async def on_guild_join(self, guild):
        """Called when bot joins a new guild"""
        print(f"📥 Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Update status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {Config.BOT_PREFIX}help"
        )
        await self.change_presence(activity=activity)
        
        # Log to console
        logging_cog = self.get_cog('LoggingCog')
        if logging_cog:
            await logging_cog.log_console(f"Joined new guild: {guild.name} (ID: {guild.id})")
    
    async def on_guild_remove(self, guild):
        """Called when bot leaves a guild"""
        print(f"📤 Left guild: {guild.name} (ID: {guild.id})")
        
        # Update status
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name=f"{len(self.guilds)} servers | {Config.BOT_PREFIX}help"
        )
        await self.change_presence(activity=activity)
        
        # Log to console
        logging_cog = self.get_cog('LoggingCog')
        if logging_cog:
            await logging_cog.log_console(f"Left guild: {guild.name} (ID: {guild.id})")
    
    async def on_command_error(self, ctx, error):
        """Global error handler"""
        # Ignore command not found errors
        if isinstance(error, commands.CommandNotFound):
            return
        
        # Handle permission errors
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                title="❌ Permission Denied",
                description="You don't have permission to use this command.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed, ephemeral=True)
            return
        
        # Handle missing arguments
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                title="❌ Missing Argument",
                description=f"Missing required argument: `{error.param.name}`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Handle bad arguments
        if isinstance(error, commands.BadArgument):
            embed = discord.Embed(
                title="❌ Invalid Argument",
                description=str(error),
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Handle cooldown errors
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(
                title="❌ Command on Cooldown",
                description=f"Try again in {error.retry_after:.2f} seconds.",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return
        
        # Log unexpected errors
        print(f"❌ Unexpected error in command {ctx.command}: {error}")
        
        embed = discord.Embed(
            title="❌ An Error Occurred",
            description="An unexpected error occurred while processing your command.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="help", description="Show help information")
    async def help_command(self, ctx: commands.Context, *, command: str = None):
        """Custom help command"""
        if command:
            # Show help for specific command
            cmd = self.get_command(command)
            if not cmd:
                await ctx.send(f"❌ Command `{command}` not found.")
                return
            
            embed = discord.Embed(
                title=f"Help: {cmd.name}",
                description=cmd.description or "No description available.",
                color=discord.Color.blue()
            )
            
            if cmd.usage:
                embed.add_field(name="Usage", value=f"`{Config.BOT_PREFIX}{cmd.usage}`", inline=False)
            
            if cmd.aliases:
                embed.add_field(name="Aliases", value=", ".join(cmd.aliases), inline=False)
            
            await ctx.send(embed=embed)
            return
        
        # Show general help
        embed = discord.Embed(
            title="🤖 Security Bot Help",
            description="A comprehensive moderation and security bot for Discord servers.",
            color=discord.Color.blue()
        )
        
        # Moderation commands
        embed.add_field(
            name="🛡️ Moderation",
            value=(
                f"`{Config.BOT_PREFIX}snipe` - Retrieve deleted messages\n"
                f"`{Config.BOT_PREFIX}drag @user #channel` - Move user between voice channels\n"
                f"`{Config.BOT_PREFIX}nsfw [#channel]` - Mark channel as NSFW\n"
                f"`{Config.BOT_PREFIX}role add/remove @user @role` - Manage user roles\n"
                f"`{Config.BOT_PREFIX}channel create text/voice <name>` - Create channels"
            ),
            inline=False
        )
        
        # Whitelist commands
        embed.add_field(
            name="📝 Whitelist",
            value=(
                f"`{Config.BOT_PREFIX}whitelist add user/role` - Add to whitelist\n"
                f"`{Config.BOT_PREFIX}whitelist remove user/role` - Remove from whitelist\n"
                f"`{Config.BOT_PREFIX}whitelist list` - View whitelist\n"
                f"`{Config.BOT_PREFIX}checkperms [@user]` - Check permissions"
            ),
            inline=False
        )
        
        # Logging commands
        embed.add_field(
            name="📊 Logging",
            value=(
                f"`{Config.BOT_PREFIX}logs [type] [limit]` - View logs\n"
                f"`{Config.BOT_PREFIX}clearlog <type> CONFIRM` - Clear logs"
            ),
            inline=False
        )
        
        # Bot info
        embed.add_field(
            name="ℹ️ Bot Info",
            value=(
                f"`{Config.BOT_PREFIX}info` - Bot information\n"
                f"`{Config.BOT_PREFIX}ping` - Check bot latency"
            ),
            inline=False
        )
        
        embed.set_footer(text=f"Use {Config.BOT_PREFIX}help <command> for detailed help on a specific command")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="info", description="Show bot information")
    async def info(self, ctx: commands.Context):
        """Show bot information"""
        embed = discord.Embed(
            title="🤖 Security Bot Information",
            color=discord.Color.blue(),
            timestamp=discord.utils.utcnow()
        )
        
        embed.add_field(name="Bot Version", value="1.0.0", inline=True)
        embed.add_field(name="Discord.py Version", value=discord.__version__, inline=True)
        embed.add_field(name="Python Version", value=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}", inline=True)
        
        embed.add_field(name="Guilds", value=len(self.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(self.get_all_members())), inline=True)
        embed.add_field(name="Commands", value=len(self.commands), inline=True)
        
        if self.startup_time:
            embed.add_field(name="Uptime", value=f"<t:{int(self.startup_time.timestamp())}:R>", inline=True)
        
        embed.add_field(name="Latency", value=f"{round(self.latency * 1000)}ms", inline=True)
        embed.add_field(name="Prefix", value=Config.BOT_PREFIX, inline=True)
        
        embed.set_thumbnail(url=self.user.display_avatar.url)
        embed.set_footer(text="Security Bot | Keeping your server safe")
        
        await ctx.send(embed=embed)
    
    @commands.hybrid_command(name="ping", description="Check bot latency")
    async def ping(self, ctx: commands.Context):
        """Check bot latency"""
        latency = round(self.latency * 1000)
        
        embed = discord.Embed(
            title="🏓 Pong!",
            description=f"Bot latency: **{latency}ms**",
            color=discord.Color.green() if latency < 100 else discord.Color.yellow() if latency < 200 else discord.Color.red()
        )
        
        await ctx.send(embed=embed)

async def main():
    """Main function to run the bot"""
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        return
    
    # Create and run bot
    bot = SecurityBot()
    
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except discord.LoginFailure:
        print("❌ Invalid Discord token. Please check your .env.local file.")
    except Exception as e:
        print(f"❌ An error occurred: {e}")
    finally:
        await bot.close()

if __name__ == "__main__":
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot shutdown requested by user.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
