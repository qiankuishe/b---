import os
import sys
import psutil

def kill_existing_process():
    """杀掉已存在的同名进程"""
    current_pid = os.getpid()
    current_name = os.path.basename(sys.argv[0])
    
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['pid'] != current_pid and proc.info['name'] == current_name:
                proc.kill()
                print(f"已杀掉旧进程: PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
