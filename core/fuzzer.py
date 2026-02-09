import asyncio
from utils.request_client import RequestClient
from utils.logger import logger


class Fuzzer:
    def __init__(self):
        self.client = RequestClient()
        # 核心绕过 Header 列表
        self.bypass_headers = [
            {"X-Forwarded-For": "127.0.0.1"},
            {"X-Originating-IP": "127.0.0.1"},
            {"X-Remote-IP": "127.0.0.1"},
            {"X-Remote-Addr": "127.0.0.1"},
            {"X-Client-IP": "127.0.0.1"},
            {"X-Real-IP": "127.0.0.1"},
            {"X-Custom-IP-Authorization": "127.0.0.1"},
            {"X-Original-URL": "/"},
            {"X-Rewrite-URL": "/"}
        ]
        # 核心绕过路径变形
        self.bypass_paths = [
            "/%2e/", "/./", "/..;/", "/index.php/..;/", "/;/"
        ]

    async def bypass_test(self, url: str):
        print(f"\n[*] 正在对 {url} 执行绕过测试...")

        # --- 1. 必须先定义这个列表，否则下面 append 会报错 ---
        tasks = []

        # --- 2. 构造 Headers 绕过任务 ---
        for header in self.bypass_headers:
            # 将每个探测请求作为一个任务加入列表
            tasks.append(self.client.check_status(url, custom_headers=header))

        # --- 3. 构造路径变形绕过任务 ---
        base_url = url.rstrip('/')
        for path in self.bypass_paths:
            test_url = base_url + path
            tasks.append(self.client.check_status(test_url))

        # --- 4. 统一执行并等待结果 ---
        # *tasks 的意思是把列表里的任务“拆开”作为参数传进去
        results = await asyncio.gather(*tasks)

        # --- 5. 处理结果 (接之前的分析逻辑) ---
        found_any = False
        for res in results:
            if not res: continue
            # ... 记录 log_result 的代码 ...