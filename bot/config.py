import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('../.env.local')

class Config:
    # Discord Bot Settings
    DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
    BOT_PREFIX = '!'
    
    # Channel IDs
    LOG_CHANNEL_ID = os.getenv('LOG_CHANNEL_ID')
    
    # Database
    DATABASE_PATH = './data/bot.db'
    
    # Logging
    LOG_DIR = './data/logs'
    
    # Bot Settings
    CASE_INSENSITIVE = True
    STRIP_AFTER_PREFIX = True
    
    # Permissions
    DEFAULT_ADMIN_ROLES = ['Admin', 'Administrator', 'Moderator']
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.DISCORD_TOKEN:
            raise ValueError("DISCORD_TOKEN is required in environment variables")
        
        return True
