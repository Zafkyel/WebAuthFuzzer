import asyncio
import aiohttp
import os
from utils.logger import logger


class Fuzzer:
    def __init__(self, payload_name="bypass_list.txt"):
        self.payload_dir = "data/payloads"
        self.payload_path = os.path.join(self.payload_dir, payload_name)
        self.payloads = []
        # --- 核心优化：信号量控制并发数量，建议设为 10-20 ---
        self.semaphore = asyncio.Semaphore(10)
        self._load_payloads()

    def _load_payloads(self):
        """加载 500+ 行字典"""
        if os.path.exists(self.payload_path):
            with open(self.payload_path, "r", encoding="utf-8") as f:
                self.payloads = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            print(f"[*] 成功加载字典，当前 Payload 规模: {len(self.payloads)}")
        else:
            print(f"[!] 警告: 字典文件不存在")

    async def _request(self, session, url, headers=None, payload=""):
        async with self.semaphore:
            try:
                # 调低超时到 5 秒，防止挂死
                async with session.get(url, headers=headers, timeout=5, ssl=False) as resp:
                    status = resp.status
                    is_success = (status == 200)

                    # 关键：调用 logger 记录
                    logger.log_bypass_detail(url, payload, status, is_success)

                    if is_success:
                        print(f"  [!!!] 成功绕过! URL: {url} | Payload: {payload}")
                    return status
            except Exception as e:
                # 可选：记录错误到日志，方便排查为什么没生成文件
                # logger.log_bypass_detail(url, payload, "Error", False)
                return None

    async def bypass_test(self, url):
        """执行 500 行 Payload 的全量测试"""
        async with aiohttp.ClientSession() as session:
            tasks = []
            for payload in self.payloads:
                # 逻辑 A：如果 Payload 是 Header 形式 (如 X-Forwarded-For: 127.0.0.1)
                if ":" in payload and not payload.startswith("/"):
                    key, value = payload.split(":", 1)
                    headers = {key.strip(): value.strip()}
                    tasks.append(self._request(session, url, headers=headers, payload=payload))

                # 逻辑 B：如果 Payload 是路径变形 (如 /admin/..;/)
                else:
                    # 确保路径拼接正确
                    target_url = url.rstrip('/') + (payload if payload.startswith('/') else '/' + payload)
                    tasks.append(self._request(session, target_url, payload=payload))

            # 并发执行
            await asyncio.gather(*tasks)