import asyncio
from core.config_loader import ConfigLoader
from core.fofa_client import FofaClient
from core.dispatcher import Dispatcher

async def main():
    loader = ConfigLoader()
    email, key = loader.get_fofa_key()
    if not email: return

    # 第一步：搜集资产
    fofa = FofaClient(email, key)
    target = input("请输入目标域名: ")
    assets = await fofa.fetch_assets(f'domain="{target}"', size=50)

    # 第二步：分流资产
    dispatcher = Dispatcher()
    classified_assets = await dispatcher.dispatch(assets)

    # 第三步：针对性处理 (下周我们要写的 Fuzzer)
    if classified_assets["403"]:
        print("\n[!] 发现 403 目标，准备进行 Bypass 测试:")
        for url in classified_assets["403"]:
            print(f"  -> {url}")
            # 这里将来调用 fuzzer.bypass(url)

if __name__ == "__main__":
    asyncio.run(main())