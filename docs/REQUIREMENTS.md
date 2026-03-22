# Dake-Video-Auto 需求文档 (v3.0)

## 1. 项目概述

### 1.1 项目定位
Dake-Video-Auto 是一款面向内容创作者的视频自动化处理工具，专注于**小红书视频下载**、**本地上传**、智能剪辑和多平台适配导出。

### 1.2 目标用户
- 社交媒体运营人员
- 短视频创作者
- 内容搬运/二创团队
- 跨境电商营销人员

### 1.3 核心场景
1. 从小红书下载优质视频素材
2. 本地上传视频进行剪辑处理
3. 批量处理视频（去水印、调色、加字幕、加Logo等）
4. 生成多平台适配格式（抖音/Instagram/YouTube/TikTok）

---

## 2. 功能需求

### 2.1 视频获取模块

#### 2.1.1 小红书视频下载
- **输入**: 小红书视频链接 (`https://www.xiaohongshu.com/explore/xxx`)
- **输出**: 原始视频文件 (MP4格式)
- **存储位置**: `videos/raw/{note_id}.mp4`
- **技术实现**: Playwright 模拟浏览器抓取
- **状态**: ✅ 已上线

#### 2.1.2 本地上传视频 ⭐ 新增
- **输入**: 本地视频文件
- **支持格式**: MP4, MOV, AVI, MKV, WEBM, M4V
- **输出**: 上传后的视频文件
- **存储位置**: `videos/raw/upload_{uuid}.mp4`
- **技术实现**: Flask 文件上传 API
- **文件大小限制**: 建议不超过 500MB
- **状态**: ✅ 已上线

#### 2.1.3 抖音视频下载 (暂停)
- **状态**: ❌ 暂时关闭
- **原因**: 抖音反爬升级，需要 Cookie 登录，配置复杂
- **备注**: 代码保留，未来可通过配置 Cookie 重新启用

#### 2.1.4 视频传输到手机 ⭐ 新增 (v3.1)
- **功能**: 视频剪辑完成后自动生成二维码，手机扫码下载
- **技术实现**: 
  - 后端生成下载二维码 (`core/video_transfer.py`)
  - 使用 `qrcode` 库生成二维码图片
  - 自动获取局域网 IP 地址构建下载链接
- **下载链接格式**: `http://{局域网IP}:5000/api/download/edited/{视频名}`
- **存储位置**: `static/qr_{视频名}.png`
- **使用方式**: 
  1. 剪辑完成后页面自动显示二维码
  2. iPhone 相机扫码
  3. 点击链接直接下载视频
- **状态**: ✅ 已上线

---

### 2.2 视频剪辑模块

#### 2.2.1 基础剪辑功能
| 功能 | 配置项 | 默认值 | 说明 |
|------|--------|--------|------|
| 裁剪首尾 | crop_top, crop_bottom | 0.5s | 自定义去除开头/结尾时长(秒) |
| 播放速度 | speed | 1.05x | 0.8x - 2.0x 可调 |
| 水平镜像 | hflip | true | 水平翻转视频 |
| 智能缩放 | zoom | 1.05 | 轻微放大画面 |

#### 2.2.2 画面调色
| 功能 | 配置项 | 默认值 | 范围 |
|------|--------|--------|------|
| 亮度调整 | brightness | 0.05 | -1.0 ~ 1.0 |
| 对比度调整 | contrast | 0.1 | -1.0 ~ 1.0 |
| 饱和度调整 | saturation | 0.05 | -1.0 ~ 1.0 |

#### 2.2.3 画幅转换
- **输入**: 任意比例视频
- **输出**: 9:16 竖屏 (1080x1920)
- **处理方式**: 智能裁剪 + 黑边填充

---

### 2.3 Logo/水印模块

#### 2.3.1 Logo 叠加
- **支持格式**: PNG (透明背景)
- **上传位置**: `assets/logos/`
- **可调参数**:
  - Logo大小: 5% - 30% (相对于视频宽度)
  - Logo位置: 左上/右上/左下/右下/底部居中
  - Logo透明度: 85% - 100%

#### 2.3.2 Logo 位置详情
| 位置 | X坐标 | Y坐标 | 说明 |
|------|-------|-------|------|
| 左上 (top_left) | 84px | 104px | 距离左边缘84px，上边缘104px |
| 右上 (top_right) | W-w-30 | 30px | 距离右边缘30px |
| 左下 (bottom_left) | 30px | H-h-30 | 距离左/下边缘30px |
| 右下 (bottom_right) | W-w-30 | H-h-30 | 距离右/下边缘30px |
| 底部居中 | (W-w)/2 | H-h-30 | 水平居中 |

