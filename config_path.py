import os
import sys

def get_app_dir():
    """获取应用数据目录"""
    if sys.platform == 'win32':
        app_dir = os.path.join(os.getenv('APPDATA'), 'BilibiliQueueSystem')
    else:
        app_dir = os.path.join(os.path.expanduser('~'), '.bilibili_queue')
    
    os.makedirs(app_dir, exist_ok=True)
    return app_dir

def get_config_path():
    return os.path.join(get_app_dir(), 'config.json')

def get_queue_data_path():
    return os.path.join(get_app_dir(), 'queue_data.json')

def get_version_path():
    """获取version.json路径（打包后在程序目录）"""
    if getattr(sys, 'frozen', False):
        # 打包后
        return os.path.join(sys._MEIPASS, 'version.json')
    else:
        # 开发环境
        return 'version.json'
