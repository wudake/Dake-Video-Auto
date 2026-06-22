# 视频封面功能设计文档

## 1. 需求概述

给最终生成的视频开头插入一张用户自行制作的封面图片，封面持续时长可配置，默认 0.5 秒。

## 2. 设计决策

| 决策项 | 选择 | 说明 |
|--------|------|------|
| 封面上传方式 | 每次剪辑单独上传 | 不保留在素材库，用完即删 |
| 封面时长 | 可配置，默认 0.5 秒 | 用户可在剪辑界面输入 |
| 封面适配 | 缩放并裁剪填充 | 保持比例，填满 1080×1920 |
| 封面期间音频 | 直接播放主视频音频 | BGM/原声从 0 秒开始 |
| 字幕时间 | 整体后移 cover_duration | 字幕出现在封面结束之后 |
| 实现方案 | 后处理插入封面 | 主视频渲染完成后再拼接封面，逻辑清晰 |

## 3. 整体流程

```
用户上传封面 ──► /api/upload/cover ──► 保存到 uploads/covers/
                                    │
                                    ▼
用户提交剪辑配置 ──► .temp_config.json（包含 cover_path, cover_duration）
                                    │
                                    ▼
                         edit_worker.py 读取配置
                                    │
                                    ▼
                         editor_advanced.edit_video()
                                    │
                 ┌──────────────────┼──────────────────┐
                 ▼                  ▼                  ▼
            生成主视频         烧录字幕（时间后移）    插入封面
                 │                  │                  │
                 └──────────────────┴──────────────────┘
                                    │
                                    ▼
                           清理临时封面文件
                                    │
                                    ▼
                           返回最终视频路径
```

## 4. 配置参数

在 `edit_video()` 的 `config` 中新增：

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `add_cover` | bool | false | 是否启用封面 |
| `cover_path` | str | "" | 封面图片在服务器的绝对路径 |
| `cover_duration` | float | 0.5 | 封面持续秒数 |

## 5. API 接口

### 5.1 上传封面

```http
POST /api/upload/cover
Content-Type: multipart/form-data
file: [PNG/JPG 图片]
```

响应：

```json
{
  "success": true,
  "data": {
    "filename": "cover_202606221800_abc123.jpg",
    "path": "/home/dake/Dake-Video-Auto/uploads/covers/cover_202606221800_abc123.jpg"
  }
}
```

限制：仅接受 `.png`、`.jpg`、`.jpeg`。

## 6. UI 调整

在剪辑配置面板的"字幕设置"附近新增"封面设置"区域：

- 开关：添加封面
- 文件上传：选择封面图片
- 数字输入：封面时长（秒），默认 0.5，范围 0.1 - 5.0

## 7. FFmpeg 实现细节

### 7.1 生成封面视频片段

输入：`cover.jpg`（任意尺寸）
输出：`cover_clip.mp4`（1080×1920，0.5 秒，无声）

```bash
ffmpeg -y -loop 1 -i cover.jpg -vf "
  scale=1080:1920:force_original_aspect_ratio=increase,
  crop=1080:1920,
  format=yuv420p,
  trim=duration=0.5
" -t 0.5 -an cover_clip.mp4
```

### 7.2 拼接封面与主视频

假设：
- `cover_clip.mp4`：无声封面片段
- `main.mp4`：主视频（含音频）
- 输出：`final.mp4`

```bash
ffmpeg -y -i cover_clip.mp4 -i main.mp4 -filter_complex "
  [0:v]format=yuv420p[v0];
  [1:v]format=yuv420p[v1];
  [v0][v1]concat=n=2:v=1:a=0[video];
  [1:a]aformat=fltp:48000:stereo[audio]
" -map "[video]" -map "[audio]" -c:v libx264 -c:a aac final.mp4
```

### 7.3 字幕时间偏移

若启用封面，则所有字幕条目起始/结束时间均增加 `cover_duration`：

```python
new_start = old_start + cover_duration
new_end = old_end + cover_duration
```

适用于：
- 手动输入字幕
- TTS 同步生成的字幕

## 8. 代码改动点

### 8.1 `app_simple.py`

- 新增 `/api/upload/cover` 路由

### 8.2 `core/editor_advanced.py`

- `edit_video()`：读取 `add_cover`、`cover_path`、`cover_duration`
- 新增 `insert_cover(main_video_path, cover_path, cover_duration, output_path)` 方法
- 新增 `shift_srt_timestamps(srt_path, offset_seconds)` 方法
- 在字幕生成前调用时间偏移
- 在主视频渲染完成后调用封面插入

### 8.3 `templates/index.html`

- 新增封面设置 UI
- 将封面路径和时长加入 `config` 对象后提交到 `/api/edit`

## 9. 异常处理

| 场景 | 处理方式 |
|------|----------|
| 封面文件不存在 | 跳过封面，仅输出主视频 |
| 封面时长超过主视频时长 | 自动截断为 `min(cover_duration, main_duration)` |
| 封面上传格式错误 | 返回 `success: false` 并提示仅支持 PNG/JPG |
| 封面 ffmpeg 处理失败 | 记录日志，回退到无封面版本 |
| 字幕 SRT 解析失败 | 保持原时间，记录警告 |

## 10. 清理策略

剪辑完成后，删除 `uploads/covers/` 下本次使用的封面文件（按文件名匹配），避免堆积。

## 11. 测试要点

1. 上传 PNG/JPG 封面成功并返回路径
2. 启用封面后最终视频第一帧为封面图
3. 封面时长可配置（0.5s、1s、2s）
4. 字幕在封面结束后出现
5. 音频从 0 秒开始播放
6. 不启用封面时行为与原来一致
7. 封面文件不存在时正常回退
8. 竖版/横版封面图均能正确裁剪填充为 1080×1920
