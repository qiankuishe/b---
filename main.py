import sys
import json
import os
import threading
from PyQt5.QtWidgets import QApplication, QMessageBox
from queue_manager import QueueManager
from admin_window import AdminWindow
from transparent_display import TransparentDisplay
from bilibili_listener import create_listener
from auto_updater import AutoUpdater
from config_wizard import show_config_wizard
from config_path import get_config_path
from process_manager import kill_existing_process

def load_config():
    with open(get_config_path(), 'r', encoding='utf-8') as f:
        return json.load(f)

def check_config():
    if not os.path.exists(get_config_path()):
        return False
    
    try:
        config = load_config()
        if not config['credential']['sessdata'] or config['room_id'] == 0:
            return False
        return True
    except:
        return False

def main():
    # 杀掉旧进程
    kill_existing_process()
    
    app = QApplication(sys.argv)
    
    # 检查配置，如果不存在则显示配置向导
    if not check_config():
        if not show_config_wizard():
            sys.exit(0)
    
    # 检查更新
    try:
        updater = AutoUpdater()
        has_update, new_version, _ = updater.check_update()
        if has_update:
            reply = QMessageBox.question(None, '更新提示', 
                                        f'发现新版本 v{new_version}，是否更新？',
                                        QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                if updater.auto_update():
                    sys.exit(0)
    except Exception as e:
        print(f"检查更新失败: {e}")
    
    # 初始化队列管理器
    queue_manager = QueueManager()
    queue_manager.load()
    
    # 启动管理窗口
    admin_window = AdminWindow(queue_manager)
    admin_window.show()
    
    # 启动显示窗口
    config = load_config()
    display_window = TransparentDisplay(queue_manager, config['display_count'])
    display_window.show()
    
    # 连接信号
    admin_window.queue_updated.connect(display_window.update_display)
    
    # 启动弹幕监听（在后台线程）
    def start_listener():
        try:
            listener = create_listener()
            listener.run()
        except Exception as e:
            print(f"弹幕监听错误: {e}")
    
    listener_thread = threading.Thread(target=start_listener, daemon=True)
    listener_thread.start()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
