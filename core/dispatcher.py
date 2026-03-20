import asyncio
import aiohttp
from utils.logger import logger


class AssetDispatcher:
    def __init__(self, concurrency=40):
        self.concurrency = concurrency
        self.semaphore = asyncio.Semaphore(concurrency)

    async def check_url(self, session, url):
        """探测单个 URL 的存活状态并分类"""
        async with self.semaphore:
            try:
                # 允许重定向，超时设为 5 秒防止卡死
                async with session.get(url, timeout=5, ssl=False, allow_redirects=True) as resp:
                    status = resp.status
                    if status == 200:
                        return "200", url
                    elif status in [401, 403]:
                        return "restricted", url
                    elif str(status).startswith("3"):
                        return "3xx", url
                    return "others", url
            except Exception:
                # 访问失败的资产归为 others
                return "others", url

    async def run(self, url_list):
        logger.info(f"[*] 正在对 {len(url_list)} 个目标进行并发存活探测...")

        results = {
            "200": [],
            "restricted": [],
            "3xx": [],
            "others": []
        }

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            tasks = [self.check_url(session, url) for url in url_list]
            # 并发执行所有探测任务
            responses = await asyncio.gather(*tasks)

            for category, url in responses:
                if category in results:
                    results[category].append(url)

        logger.info(f"[+] 探测完成: 200({len(results['200'])}), 限制级({len(results['restricted'])})")
        return results