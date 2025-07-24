import aiosqlite
import asyncio
import os
from datetime import datetime

class Database:
    def __init__(self, db_path='./data/bot.db'):
        self.db_path = db_path
        self.ensure_directory()
    
    def ensure_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize(self):
        """Initialize database tables"""
        async with aiosqlite.connect(self.db_path) as db:
            # Whitelist table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS whitelist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL, -- 'user' or 'role'
                    discord_id TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    permissions TEXT DEFAULT '[]', -- JSON array of permissions
                    added_by TEXT NOT NULL,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(type, discord_id, guild_id)
                )
            ''')
            
            # Configuration table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL,
                    key TEXT NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(guild_id, key)
                )
            ''')
            
            # Deleted messages table (for sniping)
            await db.execute('''
                CREATE TABLE IF NOT EXISTS deleted_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    message_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    guild_id TEXT NOT NULL,
                    author_id TEXT NOT NULL,
                    content TEXT,
                    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    attachments TEXT DEFAULT '[]' -- JSON array of attachment URLs
                )
            ''')
            
            # Command logs table
            await db.execute('''
                CREATE TABLE IF NOT EXISTS command_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id TEXT NOT NULL,
                    channel_id TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    command TEXT NOT NULL,
                    args TEXT,
                    success BOOLEAN DEFAULT TRUE,
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            await db.commit()
    
    async def add_to_whitelist(self, type_: str, discord_id: str, guild_id: str, permissions: list, added_by: str):
        """Add user or role to whitelist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO whitelist (type, discord_id, guild_id, permissions, added_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (type_, discord_id, guild_id, str(permissions), added_by))
            await db.commit()
    
    async def remove_from_whitelist(self, type_: str, discord_id: str, guild_id: str):
        """Remove user or role from whitelist"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                DELETE FROM whitelist WHERE type = ? AND discord_id = ? AND guild_id = ?
            ''', (type_, discord_id, guild_id))
            await db.commit()
    
    async def get_whitelist(self, guild_id: str):
        """Get all whitelist entries for a guild"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT type, discord_id, permissions FROM whitelist WHERE guild_id = ?
            ''', (guild_id,)) as cursor:
                return await cursor.fetchall()
    
    async def is_whitelisted(self, user_id: str, role_ids: list, guild_id: str):
        """Check if user or their roles are whitelisted"""
        async with aiosqlite.connect(self.db_path) as db:
            # Check user whitelist
            async with db.execute('''
                SELECT permissions FROM whitelist WHERE type = 'user' AND discord_id = ? AND guild_id = ?
            ''', (user_id, guild_id)) as cursor:
                result = await cursor.fetchone()
                if result:
                    return True, eval(result[0])  # Return permissions
            
            # Check role whitelist
            for role_id in role_ids:
                async with db.execute('''
                    SELECT permissions FROM whitelist WHERE type = 'role' AND discord_id = ? AND guild_id = ?
                ''', (str(role_id), guild_id)) as cursor:
                    result = await cursor.fetchone()
                    if result:
                        return True, eval(result[0])  # Return permissions
            
            return False, []
    
    async def set_config(self, guild_id: str, key: str, value: str):
        """Set configuration value"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT OR REPLACE INTO config (guild_id, key, value)
                VALUES (?, ?, ?)
            ''', (guild_id, key, value))
            await db.commit()
    
    async def get_config(self, guild_id: str, key: str, default=None):
        """Get configuration value"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT value FROM config WHERE guild_id = ? AND key = ?
            ''', (guild_id, key)) as cursor:
                result = await cursor.fetchone()
                return result[0] if result else default
    
    async def store_deleted_message(self, message_id: str, channel_id: str, guild_id: str, 
                                  author_id: str, content: str, attachments: list):
        """Store deleted message for sniping"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO deleted_messages (message_id, channel_id, guild_id, author_id, content, attachments)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (message_id, channel_id, guild_id, author_id, content, str(attachments)))
            await db.commit()
    
    async def get_last_deleted_message(self, channel_id: str):
        """Get last deleted message in channel"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute('''
                SELECT author_id, content, attachments, deleted_at 
                FROM deleted_messages 
                WHERE channel_id = ? 
                ORDER BY deleted_at DESC 
                LIMIT 1
            ''', (channel_id,)) as cursor:
                return await cursor.fetchone()
    
    async def log_command(self, guild_id: str, channel_id: str, user_id: str, 
                         command: str, args: str = None, success: bool = True, error_message: str = None):
        """Log command execution"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                INSERT INTO command_logs (guild_id, channel_id, user_id, command, args, success, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (guild_id, channel_id, user_id, command, args, success, error_message))
            await db.commit()
