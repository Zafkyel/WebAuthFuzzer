import asyncio
import sys
import os
import time

# 自动对齐项目根目录路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_root)

from core.config_loader import config_loader
from core.collector import FOFACollector
from core.dispatcher import AssetDispatcher
from core.scanner import RecursiveScanner
from core.bypasser import Bypasser
from utils.request_client import request_client
from utils.output_manager import OutputManager
from utils.logger import logger


async def run_pipeline():
    conf = config_loader.load_config()
    fofa_conf = conf.get("fofa", {})

    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    logger.banner()

    # --- 交互界面 ---
    print("\n" + "═" * 55)
    print("      WebAuthFuzzer 7.0 | Advanced Controller")
    print("═" * 55)

    mode = input("[?] 模式 (1.域名 2.公司 3.语法, 默认1): ").strip() or "1"
    target = input("[?] 输入目标关键字: ").strip()

    size_input = input("[?] 采集数量 (默认50): ").strip()
    fetch_size = int(size_input) if size_input.isdigit() else 50

    print("\n[!] 选择扫描速率挡位:")
    print("  1. 极速 (并发100, 延迟0ms)")
    print("  2. 均衡 (并发40,  延迟100ms)")
    print("  3. 隐蔽 (并发10,  延迟500ms)")
    speed_choice = input("[?] 选择档位 (默认2): ").strip() or "2"

    # 速率参数映射
    speed_map = {"1": (100, 0), "2": (40, 0.1), "3": (10, 0.5)}
    concurrency, delay = speed_map.get(speed_choice, (40, 0.1))

    # 初始化网络客户端
    await request_client.init_session()
    request_client.base_delay = delay

    # 初始化输出管理器 (增加描述性文件名和唯一后缀)
    om = OutputManager(target)

    try:
        # --- 1. 资产采集 ---
        collector = FOFACollector(fofa_conf.get("email"), fofa_conf.get("key"))
        query = collector.build_query(mode, target)
        raw_assets = await collector.fetch(query, size=fetch_size)

        if not raw_assets:
            print(f"\n[!] 采集结束：未在外部接口发现关于 {target} 的数据。")
            return

        # --- 2. 资产分流 ---
        print(f"\n[*] 正在对搜集到的 {len(raw_assets)} 条原始资产执行存活分流...")
        dispatcher = AssetDispatcher(concurrency=concurrency)
        classified = await dispatcher.run(raw_assets)

        # 记录到文件名清晰的本地文件
        if classified["200"]:
            for asset in classified["200"]: om.save("1", asset)

        others = classified["3xx"] + classified["restricted"]
        if others:
            for asset in others: om.save("3", asset)

        print(f"  [+] 200 存活: {len(classified['200'])} | 3xx/受限: {len(others)}")

        # --- 3. 递归与 Fuzz 扫描 (带指纹去重逻辑) ---
        scan_list = classified.get("200", [])
        if not scan_list and raw_assets:
            logger.warning("[!] 未探测到 200 存活资产，开启『强制扫描模式』...")
            scan_list = raw_assets

        if scan_list:
            logger.info(f"[*] 启动高效 Fuzz 引擎 (已加载页面指纹对比，防止重复响应)...")
            scanner = RecursiveScanner(om, config_loader, concurrency=concurrency)
            # 引入 asyncio.wait_for 保护，防止演示时 Fuzz 陷入死循环跑不完
            try:
                await asyncio.wait_for(scanner.run(scan_list), timeout=900)  # 15分钟强制截断
            except asyncio.TimeoutError:
                logger.warning("\n[!] 扫描任务达到最大预设时间，执行强制总结...")

        # --- 4. Bypass 绕过 ---
        if classified["restricted"]:
            logger.info(f"[*] 针对受限资产尝试绕过...")
            bypasser = Bypasser(om, config_loader, concurrency=concurrency // 2)
            await bypasser.run(classified["restricted"])

    except Exception as e:
        logger.error(f"[-] 运行时发生非预期错误。")
        # print(f"DEBUG: {e}") # 需要排错时取消注释
    finally:
        # --- 5. 核心：强制总结 ---
        # 无论发生什么情况（正常结束、超时、报错），最后都生成脱敏报告
        print("\n" + "=" * 55)
        print("  任务状态汇总中...")
        om.generate_report(mode_name=f"Speed-Mode-{speed_choice}")
        await request_client.close()


if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        logger.warning("\n[!] 用户中断操作，正在强制保存并退出...")
        # 注意：这里由 finally 块处理最后的报告打印