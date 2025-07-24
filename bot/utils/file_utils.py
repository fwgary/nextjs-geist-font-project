import os
import aiofiles
from datetime import datetime
import json

class FileLogger:
    def __init__(self, base_dir='./data/logs'):
        self.base_dir = base_dir
        self.ensure_directories()
    
    def ensure_directories(self):
        """Ensure log directories exist"""
        os.makedirs(self.base_dir, exist_ok=True)
    
    def get_log_path(self, log_type: str, date: datetime = None):
        """Get log file path for specific type and date"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        log_dir = os.path.join(self.base_dir, date_str, log_type)
        os.makedirs(log_dir, exist_ok=True)
        
        return os.path.join(log_dir, f'{log_type}.log')
    
    async def write_log(self, log_type: str, message: str, timestamp: datetime = None):
        """Write log message to file"""
        if timestamp is None:
            timestamp = datetime.now()
        
        log_path = self.get_log_path(log_type, timestamp)
        log_entry = f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {message}\n"
        
        try:
            async with aiofiles.open(log_path, 'a', encoding='utf-8') as f:
                await f.write(log_entry)
        except Exception as e:
            print(f"Error writing to log file {log_path}: {e}")
    
    async def write_json_log(self, log_type: str, data: dict, timestamp: datetime = None):
        """Write JSON log entry to file"""
        if timestamp is None:
            timestamp = datetime.now()
        
        data['timestamp'] = timestamp.isoformat()
        log_message = json.dumps(data, ensure_ascii=False)
        await self.write_log(log_type, log_message, timestamp)
    
    async def read_logs(self, log_type: str, date: datetime = None, limit: int = 100):
        """Read log entries from file"""
        log_path = self.get_log_path(log_type, date)
        
        if not os.path.exists(log_path):
            return []
        
        try:
            async with aiofiles.open(log_path, 'r', encoding='utf-8') as f:
                lines = await f.readlines()
                return lines[-limit:] if limit else lines
        except Exception as e:
            print(f"Error reading log file {log_path}: {e}")
            return []
    
    def get_available_dates(self, log_type: str = None):
        """Get list of available log dates"""
        dates = []
        
        if not os.path.exists(self.base_dir):
            return dates
        
        for date_dir in os.listdir(self.base_dir):
            date_path = os.path.join(self.base_dir, date_dir)
            if os.path.isdir(date_path):
                if log_type:
                    log_type_path = os.path.join(date_path, log_type)
                    if os.path.exists(log_type_path):
                        dates.append(date_dir)
                else:
                    dates.append(date_dir)
        
        return sorted(dates, reverse=True)
    
    def get_log_types(self, date: str = None):
        """Get available log types for a specific date"""
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        date_path = os.path.join(self.base_dir, date)
        if not os.path.exists(date_path):
            return []
        
        log_types = []
        for item in os.listdir(date_path):
            item_path = os.path.join(date_path, item)
            if os.path.isdir(item_path):
                log_types.append(item)
        
        return sorted(log_types)
