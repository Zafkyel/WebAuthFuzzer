import asyncio
from utils.logger import logger
from utils.request_client import request_client
from core.param_fuzzer import ParamFuzzer


class RecursiveScanner:
    def __init__(self, output_manager, config_loader, concurrency=30):
        self.om = output_manager
        self.loader = config_loader
        self.concurrency = concurrency
        self.max_depth = 2
        # 修复报错：初始化已访问集合
        self.visited = set()
        self.fuzzer = ParamFuzzer(concurrency=concurrency // 2)

    async def scan(self, url, depth, sem, dir_dict, param_dict):
        # 递归终止条件
        if depth > self.max_depth or url in self.visited:
            return
        self.visited.add(url)

        async with sem:
            logger.print_url(url)

            # 实时参数 Fuzz
            fuzz_hits = await self.fuzzer.fuzz_url(url, param_dict, sem)
            if fuzz_hits:
                self.om.save("fuzz", fuzz_hits)

            # 目录爆破
            for path in dir_dict:
                target = f"{url.rstrip('/')}/{path.lstrip('/')}"
                resp, _ = await request_client.fetch(target, allow_redirects=False)

                if resp:
                    if resp.status == 200:
                        self.om.save("recursive", target)
                        # 开启新协程递归，不阻塞当前循环
                        asyncio.create_task(self.scan(target, depth + 1, sem, dir_dict, param_dict))
                    elif resp.status in [301, 302, 403, 405]:
                        self.om.save("others", f"{target} [{resp.status}]")

    async def run(self, start_urls):
        dir_dict = self.loader.load_dict("actions.txt")
        param_dict = self.loader.load_dict("params.txt")
        if not dir_dict: return

        sem = asyncio.Semaphore(self.concurrency)
        tasks = [asyncio.create_task(self.scan(url, 1, sem, dir_dict, param_dict)) for url in start_urls]
        await asyncio.gather(*tasks)