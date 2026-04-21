import json
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from config_path import get_config_path

class ConfigWizard(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle('B站排队系统 - 配置向导')
        self.setModal(True)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout(self)
        
        # 说明
        info = QLabel('首次使用需要配置B站身份信息')
        info.setStyleSheet('font-size: 14px; color: #666; margin-bottom: 10px;')
        layout.addWidget(info)
        
        # 表单
        form = QFormLayout()
        
        self.room_id = QLineEdit()
        self.room_id.setPlaceholderText('例如: 12345678')
        form.addRow('直播间ID:', self.room_id)
        
        self.sessdata = QLineEdit()
        self.sessdata.setPlaceholderText('从浏览器Cookie获取')
        form.addRow('SESSDATA:', self.sessdata)
        
        self.bili_jct = QLineEdit()
        self.bili_jct.setPlaceholderText('从浏览器Cookie获取')
        form.addRow('bili_jct:', self.bili_jct)
        
        self.buvid3 = QLineEdit()
        self.buvid3.setPlaceholderText('从浏览器Cookie获取')
        form.addRow('buvid3:', self.buvid3)
        
        self.display_count = QSpinBox()
        self.display_count.setRange(1, 50)
        self.display_count.setValue(10)
        form.addRow('显示队列数量:', self.display_count)
        
        layout.addLayout(form)
        
        # 帮助按钮
        help_btn = QPushButton('如何获取身份码？')
        help_btn.clicked.connect(self.show_help)
        layout.addWidget(help_btn)
        
        # 按钮
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_config)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # 加载现有配置
        self.load_existing_config()
    
    def load_existing_config(self):
        config_path = get_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.room_id.setText(str(config.get('room_id', '')))
                    cred = config.get('credential', {})
                    self.sessdata.setText(cred.get('sessdata', ''))
                    self.bili_jct.setText(cred.get('bili_jct', ''))
                    self.buvid3.setText(cred.get('buvid3', ''))
                    self.display_count.setValue(config.get('display_count', 10))
            except:
                pass
    
    def show_help(self):
        help_text = '''获取B站身份码步骤：

1. 打开浏览器，登录 bilibili.com
2. 按 F12 打开开发者工具
3. 切换到 Application（应用程序）标签
4. 左侧选择 Cookies → https://www.bilibili.com
5. 找到并复制以下三个值：
   - SESSDATA
   - bili_jct
   - buvid3

注意：身份码请妥善保管，不要泄露给他人！'''
        
        QMessageBox.information(self, '帮助', help_text)
    
    def save_config(self):
        room_id = self.room_id.text().strip()
        sessdata = self.sessdata.text().strip()
        bili_jct = self.bili_jct.text().strip()
        buvid3 = self.buvid3.text().strip()
        
        if not room_id or not sessdata or not bili_jct or not buvid3:
            QMessageBox.warning(self, '错误', '请填写所有必填项！')
            return
        
        try:
            room_id = int(room_id)
        except ValueError:
            QMessageBox.warning(self, '错误', '直播间ID必须是数字！')
            return
        
        config = {
            "room_id": room_id,
            "credential": {
                "sessdata": sessdata,
                "bili_jct": bili_jct,
                "buvid3": buvid3
            },
            "display_count": self.display_count.value(),
            "commands": {
                "join": "排队",
                "cancel": "取消排队"
            }
        }
        
        config_path = get_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        QMessageBox.information(self, '成功', '配置已保存！')
        self.accept()

def show_config_wizard():
    wizard = ConfigWizard()
    return wizard.exec_() == QDialog.Accepted
