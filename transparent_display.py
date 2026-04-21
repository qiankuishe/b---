import sys
import json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from queue_manager import QueueManager

class TransparentDisplay(QWidget):
    def __init__(self, queue_manager: QueueManager, display_count: int = 10):
        super().__init__()
        self.queue_manager = queue_manager
        self.display_count = display_count
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('排队显示')
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.setGeometry(100, 100, 400, 600)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title = QLabel('当前排队')
        title.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background-color: rgba(0, 0, 0, 180);
                padding: 10px;
                border-radius: 5px;
            }
        ''')
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # 队列显示
        self.queue_label = QLabel()
        self.queue_label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 18px;
                background-color: rgba(0, 0, 0, 150);
                padding: 15px;
                border-radius: 5px;
            }
        ''')
        self.queue_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.queue_label.setWordWrap(True)
        layout.addWidget(self.queue_label)
        
        # 定时刷新
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.timer.start(1000)
        
        self.update_display()
        
        # 可拖动
        self.dragging = False
        self.offset = QPoint()
    
    def update_display(self):
        queue = self.queue_manager.get_queue(self.display_count)
        if not queue:
            self.queue_label.setText('暂无排队')
            return
        
        text = ''
        for i, user in enumerate(queue):
            text += f"{i+1}. {user['username']}\n"
        
        self.queue_label.setText(text.strip())
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(self.mapToGlobal(event.pos() - self.offset))
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.RightButton:
            self.close()
