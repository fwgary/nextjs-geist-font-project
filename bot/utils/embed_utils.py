import discord
from datetime import datetime
from typing import Optional, List

class EmbedBuilder:
    @staticmethod
    def create_log_embed(title: str, description: str, color: discord.Color = discord.Color.blue(), 
                        fields: List[dict] = None, timestamp: datetime = None) -> discord.Embed:
        """Create a standardized log embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=timestamp or datetime.now()
        )
        
        if fields:
            for field in fields:
                embed.add_field(
                    name=field.get('name', 'Field'),
                    value=field.get('value', 'No value'),
                    inline=field.get('inline', False)
                )
        
        embed.set_footer(text="Security Bot Logs")
        return embed
    
    @staticmethod
    def create_command_log_embed(user: discord.Member, command: str, args: str = None, 
                               success: bool = True, error: str = None) -> discord.Embed:
        """Create command execution log embed"""
        color = discord.Color.green() if success else discord.Color.red()
        status = "✅ Success" if success else "❌ Failed"
        
        embed = discord.Embed(
            title=f"Command Executed: {command}",
            color=color,
            timestamp=datetime.now()
        )
        
        embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        embed.add_field(name="Status", value=status, inline=True)
        embed.add_field(name="Channel", value=f"<#{user.voice.channel.id if user.voice else 'N/A'}>", inline=True)
        
        if args:
            embed.add_field(name="Arguments", value=f"```{args}```", inline=False)
        
        if error:
            embed.add_field(name="Error", value=f"```{error}```", inline=False)
        
        embed.set_footer(text="Command Log")
        return embed
    
    @staticmethod
    def create_deleted_message_embed(message: discord.Message) -> discord.Embed:
        """Create deleted message log embed"""
        embed = discord.Embed(
            title="Message Deleted",
            color=discord.Color.orange(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author.id})", inline=True)
        embed.add_field(name="Channel", value=f"<#{message.channel.id}>", inline=True)
        embed.add_field(name="Message ID", value=message.id, inline=True)
        
        if message.content:
            content = message.content[:1000] + "..." if len(message.content) > 1000 else message.content
            embed.add_field(name="Content", value=f"```{content}```", inline=False)
        
        if message.attachments:
            attachment_list = "\n".join([att.url for att in message.attachments])
            embed.add_field(name="Attachments", value=attachment_list, inline=False)
        
        embed.set_footer(text="Deleted Message Log")
        return embed
    
    @staticmethod
    def create_snipe_embed(author_id: str, content: str, attachments: List[str], 
                          deleted_at: datetime) -> discord.Embed:
        """Create message snipe embed"""
        embed = discord.Embed(
            title="Sniped Message",
            color=discord.Color.purple(),
            timestamp=deleted_at
        )
        
        embed.add_field(name="Author", value=f"<@{author_id}>", inline=True)
        embed.add_field(name="Deleted", value=f"<t:{int(deleted_at.timestamp())}:R>", inline=True)
        
        if content:
            content_display = content[:1000] + "..." if len(content) > 1000 else content
            embed.add_field(name="Content", value=f"```{content_display}```", inline=False)
        
        if attachments and attachments != '[]':
            try:
                att_list = eval(attachments) if isinstance(attachments, str) else attachments
                if att_list:
                    embed.add_field(name="Attachments", value="\n".join(att_list), inline=False)
            except:
                pass
        
        embed.set_footer(text="Message Snipe")
        return embed
    
    @staticmethod
    def create_moderation_embed(action: str, target: discord.Member, moderator: discord.Member, 
                              reason: str = None, additional_info: dict = None) -> discord.Embed:
        """Create moderation action embed"""
        embed = discord.Embed(
            title=f"Moderation Action: {action}",
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        embed.add_field(name="Target", value=f"{target.mention} ({target.id})", inline=True)
        embed.add_field(name="Moderator", value=f"{moderator.mention} ({moderator.id})", inline=True)
        
        if reason:
            embed.add_field(name="Reason", value=reason, inline=False)
        
        if additional_info:
            for key, value in additional_info.items():
                embed.add_field(name=key, value=str(value), inline=True)
        
        embed.set_footer(text="Moderation Log")
        return embed
    
    @staticmethod
    def create_error_embed(error_title: str, error_message: str, 
                          user: Optional[discord.Member] = None) -> discord.Embed:
        """Create error embed"""
        embed = discord.Embed(
            title=f"❌ {error_title}",
            description=error_message,
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        
        if user:
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        
        embed.set_footer(text="Error Log")
        return embed
    
    @staticmethod
    def create_success_embed(title: str, description: str, 
                           user: Optional[discord.Member] = None) -> discord.Embed:
        """Create success embed"""
        embed = discord.Embed(
            title=f"✅ {title}",
            description=description,
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        
        if user:
            embed.add_field(name="User", value=f"{user.mention} ({user.id})", inline=True)
        
        embed.set_footer(text="Success Log")
        return embed
