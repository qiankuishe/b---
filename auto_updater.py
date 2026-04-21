import json
import requests
import os
import sys
import zipfile
import shutil
from packaging import version

class AutoUpdater:
    def __init__(self):
        with open('version.json', 'r', encoding='utf-8') as f:
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
    
    def download_update(self, url: str, filename: str = 'update.zip') -> bool:
        try:
            response = requests.get(url, stream=True, timeout=30)
            if response.status_code != 200:
                return False
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return True
        except Exception as e:
            print(f"下载更新失败: {e}")
            return False
    
    def apply_update(self, zip_file: str = 'update.zip') -> bool:
        try:
            backup_dir = 'backup_old_version'
            if os.path.exists(backup_dir):
                shutil.rmtree(backup_dir)
            
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份当前文件
            for item in os.listdir('.'):
                if item not in [backup_dir, zip_file, 'config.json', 'queue_data.json']:
                    src = os.path.join('.', item)
                    dst = os.path.join(backup_dir, item)
                    if os.path.isfile(src):
                        shutil.copy2(src, dst)
                    elif os.path.isdir(src):
                        shutil.copytree(src, dst)
            
            # 解压新版本
            with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                zip_ref.extractall('.')
            
            os.remove(zip_file)
            
            print("更新成功！请重启程序。")
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
