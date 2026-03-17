"""
抖音视频下载器 v4.0 - API 拦截方案
通过拦截网页 API 请求获取真实视频地址
"""
import re
import json
import asyncio
from pathlib import Path
from urllib.parse import unquote
from playwright.async_api import async_playwright

CHROME_PATH = "/usr/bin/google-chrome"


class DouyinAPIDownloader:
    """通过拦截 API 请求下载抖音视频"""

    def __init__(self, raw_dir="videos/raw", headless=True):
        self.raw_dir = Path(raw_dir)
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.api_responses = {}  # 存储 API 响应

    def extract_video_id(self, url):
        """提取视频 ID"""
        patterns = [
            r'/video/(\d+)',
            r'/share/video/(\d+)',
            r'modal_id=(\d+)',
            r'/note/(\d+)',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        if 'v.douyin.com' in url or 'iesdouyin.com' in url:
            return None
        return None

    async def download(self, url, filename=None):
        """下载视频"""
        import requests
        
        # 处理短链接
        final_url = url
        video_id = self.extract_video_id(url)
        
        if not video_id and ('v.douyin.com' in url or 'iesdouyin.com' in url):
            print(f"🔗 解析短链接...")
            try:
                resp = requests.get(url, headers={
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"
                }, allow_redirects=True, timeout=10)
                final_url = resp.url
                video_id = self.extract_video_id(final_url)
                print(f"📍 真实链接: {final_url}")
            except Exception as e:
                print(f"⚠️ 短链接解析失败: {e}")
        
        if not video_id:
            return {"status": "error", "error": "无法解析视频 ID"}
        
        if not filename:
            filename = f"douyin_{video_id}.mp4"
        
        output_path = self.raw_dir / filename
        
        print(f"🚀 开始下载抖音视频: {video_id}")
        self.api_responses = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                executable_path=CHROME_PATH,
                headless=self.headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-blink-features=AutomationControlled',
                ]
            )

            context = await browser.new_context(
                user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15',
                viewport={'width': 390, 'height': 844},  # iPhone 尺寸
                device_scale_factor=3,
            )

            # 反检测
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                window.chrome = { runtime: {} };
            """)

            page = await context.new_page()

            # 拦截 API 响应
            async def handle_route(route, request):
                url = request.url
                
                # 拦截详情 API
                if '/aweme/v1/web/aweme/detail/' in url:
                    print(f"🔍 拦截到详情 API")
                    try:
                        response = await route.fetch()
                        body = await response.text()
                        self.api_responses['detail'] = json.loads(body)
                        await route.fulfill(response=response, body=body)
                        return
                    except Exception as e:
                        print(f"   API 拦截失败: {e}")
                
                # 拦截视频请求
                if any(ext in url.lower() for ext in ['.mp4', '.mov']) and 'douyin' in url:
                    print(f"🎯 发现视频: {url[:60]}...")
                
                await route.continue_()

            await page.route("**/*", handle_route)

            try:
                print("⏳ 加载页面...")
                # 使用移动端域名
                mobile_url = f"https://m.douyin.com/video/{video_id}"
                await page.goto(mobile_url, wait_until="networkidle", timeout=45000)
                
                await asyncio.sleep(3)
                
                # 点击播放
                print("▶️  点击播放...")
                try:
                    await page.click('video, .video-container, [class*="player"]', timeout=5000)
                    await asyncio.sleep(3)
                except:
                    pass
                
                # 从页面中提取数据
                print("🔍 提取页面数据...")
                page_data = await page.evaluate("""() => {
                    // 尝试获取 SSR 数据
                    const renderData = document.querySelector('#RENDER_DATA');
                    if (renderData) {
                        return { type: 'render_data', content: renderData.textContent };
                    }
                    
                    // 尝试获取全局变量
                    if (window._SSR_HYDRATED_DATA) {
                        return { type: 'ssr_data', content: JSON.stringify(window._SSR_HYDRATED_DATA) };
                    }
                    
                    return { type: 'none' };
                }""")
                
                if page_data.get('type') == 'render_data':
                    try:
                        import urllib.parse
                        decoded = urllib.parse.unquote(page_data['content'])
                        self.api_responses['page_data'] = json.loads(decoded)
                        print("✅ 获取到页面 RENDER_DATA")
                    except Exception as e:
                        print(f"   解析 RENDER_DATA 失败: {e}")
                
                elif page_data.get('type') == 'ssr_data':
                    try:
                        self.api_responses['page_data'] = json.loads(page_data['content'])
                        print("✅ 获取到 SSR_HYDRATED_DATA")
                    except Exception as e:
                        print(f"   解析 SSR 数据失败: {e}")
                
            except Exception as e:
                print(f"⚠️ 页面加载问题: {e}")
            
            await browser.close()

        # 解析视频地址
        video_urls = self._extract_video_urls()
        
        if not video_urls:
            print("❌ 未找到视频地址")
            print(f"   API 响应: {list(self.api_responses.keys())}")
            return {"status": "error", "error": "未找到视频地址"}
        
        print(f"📊 找到 {len(video_urls)} 个视频地址")
        for i, url_info in enumerate(video_urls[:3]):
            size_str = f"{url_info['size']/1024/1024:.1f}MB" if url_info.get('size') else "未知"
            print(f"   #{i+1}: {url_info['quality']} | {size_str}")
        
        # 选择最佳视频
        best_video = self._select_best_video(video_urls)
        video_url = best_video['url']
        
        print(f"\n📥 开始下载: {best_video['quality']}")
        
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)",
                "Accept": "*/*",
                "Accept-Language": "zh-CN,zh;q=0.9",
                "Referer": "https://m.douyin.com/",
            }
            
            resp = requests.get(video_url, headers=headers, stream=True, timeout=120)
            resp.raise_for_status()
            
            total_size = int(resp.headers.get('content-length', 0))
            if total_size > 0:
                print(f"📦 文件大小: {total_size / 1024 / 1024:.2f} MB")
            
            with open(output_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            file_size = output_path.stat().st_size / 1024 / 1024
            
            # 获取视频信息
            video_info = self._get_video_info()
            
            print(f"✅ 下载完成: {output_path} ({file_size:.2f} MB)")
            
            return {
                "status": "success",
                "video_id": video_id,
                "url": url,
                "video_url": video_url,
                "output_path": str(output_path),
                "size_mb": file_size,
                "platform": "douyin",
                **video_info
            }
            
        except Exception as e:
            print(f"❌ 下载失败: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_video_urls(self):
        """从 API 响应中提取视频 URL"""
        urls = []
        
        # 从 detail API 提取
        if 'detail' in self.api_responses:
            data = self.api_responses['detail']
            urls.extend(self._parse_aweme_detail(data))
        
        # 从页面数据提取
        if 'page_data' in self.api_responses:
            data = self.api_responses['page_data']
            urls.extend(self._parse_aweme_detail(data))
        
        return urls

    def _parse_aweme_detail(self, data):
        """解析作品详情数据"""
        urls = []
        
        try:
            # 获取作品详情
            aweme = data.get('aweme_detail', {})
            if not aweme:
                # 尝试其他路径
                for key in ['app', 'aweme', 'videoInfo', 'video']:
                    if key in data:
                        subdata = data[key]
                        if isinstance(subdata, dict):
                            if 'aweme_detail' in subdata:
                                aweme = subdata['aweme_detail']
                                break
                            elif 'video' in subdata:
                                aweme = subdata
                                break
            
            if not aweme:
                return urls
            
            video_info = aweme.get('video', {})
            
            # 播放地址
            play_addr = video_info.get('play_addr', {})
            if play_addr:
                url_list = play_addr.get('url_list', [])
                for url in url_list:
                    if url and url not in [u['url'] for u in urls]:
                        urls.append({
                            'url': url,
                            'quality': 'normal',
                            'type': 'play'
                        })
            
            # 高清地址
            if 'bit_rate' in video_info:
                for bit in video_info['bit_rate']:
                    play_addr = bit.get('play_addr', {})
                    url_list = play_addr.get('url_list', [])
                    for url in url_list:
                        if url and url not in [u['url'] for u in urls]:
                            urls.append({
                                'url': url,
                                'quality': f"{bit.get('gear', 'hd')}",
                                'type': 'hd',
                                'size': bit.get('data_size', 0)
                            })
            
            # 下载地址（无水印）
            download_addr = video_info.get('download_addr', {})
            if download_addr:
                url_list = download_addr.get('url_list', [])
                for url in url_list:
                    if url and url not in [u['url'] for u in urls]:
                        urls.append({
                            'url': url,
                            'quality': 'download',
                            'type': 'download'
                        })
                        
        except Exception as e:
            print(f"解析视频详情失败: {e}")
        
        return urls

    def _select_best_video(self, urls):
        """选择最佳视频"""
        if not urls:
            return None
        
        # 优先选择有大小信息的
        with_size = [u for u in urls if u.get('size', 0) > 0]
        if with_size:
            # 按大小排序
            with_size.sort(key=lambda x: x.get('size', 0), reverse=True)
            return with_size[0]
        
        # 优先选择 download 类型（通常无水印）
        downloads = [u for u in urls if u.get('type') == 'download']
        if downloads:
            return downloads[0]
        
        # 优先选择 hd 类型
        hd_videos = [u for u in urls if 'hd' in u.get('quality', '')]
        if hd_videos:
            return hd_videos[0]
        
        return urls[0]

    def _get_video_info(self):
        """获取视频信息"""
        info = {}
        
        try:
            data = self.api_responses.get('detail') or self.api_responses.get('page_data', {})
            aweme = data.get('aweme_detail', {})
            
            info['desc'] = aweme.get('desc', '')
            info['author'] = aweme.get('author', {}).get('nickname', '')
            info['create_time'] = aweme.get('create_time', '')
            
        except:
            pass
        
        return info


async def download_douyin_video(url, output_dir="videos/raw", headless=True):
    """便捷函数"""
    dl = DouyinAPIDownloader(output_dir, headless)
    return await dl.download(url)


if __name__ == "__main__":
    import sys
    import os

    has_display = os.environ.get('DISPLAY') is not None
    headless = not has_display

    if len(sys.argv) > 1:
        url = sys.argv[1]
        result = asyncio.run(download_douyin_video(url, headless=headless))
        print("\n" + "="*50)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print("Usage: python douyin_api_downloader.py <douyin_url>")
