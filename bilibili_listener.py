import asyncio
import json
from bilibili_api import live, sync, Credential
from queue_manager import QueueManager
from config_path import get_config_path

class BilibiliListener:
    def __init__(self, room_id: int, credential: Credential, queue_manager: QueueManager, config: dict):
        self.room_id = room_id
        self.credential = credential
        self.queue_manager = queue_manager
        self.config = config
        self.room = live.LiveDanmaku(room_id, credential=credential)
        
    async def send_danmaku(self, message: str):
        try:
            room_obj = live.LiveRoom(self.room_id, self.credential)
            await room_obj.send_danmaku(message)
        except Exception as e:
            print(f"发送弹幕失败: {e}")
    
    async def on_danmaku(self, event):
        try:
            msg = event['data']['info'][1]
            uid = event['data']['info'][2][0]
            username = event['data']['info'][2][1]
            
            join_cmd = self.config['commands']['join']
            cancel_cmd = self.config['commands']['cancel']
            
            if msg == join_cmd:
                success, reply = self.queue_manager.add_user(uid, username)
                await self.send_danmaku(reply)
                
            elif msg == cancel_cmd:
                success, reply = self.queue_manager.remove_user(uid)
                if success:
                    await self.send_danmaku(reply)
                    
        except Exception as e:
            print(f"处理弹幕错误: {e}")
    
    async def start(self):
        @self.room.on('DANMU_MSG')
        async def danmaku_handler(event):
            await self.on_danmaku(event)
        
        await self.room.connect()
    
    def run(self):
        asyncio.run(self.start())

def load_config():
    with open(get_config_path(), 'r', encoding='utf-8') as f:
        return json.load(f)

def create_listener():
    config = load_config()
    credential = Credential(
        sessdata=config['credential']['sessdata'],
        bili_jct=config['credential']['bili_jct'],
        buvid3=config['credential']['buvid3']
    )
    queue_manager = QueueManager()
    queue_manager.load()
    
    return BilibiliListener(config['room_id'], credential, queue_manager, config)
