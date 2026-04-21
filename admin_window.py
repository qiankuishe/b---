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
        self.setGeometry(100, 100, 800, 600)
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 队列列表
        self.queue_list = QListWidget()
        layout.addWidget(QLabel('当前队列:'))
        layout.addWidget(self.queue_list)
        
        # 按钮区
        btn_layout = QHBoxLayout()
        
        self.next_btn = QPushButton('叫号(下一位)')
        self.next_btn.clicked.connect(self.next_user)
        btn_layout.addWidget(self.next_btn)
        
        self.remove_btn = QPushButton('删除选中')
        self.remove_btn.clicked.connect(self.remove_selected)
        btn_layout.addWidget(self.remove_btn)
        
        self.insert_btn = QPushButton('插队')
        self.insert_btn.clicked.connect(self.insert_user)
        btn_layout.addWidget(self.insert_btn)
        
        self.clear_btn = QPushButton('清空队列')
        self.clear_btn.clicked.connect(self.clear_queue)
        btn_layout.addWidget(self.clear_btn)
        
        self.config_btn = QPushButton('设置')
        self.config_btn.clicked.connect(self.open_config)
        btn_layout.addWidget(self.config_btn)
        
        layout.addLayout(btn_layout)
        
        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_queue)
        self.timer.start(1000)
        
        self.refresh_queue()
    
    def refresh_queue(self):
        self.queue_list.clear()
        for i, user in enumerate(self.queue_manager.get_queue()):
            self.queue_list.addItem(
                f"#{i+1} - {user['username']} (UID:{user['uid']}) - {user['time']}"
            )
        self.queue_updated.emit()
        self.queue_manager.save()
    
    def next_user(self):
        user = self.queue_manager.next_user()
        if user:
            QMessageBox.information(self, '叫号', f"当前用户: {user['username']}\nUID: {user['uid']}")
            self.refresh_queue()
        else:
            QMessageBox.warning(self, '提示', '队列为空')
    
    def remove_selected(self):
        current = self.queue_list.currentRow()
        if current >= 0:
            self.queue_manager.remove_by_index(current)
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
                self.refresh_queue()
            except ValueError:
                QMessageBox.warning(self, '错误', 'UID必须是数字')
    
    def clear_queue(self):
        reply = QMessageBox.question(self, '确认', '确定要清空队列吗?',
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.queue_manager.clear()
            self.refresh_queue()
    
    def open_config(self):
        from config_wizard import show_config_wizard
        if show_config_wizard():
            QMessageBox.information(self, '提示', '配置已更新，请重启程序生效')