#### 2.3.3 BGM 替换
- **支持格式**: MP3, M4A, WAV
- **上传位置**: `assets/bgm/`
- **排序**: 按文件名字母顺序排序 ⭐
- **混音控制**:
  - BGM音量: 0% - 200%
  - 原声音量: 0% - 200%
  - 完全替换模式: 仅用BGM

---

### 2.4 字幕模块

#### 2.4.1 字幕模式
**自定义字幕** (当前支持)
- 手动输入字幕内容
- 自定义显示时间段
- 开始时间: 0-60秒
- 结束时间: 可选，留空表示到视频结尾

#### 2.4.2 字幕样式配置
| 样式名称 | 字体颜色 | 描边颜色 | 用途 |
|---------|---------|---------|------|
| 白字黑边 | #FFFFFF | #000000 | 通用 |
| 黄字黑边 | #FFFF00 | #000000 | 强调 |
| 白字红边 | #FFFFFF | #FF0000 | 警示 |
| 黑字白边 | #000000 | #FFFFFF | 浅色背景 |
| 青字黑边 | #00FFFF | #000000 | 科技感 |
| 粉字黑边 | #FF69B4 | #000000 | 可爱风 |

#### 2.4.3 字幕位置
- 底部 (bottom)
- 中间 (middle)
- 顶部 (top)

#### 2.4.4 字体大小
- **默认值**: 12px
- **范围**: 10px - 72px
- **对齐方式**: 左对齐 / 居中 / 右对齐

---

### 2.5 错误处理与日志

#### 2.5.1 前端错误显示
- 剪辑失败时显示详细错误信息
- 支持查看完整日志（可展开/收起）
- 彩色日志级别区分

#### 2.5.2 后端日志
- 每个剪辑任务生成独立日志文件
- 日志位置: `logs/edit_YYYYMMDD_HHMMSS.log`
- API 接口: `/api/logs/edit/latest`

---

## 3. 技术架构

### 3.1 技术栈
| 层级 | 技术 | 版本 |
|------|------|------|
| 后端框架 | Flask | 2.0+ |
| 视频处理 | FFmpeg | 4.4+ |
| 语音识别 | OpenAI Whisper | 20231117 |
| 浏览器自动化 | Playwright | 1.40+ |
| 视频下载 | yt-dlp | 2026+ (备用) |
| 前端 | HTML5 + CSS3 + JavaScript | - |

### 3.2 项目结构
```
Dake-Video-Auto/
├── app_simple.py              # 单用户主应用 (当前使用)
├── app_multi_user.py          # 多用户主应用 (可选)
├── download_worker.py         # 下载工作进程
├── edit_worker.py             # 剪辑工作进程
├── core/
│   ├── editor_advanced.py     # 视频编辑器 (含字幕)
│   ├── downloader_pw.py       # 小红书下载器
│   ├── douyin_downloader.py   # 抖音下载器 (暂停)
│   ├── douyin_ytdlp.py        # yt-dlp 抖音下载 (暂停)
│   ├── publish_assistant.py   # 发布助手
│   └── video_transfer.py      # 视频传输模块 (二维码生成) ⭐ 新增
├── templates/
│   └── index.html             # 主界面
├── static/                    # 静态资源 (含二维码)
├── videos/
│   └── raw/                   # 原始视频
├── output/                    # 成品视频
├── uploads/                   # 上传文件临时目录
├── assets/
│   ├── logos/                 # Logo文件
│   └── bgm/                   # BGM文件
├── cookies/                   # Cookie 配置目录
├── logs/                      # 日志文件
├── config/                    # 配置文件
└── requirements.txt           # 依赖列表
```

### 3.3 API 接口

#### 获取视频
```http
# 链接下载
POST /api/download
Content-Type: application/json
{
  "url": "https://www.xiaohongshu.com/explore/xxx"
}

# 本地上传
POST /api/upload/video
Content-Type: multipart/form-data
file: [视频文件]
```

#### 剪辑接口
```http
POST /api/edit
Content-Type: application/json
{
  "note_id": "视频ID",
  "config": {
    "crop_top": 0.5,
    "crop_bottom": 0.5,
    "speed": 1.05,
    "hflip": true,
    "zoom": 1.05,
    "brightness": 0.05,
    "contrast": 0.1,
    "saturation": 0.05,
    "add_logo": true,
    "logo_select": "logo.png",
    "logo_position": "top_left",
    "logo_size": 0.12,
    "replace_audio": false,
    "original_volume": 1.0,
    "add_subtitles": false,
    "subtitle_text": "",
    "subtitle_style": "yellow_black"
  }
}
```

