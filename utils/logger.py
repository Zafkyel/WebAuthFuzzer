import os
import time
import json


class Logger:
    def __init__(self):
        self.result_dir = "data/results"
        self.run_id = time.strftime('%Y%m%d_%H%M%S')
        self.current_run_dir = os.path.join(self.result_dir, self.run_id)

        if not os.path.exists(self.current_run_dir):
            os.makedirs(self.current_run_dir)

        # 定义核心输出文件
        self.inventory_file = os.path.join(self.current_run_dir, "full_inventory.json")
        self.fingerprint_file = os.path.join(self.current_run_dir, "fingerprints.json")
        self.bypass_file = os.path.join(self.current_run_dir, "bypass_details.json")
        self.summary_file = os.path.join(self.current_run_dir, "summary_report.json")

    def log_inventory(self, classified_data):
        """记录所有状态码分类的资产"""
        with open(self.inventory_file, "w", encoding="utf-8") as f:
            json.dump(classified_data, f, ensure_ascii=False, indent=4)

    def log_fingerprints(self, recon_results):
        """记录 200 OK 目标的 Title 和 Server 指纹"""
        with open(self.fingerprint_file, "w", encoding="utf-8") as f:
            json.dump(recon_results, f, ensure_ascii=False, indent=4)

    def log_bypass_detail(self, url, payload, status, is_success):
        """记录每一条 Bypass 尝试（修复 detail 文件不生成的关键）"""
        entry = {
            "time": time.strftime('%H:%M:%S'),
            "url": url,
            "payload": payload,
            "status": status,
            "result": "SUCCESS" if is_success else "FAILED"
        }
        with open(self.bypass_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()  # 强制刷新缓冲区，确保实时写入

    def log_summary(self, summary_data):
        """保存最终的统计数据（修复 AttributeError: log_summary 的关键）"""
        with open(self.summary_file, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=4)
        print(f"\n[+] 扫描总结已保存至: {self.summary_file}")
        print(f"[+] 本次任务全部结果存放在: {self.current_run_dir}")


# 实例化对象，供其他模块 import
logger = Logger()