"""
TTS 语音生成模块 - 基于 edge-tts (免费微软语音)
支持多音色、语速调节
"""
import asyncio
import edge_tts
from pathlib import Path
import json


class TTSGenerator:
    """TTS 语音生成器"""
    
    # 可用音色列表
    VOICES = {
        # 中文女声
        "zh-CN-XiaoxiaoNeural": {"name": "晓晓", "gender": "女声", "desc": "活泼自然"},
        "zh-CN-XiaoyiNeural": {"name": "晓伊", "gender": "女声", "desc": "温柔甜美"},
        "zh-CN-liaoning-XiaobeiNeural": {"name": "晓北", "gender": "女声", "desc": "东北口音"},
        "zh-CN-shaanxi-XiaoniNeural": {"name": "晓妮", "gender": "女声", "desc": "陕西口音"},
        # 中文男声
        "zh-CN-YunjianNeural": {"name": "云健", "gender": "男声", "desc": "新闻播报"},
        "zh-CN-YunxiNeural": {"name": "云希", "gender": "男声", "desc": "年轻活力"},
        "zh-CN-YunxiaNeural": {"name": "云霞", "gender": "男声", "desc": "童声"},
        "zh-CN-YunyangNeural": {"name": "云扬", "gender": "男声", "desc": "成熟稳重"},
        # 英文 - 美式英语 (en-US)
        "en-US-AnaNeural": {"name": "Ana", "gender": "女声", "desc": "美式英语 - 年轻活泼"},
        "en-US-AriaNeural": {"name": "Aria", "gender": "女声", "desc": "美式英语 - 专业自信"},
        "en-US-AvaNeural": {"name": "Ava", "gender": "女声", "desc": "美式英语 - 自然优雅"},
        "en-US-AvaMultilingualNeural": {"name": "Ava(多语言)", "gender": "女声", "desc": "美式英语 - 多语言"},
        "en-US-EmmaNeural": {"name": "Emma", "gender": "女声", "desc": "美式英语 - 温暖友好"},
        "en-US-EmmaMultilingualNeural": {"name": "Emma(多语言)", "gender": "女声", "desc": "美式英语 - 多语言"},
        "en-US-JennyNeural": {"name": "Jenny", "gender": "女声", "desc": "美式英语 - 清晰友好"},
        "en-US-MichelleNeural": {"name": "Michelle", "gender": "女声", "desc": "美式英语 - 温暖亲切"},
        "en-US-AndrewNeural": {"name": "Andrew", "gender": "男声", "desc": "美式英语 - 稳重专业"},
        "en-US-AndrewMultilingualNeural": {"name": "Andrew(多语言)", "gender": "男声", "desc": "美式英语 - 多语言"},
        "en-US-BrianNeural": {"name": "Brian", "gender": "男声", "desc": "美式英语 - 清晰有力"},
        "en-US-BrianMultilingualNeural": {"name": "Brian(多语言)", "gender": "男声", "desc": "美式英语 - 多语言"},
        "en-US-ChristopherNeural": {"name": "Christopher", "gender": "男声", "desc": "美式英语 - 权威自信"},
        "en-US-EricNeural": {"name": "Eric", "gender": "男声", "desc": "美式英语 - 年轻活力"},
        "en-US-GuyNeural": {"name": "Guy", "gender": "男声", "desc": "美式英语 - 专业稳重"},
        "en-US-RogerNeural": {"name": "Roger", "gender": "男声", "desc": "美式英语 - 成熟深沉"},
        "en-US-SteffanNeural": {"name": "Steffan", "gender": "男声", "desc": "美式英语 - 温暖可靠"},
        # 英式英语
        "en-GB-LibbyNeural": {"name": "Libby", "gender": "女声", "desc": "英式英语 - 优雅专业"},
        "en-GB-MaisieNeural": {"name": "Maisie", "gender": "女声", "desc": "英式英语 - 活泼年轻"},
        "en-GB-SoniaNeural": {"name": "Sonia", "gender": "女声", "desc": "英式英语 - 友好清晰"},
        "en-GB-RyanNeural": {"name": "Ryan", "gender": "男声", "desc": "英式英语 - 稳重自然"},
        "en-GB-ThomasNeural": {"name": "Thomas", "gender": "男声", "desc": "英式英语 - 成熟稳重"},
        # 日语
        "ja-JP-KeitaNeural": {"name": "Keita", "gender": "男声", "desc": "日语"},
        "ja-JP-NanamiNeural": {"name": "七海", "gender": "女声", "desc": "日语"},
        # 韩语
        "ko-KR-HyunsuMultilingualNeural": {"name": "贤秀(多语言)", "gender": "男声", "desc": "韩语 - 多语言"},
        "ko-KR-InJoonNeural": {"name": "仁俊", "gender": "男声", "desc": "韩语"},
        "ko-KR-SunHiNeural": {"name": "善熙", "gender": "女声", "desc": "韩语"},
    }
    
    def __init__(self, output_dir="assets/tts"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    async def generate_async(self, text, output_path, voice="zh-CN-XiaoxiaoNeural", 
                             rate="+0%", volume="+0%", pitch="+0Hz"):
        """
        异步生成语音
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            voice: 音色ID
            rate: 语速调节 (+50% 加快50%, -20% 减慢20%)
            volume: 音量调节
            pitch: 音调调节
        
        Returns:
            输出文件路径
        """
        import edge_tts.exceptions
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 验证文本
        if not text or not text.strip():
            raise ValueError("文本内容不能为空")
        
        # 清理文本（移除可能导致问题的字符）
        text = text.strip()
        
        try:
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=rate,
                volume=volume,
                pitch=pitch
            )
            
            await communicate.save(str(output_path))
            
            # 验证文件是否成功生成
            if not output_path.exists():
                raise RuntimeError("语音文件未生成")
            if output_path.stat().st_size == 0:
                output_path.unlink()
                raise RuntimeError("语音文件为空")
            
            return str(output_path)
            
        except edge_tts.exceptions.NoAudioReceived:
            raise RuntimeError("微软TTS服务未返回音频，请检查音色是否有效或稍后重试")
        except edge_tts.exceptions.VoiceNotFound:
            raise ValueError(f"音色 '{voice}' 不存在，请使用有效的音色ID")
        except Exception as e:
            # 如果文件已生成但可能损坏，删除它
            if output_path.exists():
                try:
                    output_path.unlink()
                except:
                    pass
            raise
    
    def generate(self, text, output_path=None, voice="zh-CN-XiaoxiaoNeural",
                 rate="+0%", volume="+0%", pitch="+0Hz"):
        """
        同步生成语音（阻塞方式）
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径，None则自动生成
            voice: 音色ID
            rate: 语速调节
            volume: 音量调节
            pitch: 音调调节
        
        Returns:
            输出文件路径
        """
        if output_path is None:
            import hashlib
            import time
            # 生成唯一文件名
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            output_path = self.output_dir / f"tts_{voice.split('-')[-1]}_{timestamp}_{text_hash}.mp3"
        
        try:
            return asyncio.run(self.generate_async(text, output_path, voice, rate, volume, pitch))
        except RuntimeError as e:
            # 如果在已有事件循环中运行，尝试直接使用事件循环
            if "cannot be called from a running event loop" in str(e):
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 使用 run_coroutine_threadsafe 或 nest_asyncio
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            asyncio.run, 
                            self.generate_async(text, output_path, voice, rate, volume, pitch)
                        )
                        return future.result()
            raise
            import time
            # 生成唯一文件名
            text_hash = hashlib.md5(text.encode()).hexdigest()[:8]
            timestamp = int(time.time())
            output_path = self.output_dir / f"tts_{voice.split('-')[-1]}_{timestamp}_{text_hash}.mp3"
        
        return asyncio.run(self.generate_async(text, output_path, voice, rate, volume, pitch))
    
    def generate_with_speed(self, text, output_path=None, voice="zh-CN-XiaoxiaoNeural", 
                           speed=1.0):
        """
        使用速度倍数生成语音
        
        Args:
            text: 要转换的文本
            output_path: 输出文件路径
            voice: 音色ID
            speed: 速度倍数 (0.5-2.0)
        
        Returns:
            输出文件路径
        """
        # 转换速度倍数为 edge-tts 的 rate 格式
        if speed > 1.0:
            rate = f"+{int((speed - 1) * 100)}%"
        elif speed < 1.0:
            rate = f"-{int((1 - speed) * 100)}%"
        else:
            rate = "+0%"
        
        return self.generate(text, output_path, voice, rate)
    
    def get_voices_list(self):
        """获取可用音色列表"""
        return [
            {
                "id": voice_id,
                "name": info["name"],
                "gender": info["gender"],
                "desc": info["desc"]
            }
            for voice_id, info in self.VOICES.items()
        ]
    
    def get_voice_by_name(self, name):
        """根据名称查找音色ID"""
        for voice_id, info in self.VOICES.items():
            if info["name"] == name:
                return voice_id
        return "zh-CN-XiaoxiaoNeural"  # 默认


