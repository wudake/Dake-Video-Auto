# Dake-Video-Auto - 视频处理工具

一款面向内容创作者的自动化视频处理工具，支持**小红书视频下载**、**本地上传**、智能剪辑和多平台适配导出。

## 功能特性

### 视频获取
- ✅ **小红书视频下载** - 使用 Playwright 模拟浏览器抓取
- ✅ **本地上传视频** - 支持 MP4, MOV, AVI, MKV, WEBM, M4V 格式
- ⏸️ **抖音视频下载** - 暂时关闭（需配置 Cookie）

### 智能剪辑
- ✅ **Logo 水印叠加** - 5种位置可选，支持透明度调节
- ✅ **BGM 替换** - 支持 MP3/M4A/WAV，可混音或完全替换
- ✅ **水平镜像翻转** - 一键去重处理
- ✅ **调速** - 0.8x - 2.0x 可调
- ✅ **调色** - 亮度/对比度/饱和度调节
- ✅ **字幕添加** - 自定义字幕内容、样式、位置
- ✅ **9:16 竖屏比例** - 自动适配抖音/Instagram/TikTok

### Web 界面
- ✅ 现代化深色主题界面
- ✅ 分步骤操作流程
- ✅ 实时错误日志显示
- ✅ 视频预览和下载

## 技术栈

| 组件 | 技术 |
|------|------|
| 后端 | Python + Flask |
| 视频处理 | FFmpeg |
| 浏览器自动化 | Playwright |
| 视频下载 | yt-dlp (备用) |
| 前端 | HTML5 + CSS3 + JavaScript |

## 快速开始

### 安装

```bash
# 克隆项目
git clone https://github.com/wudake/Dake-Video-Auto.git
cd Dake-Video-Auto

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

### 启动服务

```bash
# 启动 Web 服务
python app_simple.py

# 访问 http://localhost:5000
# 或 http://服务器IP:5000
```

## 使用指南

### 方式1：小红书链接下载

1. 打开 Web 界面
2. 在"链接下载"选项卡中粘贴小红书视频链接
3. 点击"开始下载"
4. 等待下载完成后自动跳转到剪辑配置

### 方式2：本地上传视频

1. 切换到"本地上传"选项卡
2. 点击上传区域选择本地视频文件
3. 支持格式：MP4, MOV, AVI, MKV, WEBM, M4V
4. 上传成功后自动跳转到剪辑配置

### 视频剪辑配置

**Logo 设置**
- 上传 Logo 文件 (PNG 格式，透明背景最佳)
- 选择 Logo 位置：左上/右上/左下/右下/底部居中
- 调节 Logo 大小 (5% - 30%)

**BGM 设置**
- 上传 BGM 文件 (MP3/M4A/WAV)
- BGM 列表按文件名自动排序
- 调节原声/BGM 音量
- 可选"使用 BGM 替换原声"

**字幕设置**
- 勾选"添加字幕"
- 输入字幕内容
- 设置显示时间段
- 选择样式和位置

**视频效果**
- 水平镜像：一键去重
- 裁剪首尾：去除开头/结尾片段
- 播放速度：0.8x - 2.0x
- 调色优化：亮度/对比度/饱和度

## 目录结构

```
Dake-Video-Auto/
├── app_simple.py              # Flask 主应用
├── download_worker.py         # 下载工作进程
├── edit_worker.py             # 剪辑工作进程
├── core/
│   ├── editor_advanced.py     # 视频编辑器
│   ├── downloader_pw.py       # 小红书下载器
│   ├── douyin_downloader.py   # 抖音下载器 (暂停)
│   └── publish_assistant.py   # 发布助手
├── templates/
│   └── index.html             # Web 界面
├── videos/raw/                # 原始视频
├── output/                    # 剪辑后视频
├── assets/
│   ├── logos/                 # Logo 文件
│   └── bgm/                   # BGM 文件
├── logs/                      # 日志文件
└── docs/                      # 文档
```

## 配置说明

### 视频剪辑默认参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 裁剪首尾 | 0.5秒 | 去除开头/结尾 |
| 播放速度 | 1.05x | 轻微加速 |
| Logo 大小 | 12% | 相对视频宽度 |
| 输出比例 | 9:16 | 1080x1920 |

### Logo 位置详情

| 位置 | 距离左边缘 | 距离上边缘 | 距离右边缘 | 距离下边缘 |
|------|-----------|-----------|-----------|-----------|
| 左上 | 84px | 104px | - | - |
| 右上 | - | 30px | 30px | - |
| 左下 | 30px | - | - | 30px |
| 右下 | - | - | 30px | 30px |
| 底部居中 | - | - | - | 30px |

### 自定义配置

编辑 `core/editor_advanced.py` 中的配置：
- `PRESETS` - 剪辑预设
- `SUBTITLE_STYLES` - 字幕样式

## API 接口

### 获取视频

```bash
# 链接下载
POST /api/download
{"url": "https://www.xiaohongshu.com/explore/xxx"}

# 本地上传
POST /api/upload/video
Content-Type: multipart/form-data
file: [视频文件]
```

### 剪辑视频

```bash
POST /api/edit
{
  "note_id": "视频ID",
  "config": {
    "crop_top": 0.5,
    "speed": 1.05,
    "hflip": true,
    "add_logo": true,
    "logo_position": "top_left",
    ...
  }
}
```

### 资源管理

```bash
GET  /api/logos/list           # Logo 列表
GET  /api/bgm/list             # BGM 列表（已排序）
POST /api/upload/logo          # 上传 Logo
POST /api/upload/bgm           # 上传 BGM
GET  /api/logs/edit/latest     # 剪辑日志
```

## 注意事项

1. **小红书链接有时效性**，请使用最新分享的链接
2. **视频剪辑需要 FFmpeg**，请确保已安装
3. **本地上传视频大小**，建议不超过 500MB
4. **抖音下载已暂停**，如需使用需配置 Cookie（见 `cookies/README.md`）
5. **建议仅用于个人学习和合法用途**

## 常见问题

### Q: 剪辑时报错"网络错误"？
A: 可能是服务已停止，请检查服务状态或重启服务。

### Q: 小红书下载失败？
A: 链接可能已过期，请重新从 App 复制分享链接。

### Q: 本地上传后找不到文件？
A: 检查 `videos/raw/` 目录，上传的文件会保存在这里。

### Q: Logo 位置如何调整？
A: 编辑 `core/editor_advanced.py` 中的 `pos_map` 配置。

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|---------|
| v3.0 | 2026-03-17 | 新增本地上传、BGM排序、优化Logo位置、移除抖音下载 |
| v2.2 | 2026-03-14 | 自定义字幕、错误日志显示 |
| v2.1 | 2026-03-13 | 多用户支持、任务队列 |
| v2.0 | 2026-03-12 | Whisper字幕识别 |
| v1.0 | 2026-03-10 | 基础功能 |

## 详细文档

- [需求文档](docs/REQUIREMENTS.md) - 详细功能需求
- [部署文档](DEPLOY.md) - 部署配置说明
- [多用户方案](docs/3_USERS_PLAN.md) - 3人团队使用方案
- [Cookie配置](cookies/README.md) - 抖音Cookie配置（暂停）

## License

MIT

## 项目信息

**项目路径**: `/home/dake/Dake-Video-Auto/`
**维护者**: Dake & Zhushou
**创建时间**: 2026-03-10
**最后更新**: 2026-03-17
