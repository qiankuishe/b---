# B站直播间排队系统

一个用于B站直播间的排队管理系统，支持弹幕互动、队列管理和半透明显示窗口。

## 功能特性

- 🎯 **弹幕互动**: 观众发送"排队"加入队列，发送"取消排队"退出队列
- 🎮 **管理客户端**: 支持删除、插队、叫号、清空等管理操作
- 👀 **半透明显示**: OBS可捕获的半透明窗口，实时显示队列状态
- 🔄 **自动更新**: 基于GitHub Releases的一键更新功能

## 安装

### 方式一：下载exe（推荐）

1. 前往 [Releases](https://github.com/YOUR_USERNAME/bilibili-queue-system/releases) 页面
2. 下载最新版本的 `BilibiliQueueSystem.zip`
3. 解压后运行 `BilibiliQueueSystem.exe`
4. 首次运行会弹出配置向导，填写以下信息：
   - 直播间ID
   - B站身份码（SESSDATA、bili_jct、buvid3）
   - 显示队列数量
5. 点击"如何获取身份码？"查看详细教程

### 方式二：源码运行

#### 1. 克隆项目

```bash
git clone https://github.com/YOUR_USERNAME/bilibili-queue-system.git
cd bilibili-queue-system
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置

编辑 `config.json` 文件：

```json
{
  "room_id": 你的直播间ID,
  "credential": {
    "sessdata": "你的SESSDATA",
    "bili_jct": "你的bili_jct",
    "buvid3": "你的buvid3"
  },
  "display_count": 10,
  "commands": {
    "join": "排队",
    "cancel": "取消排队"
  }
}
```

#### 获取B站身份码

1. 登录B站网页版
2. 按F12打开开发者工具
3. 切换到 Application/应用程序 标签
4. 左侧选择 Cookies → https://www.bilibili.com
5. 找到并复制 `SESSDATA`、`bili_jct`、`buvid3` 的值

## 使用方法

### 启动程序

```bash
python main.py
```

程序会启动两个窗口：
- **管理窗口**: 用于管理员操作队列
- **显示窗口**: 半透明窗口，可在OBS中捕获

### 管理操作

- **叫号**: 弹出当前用户信息并从队列移除
- **删除选中**: 删除选中的用户
- **插队**: 手动添加用户到指定位置
- **清空队列**: 清空所有排队用户

### 观众指令

- 发送 `排队` - 加入队列
- 发送 `取消排队` - 退出队列

### 显示窗口操作

- **左键拖动**: 移动窗口位置
- **右键双击**: 关闭窗口

## OBS设置

1. 添加来源 → 窗口捕获
2. 选择"排队显示"窗口
3. 勾选"捕获鼠标光标"（可选）

## 更新

程序启动时会自动检查更新，发现新版本会提示是否更新。

手动检查更新：
```bash
python -c "from auto_updater import AutoUpdater; AutoUpdater().auto_update()"
```

## 发布新版本

### 自动打包（推荐）

1. 修改 `version.json` 中的版本号（如 1.0.0 → 1.1.0）
2. 提交代码并打tag：
   ```bash
   git add .
   git commit -m "Release v1.1.0"
   git tag v1.1.0
   git push origin main --tags
   ```
3. GitHub Actions 会自动编译并创建 Release
4. 用户启动程序时会自动检测并提示更新

### 手动打包

```bash
pip install pyinstaller
pyinstaller build.spec
```

生成的 exe 在 `dist/` 目录下。

## 注意事项

- 身份码请妥善保管，不要泄露
- 队列数据会自动保存到 `queue_data.json`
- 程序更新时会自动备份到 `backup_old_version` 目录

## 许可证

MIT License
