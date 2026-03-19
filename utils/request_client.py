import aiohttp
import asyncio
import random
from utils.logger import logger


class RequestClient:
    def __init__(self):
        self.session = None
        self.ua_pool = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        ]
        # 默认速率参数 (会被 main.py 修改)
        self.base_delay = 0
        self.backoff_time = 10

    async def init_session(self):
        if not self.session:
            # TCPConnector limit=0 表示不限制连接池大小，由外部 Semaphore 控制
            connector = aiohttp.TCPConnector(ssl=False, limit=0)
            self.session = aiohttp.ClientSession(connector=connector)

    async def fetch(self, url, method="GET", headers=None, allow_redirects=True, timeout=10, retry=1):
        if not self.session: await self.init_session()

        # 核心速率控制：强制请求间隔
        if self.base_delay > 0:
            await asyncio.sleep(self.base_delay)

        final_headers = {"User-Agent": random.choice(self.ua_pool), "Connection": "close"}
        if headers: final_headers.update(headers)

        try:
            async with self.session.request(
                    method, url, headers=final_headers,
                    allow_redirects=allow_redirects,
                    timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                if resp.status == 429:
                    logger.warning(f"[!] 触发 429 限制，静默 {self.backoff_time}s")
                    await asyncio.sleep(self.backoff_time)
                    if retry > 0: return await self.fetch(url, method, headers, allow_redirects, timeout, retry - 1)

                content = await resp.read()
                return resp, content.decode('utf-8', errors='ignore')
        except Exception:
            return None, ""

    async def close(self):
        if self.session: await self.session.close()


request_client = RequestClient()