import asyncio
import sys
import os
from core.config_loader import ConfigLoader
from core.fofa_client import FofaClient
from core.dispatcher import Dispatcher
from core.fuzzer import Fuzzer
from utils.logger import logger


# 将当前目录加入路径，防止 ModuleNotFoundError
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


async def run_pipeline():
    print("""
    __      __ZWJ_    _         _         _      ______                           
    \ \    / / | |   / \       | |       | |    |  ____|                          
     \ \  / /__| |__/ _ \ _   _| |_ ___  | |__  | |__ _   _ _________  ___ _ __ 
      \ \/ / _ \ '_ \ / _ \ | | | __/ _ \ | '_ \ |  __| | | |_  /_  / / _ \ '__|
       \  /  __/ |_) / ___ \ |_| | || (_) || | | || |  | |_| |/ / / / |  __/ |   
        \/ \___|_.__/_/   \_\__,_|\__\___/ |_| |_||_|   \__,_/___/___(_)___|_|   
    """)
    print("--- WebAuthFuzzer 自动化测绘与绕过工具 v1.0 ---")

    # 1. 初始化配置加载器
    loader = ConfigLoader()
    email, key = loader.get_fofa_key()

    if not email or not key:
        print("[!] 错误: 无法获取 FOFA 凭据，请检查 config/config.yaml")
        return

    # 2. 获取用户输入
    target_domain = input("\n[?] 请输入要探测的目标域名 (如 example.com): ").strip()
    if not target_domain:
        print("[-] 目标不能为空")
        return

    # 3. 第一阶段：资产采集 (Recon)
    fofa = FofaClient(email, key)
    # 构造 FOFA 查询语句：搜索该域名相关的 host
    query = f'domain="{target_domain}"'
    print(f"[*] 正在检索 FOFA 资产，查询语句: {query}")

    raw_assets = await fofa.fetch_assets(query, size=50)
    if not raw_assets:
        print("[-] 未发现相关资产，程序退出。")
        return

    # 4. 第二阶段：资产分流 (Dispatcher)
    dispatcher = Dispatcher()
    print(f"[*] 正在对 {len(raw_assets)} 个原始资产进行状态码分类...")
    classified = await dispatcher.dispatch(raw_assets)

    if classified is None:
        classified = {"200": [], "403": [], "others": []}
    # 5. 第三阶段：自动化绕过测试 (Fuzzer)
    targets_403 = classified.get("403", [])

    if targets_403:
        print(f"\n[!] 发现 {len(targets_403)} 个 403 目标，准备启动 Bypass 引擎...")
        fuzzer = Fuzzer()

        # 并发执行所有 403 目标的绕过测试
        fuzz_tasks = [fuzzer.bypass_test(url) for url in targets_403]
        await asyncio.gather(*fuzz_tasks)
    else:
        print("\n[*] 本次扫描未发现 403 状态码的资产，无需执行 Bypass。")

    # 6. 扫描结束
    print("\n" + "=" * 50)
    print("[+] 扫描任务完成！")
    print(f"[+] 活跃资产 (200 OK): {len(classified.get('200', []))} 个")
    print(f"[+] 权限限制 (403 Forbidden): {len(targets_403)} 个")
    print("=" * 50)

    summary = {
        "target": target_domain,
        "total_assets": len(raw_assets),
        "200_ok": len(classified.get("200", [])),
        "403_forbidden": len(targets_403)
    }
    logger.log_summary(summary)

if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print("\n[-] 用户终止程序。")

