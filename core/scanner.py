import asyncio
import aiohttp
import hashlib
import os
import random
from utils.logger import logger


class RecursiveScanner:
    def __init__(self, output_manager, config_loader, concurrency=20):
        self.om = output_manager
        self.semaphore = asyncio.Semaphore(concurrency)
        self.visited_urls = set()  # URL 去重
        self.content_hashes = set()  # 内容去重 (核心：防止重复页面递归)
        self.not_found_hashes = {}

        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.payload_path = os.path.join(base_path, "data", "payloads")
        self.wordlist = self._load_dicts()

    def _load_dicts(self):
        combined = []
        if not os.path.exists(self.payload_path): return []
        # 建议字典按优先级排序，演示时先加载 actions.txt
        for f_name in ["actions.txt", "params.txt", "bypass.txt"]:
            p = os.path.join(self.payload_path, f_name)
            if os.path.exists(p):
                with open(p, "r", encoding="utf-8") as f:
                    combined.extend([l.strip() for l in f if l.strip()])
        return list(set(combined))

    def get_content_fingerprint(self, text):
        """提取页面结构指纹 (忽略动态内容)"""
        # 只取前1000个字符并去除空白，计算 MD5
        clean_text = "".join(text[:1000].split())
        return hashlib.md5(clean_text.encode()).hexdigest()

    async def fetch(self, session, base_url, path, depth):
        # 1. 基础 URL 过滤
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
        if url in self.visited_urls: return
        self.visited_urls.add(url)

        # 2. 后缀过滤 (防止扫出 200 OK 的图片导致递归)
        if any(url.lower().endswith(ext) for ext in ['.jpg', '.png', '.css', '.js', '.wof']): return

        async with self.semaphore:
            try:
                async with session.get(url, timeout=5, ssl=False, allow_redirects=False) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        fingerprint = self.get_content_fingerprint(text)

                        # 3. 核心去重：如果页面指纹已存在，说明是重复内容（如统一报错页），不再处理
                        if fingerprint in self.content_hashes or fingerprint == self.not_found_hashes.get(base_url):
                            return

                        self.content_hashes.add(fingerprint)
                        print(f"  [+] 发现新页面: {url}")
                        self.om.save("2", url)
                        self.om.save("4", url)

                        # 4. 限制递归：只有发现真正的新目录才递归，且深度严格限制为 1
                        if depth < 1 and "/" not in path and "." not in path:
                            await self.scan_layer(session, url, depth + 1)

                    elif resp.status in [301, 302]:
                        self.om.save("3", f"{url} -> {resp.headers.get('Location')}")
            except:
                pass

    async def scan_layer(self, session, url, depth):
        # 限制单页面下的 Fuzz 数量，防止爆炸
        tasks = [self.fetch(session, url, w, depth) for w in self.wordlist[:1000]]
        await asyncio.gather(*tasks)

    async def scan_target(self, url):
        self.om.save("1", url)
        try:
            async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
                # 获取该站点的 404 指纹
                t_url = f"{url.rstrip('/')}/non_existent_{random.randint(100, 999)}"
                async with session.get(t_url, timeout=5) as r:
                    self.not_found_hashes[url] = self.get_content_fingerprint(await r.text())
                await self.scan_layer(session, url, 0)
        except:
            pass

    async def run(self, url_list):
        if not self.wordlist: return
        # 限制总目标数，毕设建议一次跑 5-10 个最有价值的
        targets = url_list[:10]
        print(f"\n[*] 启动高效探测模式 | 目标量: {len(targets)} | 字典量: {len(self.wordlist)}")
        for i in range(0, len(targets), 2):  # 降低每组并发的目标数，提高单站速度
            await asyncio.gather(*[self.scan_target(u) for u in targets[i:i + 2]])