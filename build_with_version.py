import json
import os
import subprocess
import sys

# 读取版本号
with open('version.json', 'r', encoding='utf-8') as f:
    version = json.load(f)['version']

# 修改 build.spec 中的版本号
with open('build.spec', 'r', encoding='utf-8') as f:
    spec_content = f.read()

# 替换 name 字段
import re
spec_content = re.sub(
    r"name='paiduiji-v[\d.]+',",
    f"name='paiduiji-v{version}',",
    spec_content
)

with open('build.spec', 'w', encoding='utf-8') as f:
    f.write(spec_content)

print(f"Building paiduiji-v{version}.exe...")

# 执行 pyinstaller
result = subprocess.run(['pyinstaller', 'build.spec'], capture_output=True)
if result.returncode != 0:
    print(result.stderr.decode())
    sys.exit(1)

print(f"Build complete: dist/paiduiji-v{version}.exe")