class ScriptToSpeech:
    """脚本转语音 - 支持多段落生成"""
    
    def __init__(self, tts_generator=None):
        self.tts = tts_generator or TTSGenerator()
    
    def generate_multi_segments(self, segments, output_path=None):
        """
        生成多段落语音并合并
        
        Args:
            segments: 段落列表，每个段落是字典 {"text": "...", "voice": "...", "speed": 1.0}
            output_path: 最终输出路径
        
        Returns:
            输出文件路径
        """
        import tempfile
        import subprocess
        import os
        
        if output_path is None:
            import time
            output_path = self.tts.output_dir / f"script_{int(time.time())}.mp3"
        else:
            output_path = Path(output_path)
        
        # 生成每个段落的语音
        temp_files = []
        try:
            for i, seg in enumerate(segments):
                text = seg.get("text", "").strip()
                if not text:
                    continue
                
                voice = seg.get("voice", "zh-CN-XiaoxiaoNeural")
                speed = seg.get("speed", 1.0)
                
                temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
                temp_file.close()
                
                self.tts.generate_with_speed(text, temp_file.name, voice, speed)
                temp_files.append(temp_file.name)
            
            if not temp_files:
                return None
            
            # 使用 FFmpeg 合并音频
            if len(temp_files) == 1:
                # 只有一个文件，直接复制
                import shutil
                shutil.copy(temp_files[0], output_path)
            else:
                # 多个文件，合并
                concat_file = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
                for f in temp_files:
                    concat_file.write(f"file '{f}'\n")
                concat_file.close()
                
                cmd = [
                    "ffmpeg", "-y",
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_file.name,
                    "-c", "copy",
                    str(output_path)
                ]
                
                subprocess.run(cmd, capture_output=True, check=True)
                os.unlink(concat_file.name)
            
            return str(output_path)
            
        finally:
            # 清理临时文件
            for f in temp_files:
                try:
                    os.unlink(f)
                except:
                    pass
    
    def estimate_duration(self, text, speed=1.0):
        """
        估算语音时长（粗略估计）
        
        Args:
            text: 文本内容
            speed: 语速倍数
        
        Returns:
            估计的时长（秒）
        """
        # 中文：每分钟约200-250字
        # 英文：每分钟约130-150词
        
        import re
        
        # 统计中文字符
        chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
        # 统计英文单词
        english_words = len(re.findall(r'[a-zA-Z]+', text))
        
        # 计算时长（秒）
        chinese_duration = chinese_chars / 4  # 约4字/秒
        english_duration = english_words / 2.2  # 约2.2词/秒
        
        total_duration = (chinese_duration + english_duration) / speed
        
        return round(total_duration, 1)


# 快捷函数
def generate_speech(text, output_path=None, voice="晓晓", speed=1.0):
    """
    快速生成语音
    
    示例:
        generate_speech("大家好，今天我来介绍...", "output.mp3", "晓晓", 1.2)
    """
    tts = TTSGenerator()
    voice_id = tts.get_voice_by_name(voice)
    return tts.generate_with_speed(text, output_path, voice_id, speed)


if __name__ == "__main__":
    # 测试
    print("🎙️ 测试 TTS 生成...")
    
    tts = TTSGenerator()
    
    # 列出可用音色
    print("\n可用音色：")
    for v in tts.get_voices_list()[:5]:
        print(f"  - {v['name']} ({v['gender']}): {v['desc']}")
    
    # 生成测试语音
    test_text = "大家好，我是Dake的AI助手，很高兴为大家服务！"
    output = tts.generate_with_speed(test_text, voice="zh-CN-XiaoxiaoNeural", speed=1.0)
    print(f"\n✅ 测试语音生成: {output}")
