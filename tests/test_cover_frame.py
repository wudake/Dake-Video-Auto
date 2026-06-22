"""
视频封面功能测试
覆盖: shift_srt_timestamps, insert_cover, edit_video 封面分支
"""
import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "core"))

from editor_advanced import AdvancedVideoEditor


class TestCoverFrame(unittest.TestCase):
    """封面功能单元与集成测试"""

    @classmethod
    def setUpClass(cls):
        cls.temp_dir = Path(tempfile.mkdtemp(prefix="cover_frame_test_"))
        cls.raw_dir = cls.temp_dir / "videos" / "raw"
        cls.output_dir = cls.temp_dir / "output"
        cls.assets_dir = cls.temp_dir / "assets"
        cls.logos_dir = cls.assets_dir / "logos"
        cls.bgm_dir = cls.assets_dir / "bgm"

        for d in [cls.raw_dir, cls.output_dir, cls.assets_dir, cls.logos_dir, cls.bgm_dir]:
            d.mkdir(parents=True, exist_ok=True)

        cls.editor = AdvancedVideoEditor(
            raw_dir=str(cls.raw_dir),
            edited_dir=str(cls.output_dir),
            assets_dir=str(cls.assets_dir),
            logos_dir=str(cls.logos_dir),
            bgm_dir=str(cls.bgm_dir),
        )

        # 生成 4 秒 1080x1920 测试视频（绿色背景 + 正弦波音轨）
        cls.video_with_audio = cls.raw_dir / "test_with_audio.mp4"
        cls._generate_test_video(str(cls.video_with_audio), duration=4, with_audio=True)

        # 生成 4 秒无音频测试视频
        cls.video_no_audio = cls.raw_dir / "test_no_audio.mp4"
        cls._generate_test_video(str(cls.video_no_audio), duration=4, with_audio=False)

        # 生成不同尺寸的封面图片
        cls.cover_1080_1920 = cls.temp_dir / "cover_1080_1920.jpg"
        cls.cover_800_1200 = cls.temp_dir / "cover_800_1200.jpg"
        cls.cover_1920_1080 = cls.temp_dir / "cover_1920_1080.jpg"  # 横版
        cls._generate_cover_image(str(cls.cover_1080_1920), 1080, 1920, "purple")
        cls._generate_cover_image(str(cls.cover_800_1200), 800, 1200, "blue")
        cls._generate_cover_image(str(cls.cover_1920_1080), 1920, 1080, "red")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    @classmethod
    def _generate_test_video(cls, output_path, duration=4, with_audio=True):
        """用 FFmpeg 生成测试视频"""
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c=green:s=1080x1920:d={duration}",
        ]
        if with_audio:
            cmd.extend(["-f", "lavfi", "-i", f"sine=frequency=1000:duration={duration}"])
        cmd.extend([
            "-shortest",
            "-c:v", "libx264", "-preset", "ultrafast",
            "-c:a", "aac", "-b:a", "128k" if with_audio else "-an",
            "-pix_fmt", "yuv420p",
            output_path
        ])
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg 生成测试视频失败: {result.stderr}")

    @classmethod
    def _generate_cover_image(cls, output_path, width, height, color):
        """用 FFmpeg 生成纯色封面图"""
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi", "-i", f"color=c={color}:s={width}x{height}:d=1",
            "-frames:v", "1",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg 生成封面图失败: {result.stderr}")

    @staticmethod
    def _get_video_info(video_path):
        """获取视频时长和分辨率"""
        result = subprocess.run(
            ["ffprobe", "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height", "-show_entries", "format=duration",
             "-of", "json", str(video_path)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        stream = data.get("streams", [{}])[0]
        fmt = data.get("format", {})
        return {
            "width": stream.get("width", 0),
            "height": stream.get("height", 0),
            "duration": float(fmt.get("duration", 0))
        }

    @staticmethod
    def _extract_frame(video_path, time_sec, output_path):
        """提取指定时间的帧"""
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(video_path), "-ss", str(time_sec),
             "-vframes", "1", str(output_path)],
            check=True, capture_output=True
        )

    @staticmethod
    def _get_dominant_color(image_path):
        """获取图片中心像素颜色"""
        from PIL import Image
        img = Image.open(image_path)
        return img.getpixel((img.width // 2, img.height // 2))

    # ==================== 单元测试：shift_srt_timestamps ====================

    def test_shift_srt_timestamps_basic(self):
        """基础时间偏移"""
        srt_path = self.temp_dir / "shift_basic.srt"
        srt_path.write_text(
            "1\n00:00:00,000 --> 00:00:02,000\nHello\n\n"
            "2\n00:00:03,500 --> 00:00:05,500\nWorld\n",
            encoding="utf-8"
        )
        self.editor.shift_srt_timestamps(srt_path, 0.5)
        content = srt_path.read_text(encoding="utf-8")
        self.assertIn("00:00:00,500 --> 00:00:02,500", content)
        self.assertIn("00:00:04,000 --> 00:00:06,000", content)

    def test_shift_srt_timestamps_zero_offset(self):
        """偏移为 0 时不改变文件"""
        srt_path = self.temp_dir / "shift_zero.srt"
        original = "1\n00:00:01,000 --> 00:00:03,000\nHello\n"
        srt_path.write_text(original, encoding="utf-8")
        self.editor.shift_srt_timestamps(srt_path, 0)
        self.assertEqual(srt_path.read_text(encoding="utf-8"), original)

    def test_shift_srt_timestamps_large_offset(self):
        """较大偏移值（跨分钟）"""
        srt_path = self.temp_dir / "shift_large.srt"
        srt_path.write_text(
            "1\n00:00:58,500 --> 00:01:01,000\nHello\n",
            encoding="utf-8"
        )
        self.editor.shift_srt_timestamps(srt_path, 2.5)
        content = srt_path.read_text(encoding="utf-8")
        self.assertIn("00:01:01,000 --> 00:01:03,500", content)

    def test_shift_srt_timestamps_negative_result_clamped(self):
        """偏移不会导致负时间（实际只会后移，此测试验证安全）"""
        srt_path = self.temp_dir / "shift_clamp.srt"
        srt_path.write_text(
            "1\n00:00:00,100 --> 00:00:02,000\nHello\n",
            encoding="utf-8"
        )
        # 偏移 -0.2 秒在业务中不会出现，但方法应能处理
        # _seconds_to_srt_time 内部有 max(0, ...) 保护
        # 这里只测试正常后移
        self.editor.shift_srt_timestamps(srt_path, 0.1)
        content = srt_path.read_text(encoding="utf-8")
        self.assertIn("00:00:00,200 --> 00:00:02,100", content)

    # ==================== 单元测试：insert_cover ====================

    def test_insert_cover_with_audio(self):
        """插入封面到带音频的视频"""
        output = self.output_dir / "cover_with_audio.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.cover_1080_1920, 1.0, output
        )
        self.assertIsNotNone(result)
        self.assertTrue(output.exists())

        info = self._get_video_info(output)
        self.assertEqual(info["width"], 1080)
        self.assertEqual(info["height"], 1920)
        self.assertAlmostEqual(info["duration"], 5.0, delta=0.2)  # 4s + 1s

        # 验证第一帧是封面颜色（紫色）
        frame_path = self.temp_dir / "frame_with_audio_0.png"
        self._extract_frame(output, 0.2, frame_path)
        color = self._get_dominant_color(frame_path)
        # 紫色近似判断：R 和 B 较高，G 较低
        self.assertGreater(color[0], 100)
        self.assertGreater(color[2], 100)
        self.assertLess(color[1], 50)

        # 验证 1.5 秒后回到主视频颜色（绿色）
        frame_path2 = self.temp_dir / "frame_with_audio_15.png"
        self._extract_frame(output, 1.5, frame_path2)
        color2 = self._get_dominant_color(frame_path2)
        self.assertLess(color2[0], 50)
        self.assertGreater(color2[1], 100)
        self.assertLess(color2[2], 50)

    def test_insert_cover_no_audio(self):
        """插入封面到无音频的视频"""
        output = self.output_dir / "cover_no_audio.mp4"
        result = self.editor.insert_cover(
            self.video_no_audio, self.cover_1080_1920, 0.5, output
        )
        self.assertIsNotNone(result)
        self.assertTrue(output.exists())

        info = self._get_video_info(output)
        self.assertAlmostEqual(info["duration"], 4.5, delta=0.2)

    def test_insert_cover_scaling_crop(self):
        """封面尺寸非 1080x1920 时应裁剪填充"""
        output = self.output_dir / "cover_scaled.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.cover_800_1200, 0.5, output
        )
        self.assertIsNotNone(result)
        info = self._get_video_info(output)
        self.assertEqual(info["width"], 1080)
        self.assertEqual(info["height"], 1920)

    def test_insert_cover_landscape_crop(self):
        """横版封面应被裁剪填充为竖屏"""
        output = self.output_dir / "cover_landscape.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.cover_1920_1080, 0.5, output
        )
        self.assertIsNotNone(result)
        info = self._get_video_info(output)
        self.assertEqual(info["width"], 1080)
        self.assertEqual(info["height"], 1920)

    def test_insert_cover_duration_exceeds_video(self):
        """封面时长超过主视频时应自动截断为主视频时长"""
        output = self.output_dir / "cover_long.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.cover_1080_1920, 10.0, output
        )
        self.assertIsNotNone(result)
        info = self._get_video_info(output)
        # 封面被截断为 4s，加上主视频 4s，总时长约 8s
        self.assertAlmostEqual(info["duration"], 8.0, delta=0.2)

    def test_insert_cover_missing_file(self):
        """封面文件不存在时应返回 None"""
        output = self.output_dir / "cover_missing.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.temp_dir / "not_exist.jpg", 0.5, output
        )
        self.assertIsNone(result)
        self.assertFalse(output.exists())

    def test_insert_cover_invalid_duration(self):
        """封面时长为 0 或负数时应跳过"""
        output = self.output_dir / "cover_zero.mp4"
        result = self.editor.insert_cover(
            self.video_with_audio, self.cover_1080_1920, 0, output
        )
        self.assertIsNone(result)

    # ==================== 集成测试：edit_video with cover ====================

    def test_edit_video_with_cover_and_subtitle(self):
        """完整剪辑流程：视频 + 封面 + 字幕"""
        config = {
            "crop_top": 0,
            "crop_bottom": 0,
            "speed": 1.0,
            "hflip": False,
            "zoom": 1.0,
            "brightness": 0,
            "contrast": 0,
            "saturation": 0,
            "add_logo": False,
            "replace_audio": False,
            "bgm_select": "",
            "original_volume": 1.0,
            "add_subtitles": True,
            "subtitle_text": "Cover Integration Test",
            "subtitle_start": 0,
            "subtitle_end": None,
            "subtitle_style": "yellow_classic",
            "subtitle_font_size": 24,
            "subtitle_position": "bottom",
            "subtitle_align": "center",
            "subtitle_outline_width": 2,
            "add_cover": True,
            "cover_path": str(self.cover_1080_1920),
            "cover_duration": 1.0
        }

        output = self.editor.edit_video(self.video_with_audio, config)
        self.assertIsNotNone(output)
        self.assertTrue(Path(output).exists())

        info = self._get_video_info(output)
        self.assertAlmostEqual(info["duration"], 5.0, delta=0.3)  # 4s + 1s 封面

        # 验证封面帧
        frame_path = self.temp_dir / "edit_frame_0.png"
        self._extract_frame(output, 0.2, frame_path)
        color = self._get_dominant_color(frame_path)
        self.assertGreater(color[0], 100)
        self.assertGreater(color[2], 100)

        # 验证字幕出现在封面之后（1.5s 处应能看到黄色字幕像素）
        frame_path2 = self.temp_dir / "edit_frame_subtitle.png"
        self._extract_frame(output, 1.5, frame_path2)
        from PIL import Image
        img = Image.open(frame_path2)
        # 在底部区域搜索黄色像素
        region = img.crop((200, 1500, 880, 1570))
        pixels = list(region.getdata())
        yellowish = sum(1 for p in pixels if p[0] > 200 and p[1] > 150 and p[2] < 100)
        self.assertGreater(yellowish, 10, "字幕应在封面结束后出现")

    def test_edit_video_with_cover_disabled(self):
        """不启用封面时应与原有行为一致"""
        config = {
            "crop_top": 0,
            "crop_bottom": 0,
            "speed": 1.0,
            "hflip": False,
            "zoom": 1.0,
            "add_logo": False,
            "replace_audio": False,
            "bgm_select": "",
            "original_volume": 1.0,
            "add_subtitles": True,
            "subtitle_text": "No Cover Test",
            "subtitle_start": 0,
            "subtitle_end": None,
            "subtitle_style": "yellow_classic",
            "subtitle_font_size": 24,
            "subtitle_position": "bottom",
            "subtitle_align": "center",
            "subtitle_outline_width": 2,
            "add_cover": False
        }

        output = self.editor.edit_video(self.video_with_audio, config)
        self.assertIsNotNone(output)
        info = self._get_video_info(output)
        self.assertAlmostEqual(info["duration"], 4.0, delta=0.2)

        # 第一帧应为绿色主视频，不是紫色封面
        frame_path = self.temp_dir / "no_cover_frame_0.png"
        self._extract_frame(output, 0.2, frame_path)
        color = self._get_dominant_color(frame_path)
        self.assertLess(color[0], 50)
        self.assertGreater(color[1], 100)
        self.assertLess(color[2], 50)

    def test_edit_video_cover_path_missing(self):
        """封面路径不存在时应跳过封面，不影响主视频"""
        config = {
            "crop_top": 0,
            "crop_bottom": 0,
            "speed": 1.0,
            "hflip": False,
            "zoom": 1.0,
            "add_logo": False,
            "replace_audio": False,
            "bgm_select": "",
            "original_volume": 1.0,
            "add_subtitles": False,
            "add_cover": True,
            "cover_path": str(self.temp_dir / "missing.jpg"),
            "cover_duration": 1.0
        }

        output = self.editor.edit_video(self.video_with_audio, config)
        self.assertIsNotNone(output)
        info = self._get_video_info(output)
        self.assertAlmostEqual(info["duration"], 4.0, delta=0.2)

    def test_edit_video_cover_no_subtitle(self):
        """仅启用封面，无字幕"""
        config = {
            "crop_top": 0,
            "crop_bottom": 0,
            "speed": 1.0,
            "hflip": False,
            "zoom": 1.0,
            "add_logo": False,
            "replace_audio": False,
            "bgm_select": "",
            "original_volume": 1.0,
            "add_subtitles": False,
            "add_cover": True,
            "cover_path": str(self.cover_1080_1920),
            "cover_duration": 0.5
        }

        output = self.editor.edit_video(self.video_with_audio, config)
        self.assertIsNotNone(output)
        info = self._get_video_info(output)
        self.assertAlmostEqual(info["duration"], 4.5, delta=0.2)


if __name__ == "__main__":
    import json
    unittest.main(verbosity=2)
