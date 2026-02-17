import asyncio
import sys
import os

# 路径补丁：确保脚本在任何目录下运行都能找到核心模块
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入核心模块
from core.config_loader import ConfigLoader
from core.fofa_client import FofaClient
from core.dispatcher import Dispatcher  # 确保这里导入的是类
from core.fuzzer import Fuzzer
from core.recon import Recon
from utils.logger import logger  # 确保 logger.py 最后有 logger = Logger()


async def run_pipeline():
    # 打印 Banner
    print("""
    __      __ZWJ_    _         _         _      ______                           
    \ \    / / | |   / \       | |       | |    |  ____|                          
     \ \  / /__| |__/ _ \ _   _| |_ ___  | |__  | |__ _   _ _________  ___ _ __ 
      \ \/ / _ \ '_ \ / _ \ | | | __/ _ \ | '_ \ |  __| | | |_  /_  / / _ \ '__|
       \  /  __/ |_) / ___ \ |_| | || (_) || | | || |  | |_| |/ / / / |  __/ |   
        \/ \___|_.__/_/   \_\__,_|\__\___/ |_| |_||_|   \__,_/___/___(_)___|_|   
    """)
    print("--- WebAuthFuzzer 自动化测绘与绕过系统 v1.2 ---")

    # 1. 配置加载
    loader = ConfigLoader()
    email, key = loader.get_fofa_key()
    if not email or not key:
        print("[!] 错误: 无法获取 FOFA 凭据，请检查 config/config.yaml")
        return

    # 2. 交互式模式选择
    print("\n" + "=" * 30)
    print(" [模式选择]")
    print(" 1. 域名模式 (搜子域名资产)")
    print(" 2. 公司模式 (搜组织/备案资产)")
    print(" 3. 语法模式 (FOFA 原生语法)")
    print("=" * 30)

    mode = input("[?] 请选择模式 (1/2/3): ").strip()
    keyword = input("[?] 请输入搜索关键字: ").strip()

    # 构造查询语句
    if mode == "1":
        query = f'domain="{keyword}"'
    elif mode == "2":
        query = f'org="{keyword}" || icp="{keyword}"'
    elif mode == "3":
        query = keyword
    else:
        query = f'domain="{keyword}"'

    size = input("[?] 抓取资产数量? (默认 50): ").strip()
    size = int(size) if size.isdigit() else 50

    # 3. 第一阶段：FOFA 资产采集
    fofa = FofaClient(email, key)
    print(f"\n[*] 正在检索 FOFA 资产，查询语句: {query}")
    raw_assets = await fofa.fetch_assets(query, size=size)

    if not raw_assets:
        print("[-] 未发现相关资产，程序退出。")
        return

    # 4. 第二阶段：资产存活分流
    # 注意：这里必须先实例化类 Dispatcher()
    dispatcher_instance = Dispatcher()
    print(f"[*] 正在对 {len(raw_assets)} 个原始资产进行状态码分类...")
    classified = await dispatcher_instance.dispatch(raw_assets)

    if not classified:
        print("[-] 资产探测失败。")
        return

    # --- 核心改进：保存全量资产到 Result 目录 ---
    logger.log_inventory(classified)

    # 5. 第三阶段：分类处理

    # (A) 处理 200 OK 资产 - 提取指纹/标题
    targets_200 = classified.get("200", [])
    if targets_200:
        print(f"\n[*] 发现 {len(targets_200)} 个活跃资产，正在提取画像...")
        recon = Recon()
        recon_tasks = [recon.get_fingerprint(url) for url in targets_200]
        recon_results = await asyncio.gather(*recon_tasks)

        # 打印到屏幕
        for info in recon_results:
            print(f"  [+] {info['url']} | 标题: {info['title']} | 服务: {info['server']}")

        # --- 新增：保存指纹到文件 ---
        logger.log_fingerprints(recon_results)

    # (B) 处理 403 Forbidden 资产 - 绕过测试
    targets_403 = classified.get("403", [])
    if targets_403:
        print(f"\n[!] 发现 {len(targets_403)} 个权限受限资产")
        print("-" * 30)
        print(" 1. 默认执行 (data/payloads/bypass_list.txt)")
        print(" 2. 指定字典执行 (输入 data/payloads/ 下的文件名)")
        print("-" * 30)

        choice = input("[?] 请选择 (1/2): ").strip()

        # --- 核心修复点：初始化 p_name ---
        p_name = "bypass_list.txt"

        if choice == "2":
            input_name = input("[?] 请输入文件名 (例如 custom.txt): ").strip()
            if input_name:
                p_name = input_name

        # 传入确定的 p_name
        fuzzer = Fuzzer(payload_name=p_name)

        print(f"[*] 启动 Bypass 引擎，模式: {p_name}")
        tasks = [fuzzer.bypass_test(url) for url in targets_403]
        await asyncio.gather(*tasks)

    # 6. 任务总结
    print("\n" + "=" * 50)
    print(f"[+] 扫描任务完成！")
    print(f"[+] 活跃资产 (200): {len(targets_200)}")
    print(f"[+] 权限受限 (403): {len(targets_403)}")
    print(f"[+] 跳转/其他: {len(classified.get('301/302', [])) + len(classified.get('others', []))}")
    print("=" * 50)

    summary = {
        "target": keyword,
        "query": query,
        "results": {
            "total": len(raw_assets),
            "200": len(targets_200),
            "403": len(targets_403),
            "redirect": len(classified.get("301/302", []))
        }
    }
    logger.log_summary(summary)


if __name__ == "__main__":
    try:
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        print("\n[-] 用户手动终止扫描。")
    except Exception as e:
        print(f"\n[!] 系统运行异常: {e}")