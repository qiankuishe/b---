import json
from datetime import datetime
from typing import List, Dict, Optional
from config_path import get_queue_data_path

class QueueManager:
    def __init__(self):
        self.queue: List[Dict] = []
        self.current_number = 0
        
    def add_user(self, uid: int, username: str) -> tuple[bool, str]:
        if any(u['uid'] == uid for u in self.queue):
            return False, f"@{username} 你已经在队列中了"
        
        self.current_number += 1
        self.queue.append({
            'uid': uid,
            'username': username,
            'number': self.current_number,
            'time': datetime.now().strftime('%H:%M:%S')
        })
        position = len(self.queue)
        return True, f"@{username} 排队成功！你是第{position}位，排队号{self.current_number}"
    
    def remove_user(self, uid: int) -> tuple[bool, str]:
        for i, user in enumerate(self.queue):
            if user['uid'] == uid:
                username = user['username']
                self.queue.pop(i)
                return True, f"@{username} 已取消排队"
        return False, "你不在队列中"
    
    def remove_by_index(self, index: int) -> bool:
        if 0 <= index < len(self.queue):
            self.queue.pop(index)
            return True
        return False
    
    def insert_user(self, uid: int, username: str, position: int) -> bool:
        if position < 0 or position > len(self.queue):
            return False
        self.current_number += 1
        self.queue.insert(position, {
            'uid': uid,
            'username': username,
            'number': self.current_number,
            'time': datetime.now().strftime('%H:%M:%S')
        })
        return True
    
    def next_user(self) -> Optional[Dict]:
        if self.queue:
            return self.queue.pop(0)
        return None
    
    def get_queue(self, limit: Optional[int] = None) -> List[Dict]:
        return self.queue[:limit] if limit else self.queue
    
    def clear(self):
        self.queue.clear()
    
    def save(self, filename=None):
        if filename is None:
            filename = get_queue_data_path()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'queue': self.queue,
                'current_number': self.current_number
            }, f, ensure_ascii=False, indent=2)
    
    def load(self, filename=None):
        if filename is None:
            filename = get_queue_data_path()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.queue = data.get('queue', [])
                self.current_number = data.get('current_number', 0)
        except FileNotFoundError:
            pass
