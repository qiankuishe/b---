import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from queue_manager import QueueManager

class AdminWindow(QMainWindow):
    queue_updated = pyqtSignal()
    
    def __init__(self, queue_manager: QueueManager):
        super().__init__()
        self.queue_manager = queue_manager
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('排队系统管理端')
        self.setGeometry(100, 100, 900, 500)
        
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QHBoxLayout(central)
        
        # 左侧：队列管理
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        
        # 队列列表
        self.queue_list = QListWidget()
        left_layout.addWidget(QLabel('当前队列:'))
        left_layout.addWidget(self.queue_list)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        
        self.next_btn = QPushButton('叫号')
        self.next_btn.clicked.connect(self.next_user)
        btn_layout.addWidget(self.next_btn)
        
        self.remove_btn = QPushButton('删除')
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.insert_btn = QPushButton('插队')
        self.insert_btn.clicked.connect(self.insert_user)
        btn_layout.addWidget(self.insert_btn)
        
        self.clear_btn = QPushButton('清空')
        self.clear_btn.clicked.connect(self.clear_queue)
        btn_layout.addWidget(self.clear_btn)
        
        self.config_btn = QPushButton('设置')
        self.config_btn.clicked.connect(self.open_config)
        btn_layout.addWidget(self.config_btn)
        
        self.update_btn = QPushButton('更新')
        self.update_btn.clicked.connect(self.check_update)
        btn_layout.addWidget(self.update_btn)
        
        left_layout.addLayout(btn_layout)
        
        # 右侧：日志
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.addWidget(QLabel('日志:'))
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumWidth(250)
        self.log_text.setStyleSheet('font-size: 12px;')
        right_layout.addWidget(self.log_text)
        
        # 添加到主布局
        main_layout.addWidget(left_widget, 3)
        main_layout.addWidget(right_widget, 1)
        
        # 日志行数限制
        self.max_log_lines = 100
        
        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_queue)
        self.timer.start(1000)
        
        self.refresh_queue()
        self.add_log('系统启动')
    
    def refresh_queue(self):
        self.queue_list.clear()
        for i, user in enumerate(self.queue_manager.get_queue()):
            self.queue_list.addItem(
                f"#{i+1} - {user['username']} (UID:{user['uid']}) - {user['time']}"
            )
        self.queue_updated.emit()
        self.queue_manager.save()
    
    def add_log(self, message):
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.log_text.append(f"[{timestamp}] {message}")
        
        # 限制日志行数
        lines = self.log_text.toPlainText().split('\n')
        if len(lines) > self.max_log_lines:
            self.log_text.setPlainText('\n'.join(lines[-self.max_log_lines:]))
        
        # 滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def next_user(self):
        user = self.queue_manager.next_user()
        if user:
            QMessageBox.information(self, '叫号', f"当前用户: {user['username']}\nUID: {user['uid']}")
            self.add_log(f"叫号: {user['username']}")
            self.refresh_queue()
        else:
            QMessageBox.warning(self, '提示', '队列为空')
    
    def remove_selected(self):
        current = self.queue_list.currentRow()
        if current >= 0:
            user = self.queue_manager.queue[current]
            self.queue_manager.remove_by_index(current)
            self.add_log(f"删除: {user['username']}")
            self.refresh_queue()
    
    def insert_user(self):
        dialog = QDialog(self)
        dialog.setWindowTitle('插队')
        layout = QFormLayout(dialog)
        
        uid_input = QLineEdit()
        username_input = QLineEdit()
        position_input = QSpinBox()
        position_input.setMinimum(0)
        position_input.setMaximum(len(self.queue_manager.queue))
        
        layout.addRow('UID:', uid_input)
        layout.addRow('用户名:', username_input)
        layout.addRow('插入位置:', position_input)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            try:
                uid = int(uid_input.text())
                username = username_input.text()
                position = position_input.value()
                self.queue_manager.insert_user(uid, username, position)
                self.add_log(f"插队: {username} 位置{position}")
                self.refresh_queue()
            except ValueError:
                QMessageBox.warning(self, '错误', 'UID必须是数字')
    
    def clear_queue(self):
        reply = QMessageBox.question(self, '确认', '确定要清空队列吗?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            count = len(self.queue_manager.queue)
            self.queue_manager.clear()
            self.add_log(f"清空队列 ({count}人)")
            self.refresh_queue()
    
    def open_config(self):
        from config_wizard import show_config_wizard
        if show_config_wizard():
            QMessageBox.information(self, '提示', '配置已更新，请重启程序生效')
    
    def check_update(self):
        from auto_updater import AutoUpdater
        try:
            self.add_log('检查更新...')
            updater = AutoUpdater()
            has_update, new_version, download_url = updater.check_update()
            
            if has_update:
                self.add_log(f'发现新版本: v{new_version}')
                reply = QMessageBox.question(
                    self, '发现新版本', 
                    f'当前版本: v{updater.current_version}\n新版本: v{new_version}\n\n是否立即更新？',
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    self.add_log('开始下载更新...')
                    self.update_btn.setEnabled(False)
                    
                    def progress_callback(progress, slow=False, timeout=False):
                        if timeout:
                            self.add_log('连接速度慢，请切换网络或手动更新')
                        elif slow:
                            self.add_log(f'当前进度: {progress}% (速度较慢)')
                        else:
                            self.add_log(f'下载进度: {progress}%')
                    
                    if updater.download_update(download_url, progress_callback=progress_callback):
                        self.add_log('下载完成，正在安装...')
                        if updater.apply_update():
                            self.add_log('更新完成，即将重启')
                            import sys
                            sys.exit(0)
                        else:
                            self.add_log('安装失败')
                            self.update_btn.setEnabled(True)
                    else:
                        self.add_log('下载失败')
                        self.update_btn.setEnabled(True)
            else:
                self.add_log(f'当前已是最新版本 v{updater.current_version}')
        except Exception as e:
            self.add_log(f'检查更新失败: {str(e)}')
