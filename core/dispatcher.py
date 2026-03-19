import asyncio
from utils.logger import logger
from utils.request_client import request_client


class AssetDispatcher:
    """
    三路分流模块 (核心功能 1)
    功能：判定存活，并将 200, 3xx, 403 分流隔离
    """

    def __init__(self, concurrency=50):
        self.concurrency = concurrency
        self.results = {
            "200": [],  # 存活
            "3xx": [],  # 跳转
            "restricted": [],  # 403/405
            "dead": []  # 无法访问
        }

    async def probe(self, url, sem):
        async with sem:
            # allow_redirects=False 极其重要，否则抓不到原始 3xx
            resp, _ = await request_client.fetch(url, timeout=10, allow_redirects=False)

            if not resp:
                self.results["dead"].append(url)
                return

            status = resp.status
            if status == 200:
                self.results["200"].append(url)
                logger.success(f"[200 OK] {url}")
            elif 300 <= status < 400:
                loc = resp.headers.get("Location", "Unknown")
                self.results["3xx"].append(f"{url} -> {loc}")
                logger.info(f"[3xx RED] {url}")
            elif status in [403, 405]:
                self.results["restricted"].append(url)
                logger.warning(f"[403/405] {url}")
            else:
                self.results["dead"].append(url)

    async def run(self, url_list):
        if not url_list: return self.results

        logger.info(f"开始存活探测，资产总数: {len(url_list)}")
        sem = asyncio.Semaphore(self.concurrency)
        tasks = [asyncio.create_task(self.probe(url, sem)) for url in url_list]
        await asyncio.gather(*tasks)

        return self.results