#### 资源管理
```http
GET  /api/logos/list          # 获取 Logo 列表
GET  /api/bgm/list            # 获取 BGM 列表（已排序）
POST /api/upload/logo         # 上传 Logo
POST /api/upload/bgm          # 上传 BGM
GET  /api/logs/edit/latest    # 获取最新剪辑日志
GET  /static/qr_{视频名}.png   # 获取下载二维码 ⭐ 新增
```

#### 二维码传输响应
剪辑接口 (`POST /api/edit`) 成功响应新增字段：
```json
{
  "success": true,
  "data": {
    "output_name": "video_xxx.mp4",
    "preview_url": "/api/preview/video_xxx.mp4",
    "download_url": "/api/download/edited/video_xxx.mp4",
    "qr_url": "/static/qr_video_xxx.mp4.png",
    "qr_tip": "iPhone 扫码直接下载"
  }
}
```

---

## 4. 用户界面

### 4.1 操作流程
```
1. 获取视频 (链接下载 或 本地上传)
   ↓
2. 配置剪辑选项 (Logo/BGM/字幕/效果)
   ↓
3. 开始剪辑
   ↓
4. 预览/下载成品
```

### 4.2 界面布局
- **步骤1**: 获取视频
  - 选项卡1: 链接下载 (小红书)
  - 选项卡2: 本地上传 (MP4/MOV/AVI等)
- **步骤2**: 剪辑配置
  - Logo设置 (上传/选择/位置)
  - BGM设置 (上传/选择/音量)
  - 字幕设置 (自定义/样式/位置)
  - 视频效果 (镜像/裁剪/调色)
- **步骤3**: 完成预览

---

## 5. 部署配置

### 5.1 环境要求
- **操作系统**: Linux (Ubuntu 20.04+)
- **Python**: 3.10+
- **内存**: 建议 8GB+
- **磁盘**: 建议 50GB+
- **网络**: 可访问小红书网站

### 5.2 安装步骤
```bash
# 1. 克隆项目
git clone https://github.com/wudake/Dake-Video-Auto.git
cd Dake-Video-Auto

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright
playwright install chromium

# 5. 启动服务
python app_simple.py
```

### 5.3 访问地址
```
http://服务器IP:5000
# 默认: http://172.20.5.151:5000
```

---

## 6. 已知限制与待办

### 6.1 当前版本限制
| 功能 | 状态 | 说明 |
|------|------|------|
| 抖音下载 | ❌ 暂停 | 需要 Cookie，配置复杂 |
| 批量处理 | ⏳ 待开发 | 当前仅支持单视频 |
| 自动字幕识别 | ⏳ 待优化 | Whisper 模型加载慢 |
| 多用户支持 | ⏳ 可选 | 有 app_multi_user.py |

### 6.2 待办事项
- [ ] 恢复抖音下载功能（简化 Cookie 配置流程）
- [ ] 批量视频处理
- [ ] 任务队列管理
- [ ] 用户认证系统
- [ ] 发布到社交平台（TikTok/Instagram/YouTube）

---

## 7. 版本历史

### v3.1 (2026-03-22) ⭐ 最新
- ✅ 新增视频传输功能：自动生成下载二维码
- ✅ iPhone 扫码直接下载剪辑后的视频
- ✅ 新增 `core/video_transfer.py` 传输模块
- ✅ 前端页面显示二维码区域
- ✅ 自动获取局域网 IP 构建下载链接

### v3.0 (2026-03-17)
- ✅ 新增本地上传视频功能
- ✅ BGM 列表按文件名排序
- ✅ Logo 左上角位置调整 (84px, 104px)
- ✅ 前端错误日志显示优化
- ✅ 移除抖音下载（临时关闭）

### v2.2 (2026-03-14)
- ✅ 新增自定义字幕功能
- ✅ 修复字幕开始时间为0的bug
- ✅ 完善前后端参数传递

### v2.1 (2026-03-13)
- ✅ 多用户支持
- ✅ 任务队列管理
- ✅ 实时进度显示

### v2.0 (2026-03-12)
- ✅ 字幕自动识别 (Whisper)
- ✅ 6种字幕样式
- ✅ 自定义裁剪时间

### v1.0 (2026-03-10)
- ✅ 小红书视频下载
- ✅ 基础视频剪辑
- ✅ Logo/BGM 叠加

---

## 8. 项目信息

**项目路径**: `/home/dake/Dake-Video-Auto/`
**维护者**: Dake & Zhushou
**创建时间**: 2026-03-10
**最后更新**: 2026-03-22
**版本**: v3.1

---

## 9. 联系方式

如有问题或建议，请联系项目维护者。
