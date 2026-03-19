import asyncio
from utils.request_client import request_client
from utils.logger import logger


class ParamFuzzer:
    def __init__(self, concurrency=20):
        self.concurrency = concurrency

    async def fuzz_url(self, url, param_list, sem):
        """
        对传入的 URL 进行参数差异化探测
        """
        if not param_list: return []

        # 1. 获取原始页面的基准长度
        base_resp, base_html = await request_client.fetch(url, timeout=5)
        if not base_resp: return []
        base_len = len(base_html)

        hits = []

        async def check_param(param):
            async with sem:  # 使用全局信号量控制速率
                conn = "&" if "?" in url else "?"
                test_url = f"{url}{conn}{param}=1337"
                resp, html = await request_client.fetch(test_url, timeout=5)

                if resp and resp.status == 200:
                    # 如果加入参数后，页面长度变化超过 15 字节，判定为有效参数
                    if abs(len(html) - base_len) > 15:
                        logger.success(f"[Param Found] {test_url}")
                        hits.append(test_url)

        # 这里的并发由 Scanner 传进来的 sem 统一控制
        tasks = [asyncio.create_task(check_param(p)) for p in param_list]
        await asyncio.gather(*tasks)
        return hits