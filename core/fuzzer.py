import asyncio
import aiohttp
import os
from tqdm import tqdm
from utils.logger import logger


class Fuzzer:
    def __init__(self, payload_name="bypass_list.txt"):
        self.payload_dir = "data/payloads"
        self.payload_path = os.path.join(self.payload_dir, payload_name)
        self.payloads = []
        self.semaphore = asyncio.Semaphore(15)
        self.success_count = 0  # 核心：新增计数器
        self._load_payloads()

    def _load_payloads(self):
        if os.path.exists(self.payload_path):
            with open(self.payload_path, "r", encoding="utf-8") as f:
                self.payloads = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        else:
            self.payloads = ["X-Forwarded-For: 127.0.0.1"]

    async def _request(self, session, url, headers=None, payload=""):
        async with self.semaphore:
            try:
                # 显式添加随机 User-Agent 提高成功率
                base_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                if headers: base_headers.update(headers)

                async with session.get(url, headers=base_headers, timeout=5, ssl=False) as resp:
                    status = resp.status
                    is_success = (status == 200)
                    if is_success:
                        self.success_count += 1  # 统计成功数

                    # 确保写入 detail 文件
                    logger.log_bypass_detail(url, payload, status, is_success)
                    return is_success, status, payload
            except Exception:
                return False, None, payload

    async def bypass_test(self, url):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for payload in self.payloads:
                if ":" in payload and not payload.startswith("/"):
                    key, val = payload.split(":", 1)
                    tasks.append(self._request(session, url, headers={key.strip(): val.strip()}, payload=payload))
                else:
                    target_url = url.rstrip('/') + (payload if payload.startswith('/') else '/' + payload)
                    tasks.append(self._request(session, target_url, payload=payload))

            # PyCharm 稳健版进度条
            with tqdm(
                    total=len(tasks),
                    unit="req",
                    desc=f"[*] Fuzzing: {url[:20]}",
                    ncols=80,
                    mininterval=1.0,  # 降低刷新频率，防止跳行
                    ascii=".#",  # 纯字符样式最稳
                    leave=False
            ) as pbar:
                for f in asyncio.as_completed(tasks):
                    is_success, status, payload = await f
                    if is_success:
                        tqdm.write(f"  [!!!] BYPASS SUCCESS: {url} | {payload}")
                    pbar.update(1)

            return self.success_count  # 返回给 main.py