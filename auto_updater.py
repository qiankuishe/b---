import json
import requests
import os
import sys
import zipfile
import shutil
from packaging import version
from config_path import get_version_path

class AutoUpdater:
    def __init__(self):
        with open(get_version_path(), 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.current_version = data['version']
            self.repo = data['github_repo']
        
        self.api_url = f'https://api.github.com/repos/{self.repo}/releases/latest'
    
    def check_update(self) -> tuple[bool, str, str]:
        try:
            response = requests.get(self.api_url, timeout=10)
            if response.status_code != 200:
                return False, '', ''
            
            data = response.json()
            latest_version = data['tag_name'].lstrip('v')
            
            if version.parse(latest_version) > version.parse(self.current_version):
                download_url = data['assets'][0]['browser_download_url'] if data['assets'] else ''
                return True, latest_version, download_url
            
            return False, latest_version, ''
        except Exception as e:
            print(f"检查更新失败: {e}")
            return False, '', ''
    
    def download_update(self, url: str, filename: str = 'update.exe', progress_callback=None) -> bool:
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                return False
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            last_progress = -1
            timeout_count = 0
            last_update_time = __import__('time').time()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = int(downloaded * 100 / total_size)
                        current_time = __import__('time').time()
                        
                        # 每10%显示一次
                        if progress // 10 > last_progress // 10:
                            if progress_callback:
                                progress_callback(progress)
                            last_progress = progress
                            timeout_count = 0
                            last_update_time = current_time
                        
                        # 超过15秒没进展
                        elif current_time - last_update_time > 15:
                            if progress_callback:
                                progress_callback(last_progress, slow=True)
                            last_update_time = current_time
                            timeout_count += 1
                            
                            if timeout_count >= 3:
                                if progress_callback:
                                    progress_callback(-1, timeout=True)
                                return False
            
            return True
        except Exception as e:
            print(f"下载更新失败: {e}")
            return False
    
    def apply_update(self, new_exe: str = 'update.exe') -> bool:
        try:
            import subprocess
            
            # 获取当前exe路径
            if getattr(sys, 'frozen', False):
                current_exe = sys.executable
            else:
                current_exe = 'main.py'
            
            # 创建更新脚本
            update_script = f'''
import time
import os
import sys
import shutil

time.sleep(2)

try:
    if os.path.exists("{current_exe}"):
        os.remove("{current_exe}")
    shutil.move("{new_exe}", "{current_exe}")
    os.startfile("{current_exe}")
except Exception as e:
    print(f"更新失败: {{e}}")
'''
            
            with open('_update.py', 'w', encoding='utf-8') as f:
                f.write(update_script)
            
            # 启动更新脚本
            subprocess.Popen([sys.executable, '_update.py'], 
                           creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            
            return True
            
        except Exception as e:
            print(f"应用更新失败: {e}")
            return False
    
    def auto_update(self) -> bool:
        has_update, new_version, download_url = self.check_update()
        
        if not has_update:
            print(f"当前已是最新版本 v{self.current_version}")
            return False
        
        print(f"发现新版本 v{new_version}，当前版本 v{self.current_version}")
        print("开始下载更新...")
        
        if not self.download_update(download_url):
            print("下载失败")
            return False
        
        print("下载完成，开始应用更新...")
        return self.apply_update()
