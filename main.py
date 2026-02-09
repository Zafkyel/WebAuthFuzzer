import asyncio
from core.recon import FofaScanner
from utils.request_client import AsyncReq


async def start_task(target_domain):
    print(f"[*] 启动任务: {target_domain}")

    # 1. 资产收集
    fofa = FofaScanner()
    assets = await fofa.search(f'domain="{target_domain}"')

    # 2. 存活探测与初筛
    req = AsyncReq()
    for host in assets:
        status, size = await req.get_status(host)
        if status == 403:
            print(f"[!] 发现 403 目标: {host} -> 触发未授权绕过策略")
            # 此处后续对接 dispatcher.py
        elif status == 200:
            print(f"[*] 发现 200 目标: {host} -> 触发 API 提取策略")


if __name__ == "__main__":
    asyncio.run(start_task("example.com"))