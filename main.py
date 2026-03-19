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

    # 清屏 (可选，让界面更干净)
    os.system('cls' if os.name == 'nt' else 'clear')
    # 打印新 Banner
    logger.banner()

    # --- 交互界面 ---
    print("\n" + "═" * 50)
    print("      WebAuthFuzzer 7.0 | Advanced Controller")
    print("═" * 50)

    mode = input("[?] 模式 (1.域名 2.公司 3.语法, 默认1): ").strip() or "1"
    target = input("[?] 输入目标关键字: ").strip()

    # 修复：确保数量可选且生效
    size_input = input("[?] 采集数量 (默认50): ").strip()
    fetch_size = int(size_input) if size_input.isdigit() else 50

    print("\n[!] 选择扫描速率挡位:")
    print("  1. 极速 (并发100, 延迟0ms)")
    print("  2. 均衡 (并发40,  延迟100ms)")
    print("  3. 隐蔽 (并发10,  延迟500ms)")
    speed_choice = input("[?] 选择档位 (默认2): ").strip() or "2"

    # 速率参数映射
    speed_map = {
        "1": (100, 0),
        "2": (40, 0.1),
        "3": (10, 0.5)
    }
    concurrency, delay = speed_map.get(speed_choice, (40, 0.1))

    # 初始化组件
    await request_client.init_session()
    request_client.base_delay = delay  # 注入延迟
    om = OutputManager(target)

    try:
        # --- 1. 资产采集 ---
        collector = FOFACollector(fofa_conf.get("email"), fofa_conf.get("key"))
        query = collector.build_query(mode, target)
        # 关键修复：显式传递 fetch_size
        raw_assets = await collector.fetch(query, size=fetch_size)

        if not raw_assets:
            logger.warning("未搜集到数据。")
            return

        # --- 2. 资产分流 ---
        dispatcher = AssetDispatcher(concurrency=concurrency)
        classified = await dispatcher.run(raw_assets)

        om.save("alive", classified["200"])
        om.save("others", classified["3xx"] + classified["restricted"])

        # --- 3. 递归扫描 (含 visited 修复) ---
        if classified["200"]:
            logger.info(f"[*] 启动递归探测 (并发:{concurrency})...")
            scanner = RecursiveScanner(om, config_loader, concurrency=concurrency)
            await scanner.run(classified["200"])

        # --- 4. Bypass 绕过 ---
        if classified["restricted"]:
            bypasser = Bypasser(om, config_loader, concurrency=concurrency // 2)
            await bypasser.run(classified["restricted"])

        logger.success(f"任务结束！结果路径: {om.output_path}")

        # --- 5. 生成总结报告 (Report 增强版) ---
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        report_name = f"Report_{target}_{om.timestamp}.txt"
        report_path = os.path.join(config_loader.base_path, "reports", report_name)
        os.makedirs(os.path.dirname(report_path), exist_ok=True)

        # 统计各文件行数
        stats = {}
        for key, filename in om.file_map.items():
            f_path = os.path.join(om.output_path, filename)
            if os.path.exists(f_path):
                with open(f_path, 'r') as f:
                    stats[key] = len(f.readlines())
            else:
                stats[key] = 0

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"╔{'═' * 50}╗\n")
            f.write(f"║ WebAuthFuzzer 自动化扫描报告 {' ' * (50 - 26)}║\n")
            f.write(f"╠{'═' * 50}╣\n")
            f.write(f"║ 目标关键字: {target:<37}║\n")
            f.write(f"║ 扫描时间: {timestamp:<39}║\n")
            f.write(f"║ 速率模式: {speed_choice} (并发:{concurrency} 延迟:{delay}s){' ' * (15)}║\n")
            f.write(f"╠{'═' * 50}╣\n")
            f.write(f"║ [1] 初始存活资产: {stats.get('alive', 0):<30}║\n")
            f.write(f"║ [2] 递归发现目录: {stats.get('recursive', 0):<30}║\n")
            f.write(f"║ [3] 3xx/4xx 资产: {stats.get('others', 0):<31}║\n")
            f.write(f"║ [4] Fuzz 成功参数: {stats.get('fuzz', 0):<30}║\n")
            f.write(f"║ [5] Bypass 成功数: {stats.get('bypass', 0):<30}║\n")
            f.write(f"╚{'═' * 50}╝\n")
            f.write(f"\n[!] 结果详情请访问: {om.output_path}\n")

        logger.success(f"任务圆满完成！报告已归档: {report_path}")

    except Exception as e:
        logger.error(f"运行时发生错误: {e}")
    finally:
        await request_client.close()


if __name__ == "__main__":
    try:
        # 针对不同系统的事件循环策略
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(run_pipeline())
    except KeyboardInterrupt:
        logger.warning("\n[!] 用户中断操作，正在强制退出...")
    except Exception as e:
        logger.error(f"程序启动失败: {e}")